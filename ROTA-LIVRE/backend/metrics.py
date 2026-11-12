from pathlib import Path
from time import perf_counter

from prometheus_client import CollectorRegistry, Counter, Histogram
from prometheus_client.core import GaugeMetricFamily
from starlette.types import ASGIApp, Message, Receive, Scope, Send


REGISTRY = CollectorRegistry()
HTTP_REQUESTS = Counter(
    "rota_livre_http_requests_total",
    "Respostas HTTP da API por metodo, rota e classe de status.",
    ("method", "route", "status_class"),
    registry=REGISTRY,
)
HTTP_DURATION = Histogram(
    "rota_livre_http_request_duration_seconds",
    "Duracao das requisicoes HTTP da API em segundos.",
    ("method", "route"),
    buckets=(0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
    registry=REGISTRY,
)
HTTP_METHODS = frozenset({"GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT"})
for public_route in ("/", "/api/obstacles"):
    HTTP_REQUESTS.labels("GET", public_route, "5xx")


class ContainerMemoryCollector:
    def __init__(self, cgroup: Path):
        self.cgroup = cgroup

    def collect(self):
        try:
            usage = int((self.cgroup / "memory.current").read_text())
            limit = int((self.cgroup / "memory.max").read_text())
        except (OSError, ValueError):
            # Cgroup v2 is unavailable or the container has no finite limit.
            return
        if limit > 0:
            yield GaugeMetricFamily(
                "rota_livre_container_memory_usage_ratio",
                "Memoria utilizada pelo container da API como fracao do limite cgroup v2.",
                value=usage / limit,
            )


REGISTRY.register(ContainerMemoryCollector(Path("/sys/fs/cgroup")))


class HttpMetricsMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http" or scope["path"] in {"/health", "/metrics"}:
            await self.app(scope, receive, send)
            return

        started = perf_counter()
        status_code = None

        async def track_status(message: Message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, track_status)
        except Exception:
            if status_code is None:
                status_code = 500
            raise
        finally:
            if status_code is not None:
                method = scope["method"] if scope["method"] in HTTP_METHODS else "OTHER"
                # Only configured route templates become labels. Unknown paths share a label.
                route = getattr(scope.get("route"), "path", "unmatched")
                HTTP_REQUESTS.labels(method, route, f"{status_code // 100}xx").inc()
                HTTP_DURATION.labels(method, route).observe(perf_counter() - started)
