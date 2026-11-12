
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from metrics import REGISTRY, HttpMetricsMiddleware

app = FastAPI(
    title="ROTA LIVRE API",
    description="API de mobilidade e acessibilidade urbana.",
    version="1.0.0"
)
app.add_middleware(HttpMetricsMiddleware)


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def home():
    return {
        "projeto": "ROTA LIVRE",
        "mensagem": "API funcionando com sucesso!"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "rota-livre-api"
    }


@app.get("/api/obstacles")
def listar_obstaculos():
    return {
        "total": 2,
        "obstaculos": [
            {
                "id": 1,
                "tipo": "Calçada danificada",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "status": "Pendente"
            },
            {
                "id": 2,
                "tipo": "Rampa bloqueada",
                "latitude": -23.5510,
                "longitude": -46.6340,
                "status": "Em análise"
            }
        ]
    }
