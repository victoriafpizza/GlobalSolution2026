from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Citacao(Strict):
    chunk_id: str
    source_id: str
    titulo: str
    url: str


class Resposta(Strict):
    status: Literal["respondido", "nao_consta", "esclarecimento_necessario"]
    pergunta: str
    resposta: str
    citacoes: list[Citacao]
    confianca: None


class Decisao(Strict):
    status: Literal["respondido", "nao_consta", "esclarecimento_necessario"]
    chunk_id: str | None
    texto: str = Field(max_length=1500)
