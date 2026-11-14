"""Integração opt-in para a demonstração local do assistente."""

from functools import lru_cache
from pathlib import Path
from threading import Lock
from time import monotonic
from typing import Literal
import sys

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "generative-ai"))
from llm.cliente_local import ClienteLocal
from llm.gerador import Gerador, limiar_local
from llm.schemas import Resposta
from rag.busca import Busca

router = APIRouter()
gate = Lock()
last_request = 0.0
ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173"}


class Consulta(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)
    pergunta: str = Field(min_length=1, max_length=600)
    modo: Literal["rag", "agente"] = "agente"


@lru_cache(maxsize=1)
def assistente():
    return Gerador(ClienteLocal(timeout=25), Busca(), limiar_local())


def responder(consulta):
    resposta, evento = assistente().executar(consulta.pergunta, consulta.modo)
    if evento["erro"] == "RuntimeError":
        raise RuntimeError("Inferência indisponível")
    return resposta


@router.post(
    "/api/ai/ask",
    response_model=Resposta,
    openapi_extra={"requestBody": {"required": True, "content": {
        "application/json": {"schema": Consulta.model_json_schema()},
    }}},
)
async def perguntar(request: Request):
    global last_request
    if (request.client is None or request.client.host not in {"127.0.0.1", "::1"}
            or request.headers.get("origin") not in (ORIGINS | {None})):
        raise HTTPException(403, "Acesso restrito à demonstração local.")
    if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
        raise HTTPException(415, "Use application/json.")
    body = bytearray()
    async for part in request.stream():
        if len(body) + len(part) > 4096:
            raise HTTPException(413, "Corpo da consulta muito grande.")
        body.extend(part)
    try:
        consulta = Consulta.model_validate_json(body)
    except ValidationError:
        raise HTTPException(422, "Informe uma pergunta válida e um modo permitido.") from None
    if not gate.acquire(blocking=False):
        raise HTTPException(429, "Assistente ocupado. Tente novamente.")
    try:
        now = monotonic()
        if now - last_request < 1:
            raise HTTPException(429, "Aguarde antes de enviar outra pergunta.")
        last_request = now
        try:
            return await run_in_threadpool(responder, consulta)
        except Exception:
            raise HTTPException(503, "Assistente indisponível no momento.") from None
    finally:
        gate.release()
