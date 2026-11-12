"""Localiza um relatório da Etapa 3 e prepara os dados públicos da triagem."""

import json
import os
import stat
from datetime import datetime
from pathlib import Path
from uuid import UUID

from config import PASTA_SAIDA
from src.validador import validar


PRIORIDADES = ("alta", "media", "baixa")
CATEGORIAS = ("validos", "invalidos", "duplicados")
CAMPOS_MAPA = ("id", "tipo", "latitude", "longitude")


class RelatorioIndisponivel(Exception):
    """Falha de leitura com mensagem segura para o consumidor."""

    def __init__(self, mensagem, *, ausente=False):
        super().__init__(mensagem)
        self.ausente = ausente


def _preparar_resposta(relatorio):
    execucao_id = relatorio["execucao_id"]
    processado_em = relatorio["processado_em"]
    origem = relatorio["origem"]
    situacao = relatorio["situacao"]
    if UUID(execucao_id).hex != execucao_id or datetime.fromisoformat(processado_em).utcoffset() is None:
        raise ValueError("Metadados inválidos.")
    if origem not in ("arquivo", "api", "contingencia") or situacao not in ("sucesso", "sucesso_parcial"):
        raise ValueError("Origem ou situação inválida.")

    resumo = relatorio["resumo"]
    for categoria in CATEGORIAS:
        itens = relatorio[categoria]
        if not isinstance(itens, list) or type(resumo[categoria]) is not int or resumo[categoria] != len(itens):
            raise ValueError("Contagem incompatível com o relatório.")
    total = resumo["total"]
    if type(total) is not int or total != sum(resumo[categoria] for categoria in CATEGORIAS):
        raise ValueError("Total incompatível com o relatório.")

    por_prioridade = dict.fromkeys(PRIORIDADES, 0)
    obstaculos = []
    for item in relatorio["validos"]:
        registro = item["registro"]
        prioridade = item["prioridade"]
        if validar(registro) or prioridade not in PRIORIDADES:
            raise ValueError("Obstáculo processado inválido.")
        # O relatório interno preserva os registros. A API usa apenas os campos do mapa.
        mapa = {campo: registro[campo] for campo in CAMPOS_MAPA}
        for campo in ("id", "tipo"):
            if isinstance(mapa[campo], str):
                mapa[campo].encode("utf-8")
        obstaculos.append({**mapa, "prioridade": prioridade, "status_triagem": "processado"})
        por_prioridade[prioridade] += 1

    return {
        "execucao_id": execucao_id,
        "processado_em": processado_em,
        "origem": origem,
        "situacao": situacao,
        "resumo": {campo: resumo[campo] for campo in ("total", *CATEGORIAS)},
        "por_prioridade": por_prioridade,
        "obstaculos": obstaculos,
    }


def ler_ultimo_relatorio(pasta=PASTA_SAIDA):
    """Retorna o relatório compatível publicado mais recentemente na pasta confiável."""
    candidatos = []
    encontrou = False
    try:
        pasta = Path(pasta).resolve(strict=True)
        for caminho in pasta.iterdir():
            if not caminho.match("resultado_*.json"):
                continue
            encontrou = True
            try:
                estado = caminho.lstat()
                if stat.S_ISREG(estado.st_mode) and estado.st_nlink == 1:
                    candidatos.append((estado.st_mtime_ns, caminho, estado))
            except OSError:
                continue
    except FileNotFoundError:
        raise RelatorioIndisponivel("Nenhum relatório de triagem disponível.", ausente=True) from None
    except (OSError, RuntimeError, ValueError):
        raise RelatorioIndisponivel("Os relatórios de triagem estão indisponíveis.") from None

    for _, caminho, estado in sorted(candidatos, reverse=True):
        try:
            if caminho.resolve(strict=True) != caminho:
                continue
            with caminho.open(encoding="utf-8") as arquivo:
                atual = os.fstat(arquivo.fileno())
                if not os.path.samestat(estado, atual) or atual.st_nlink != 1:
                    continue
                return _preparar_resposta(json.load(arquivo))
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError, RuntimeError):
            continue

    if encontrou:
        raise RelatorioIndisponivel("Nenhum relatório de triagem válido está disponível.")
    raise RelatorioIndisponivel("Nenhum relatório de triagem disponível.", ausente=True)
