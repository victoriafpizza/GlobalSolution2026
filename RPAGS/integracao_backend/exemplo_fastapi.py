"""Aplicação de exemplo e roteador reutilizável para o backend."""

from fastapi import APIRouter, FastAPI, HTTPException

from config import PASTA_SAIDA
from src.integracao import RelatorioIndisponivel, ler_ultimo_relatorio


def criar_roteador(pasta=PASTA_SAIDA):
    router = APIRouter(prefix="/rpa", tags=["RPA"])

    def carregar():
        try:
            return ler_ultimo_relatorio(pasta)
        except RelatorioIndisponivel as erro:
            raise HTTPException(
                status_code=404 if erro.ausente else 503, detail=str(erro),
            ) from None

    @router.get("/obstaculos-processados")
    def obstaculos_processados():
        return carregar()

    @router.get("/resumo")
    def resumo():
        resultado = carregar()
        del resultado["obstaculos"]
        return resultado

    return router


app = FastAPI(title="ROTA LIVRE — exemplo local de integração RPA")
app.include_router(criar_roteador())
