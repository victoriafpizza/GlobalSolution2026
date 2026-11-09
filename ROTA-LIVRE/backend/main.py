
from fastapi import FastAPI

app = FastAPI(
    title="ROTA LIVRE API",
    description="API de mobilidade e acessibilidade urbana.",
    version="1.0.0"
)


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
