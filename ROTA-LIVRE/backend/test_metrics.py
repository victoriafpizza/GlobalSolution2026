import tempfile
import unittest
from pathlib import Path

from metrics import REGISTRY, ContainerMemoryCollector, HttpMetricsMiddleware


class HttpMetricsTests(unittest.IsolatedAsyncioTestCase):
    async def test_unmatched_paths_and_custom_methods_use_bounded_labels(self):
        async def respond(scope, receive, send):
            await send({"type": "http.response.start", "status": 404})

        async def send(message):
            pass

        labels = {"method": "OTHER", "route": "unmatched", "status_class": "4xx"}
        before = REGISTRY.get_sample_value("rota_livre_http_requests_total", labels) or 0
        await HttpMetricsMiddleware(respond)(
            {"type": "http", "path": "/unregistered/123", "method": "CUSTOM"}, None, send
        )
        after = REGISTRY.get_sample_value("rota_livre_http_requests_total", labels)
        self.assertEqual(after, before + 1)

    async def test_unhandled_exception_is_counted_and_propagated(self):
        async def fail(scope, receive, send):
            raise RuntimeError("test failure")

        labels = {"method": "GET", "route": "unmatched", "status_class": "5xx"}
        before = REGISTRY.get_sample_value("rota_livre_http_requests_total", labels) or 0
        with self.assertRaises(RuntimeError):
            await HttpMetricsMiddleware(fail)(
                {"type": "http", "path": "/unregistered", "method": "GET"}, None, None
            )
        after = REGISTRY.get_sample_value("rota_livre_http_requests_total", labels)
        self.assertEqual(after, before + 1)


class ContainerMemoryTests(unittest.TestCase):
    def test_reports_fraction_only_with_finite_cgroup_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            cgroup = Path(directory)
            (cgroup / "memory.current").write_text("64\n")
            (cgroup / "memory.max").write_text("256\n")
            collector = ContainerMemoryCollector(cgroup)
            self.assertEqual(next(collector.collect()).samples[0].value, 0.25)

            (cgroup / "memory.max").write_text("max\n")
            self.assertEqual(list(collector.collect()), [])


if __name__ == "__main__":
    unittest.main()
