"""Leitura da lista de obstáculos e recuperação de falhas da API."""

import json
import logging
import math
import time
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


LOGGER = logging.getLogger("rota_livre.leitor")


class ErroLeitura(Exception):
    """Falha de entrada com mensagem adequada para o log."""


def _rejeitar_constante(_valor):
    raise ValueError("Constante fora do padrão JSON.")


def _ler_numero(valor):
    numero = float(valor)
    if not math.isfinite(numero):
        raise ValueError("Número fora da faixa representável.")
    return numero


def _decodificar(conteudo, chave_lista=None):
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeError:
        raise ErroLeitura("A entrada deve estar em UTF-8.") from None
    if not texto.strip():
        raise ErroLeitura("Entrada vazia.")
    try:
        dados = json.loads(texto, parse_constant=_rejeitar_constante, parse_float=_ler_numero)
    except json.JSONDecodeError as erro:
        raise ErroLeitura(f"JSON malformado na linha {erro.lineno}, coluna {erro.colno}.") from None
    except (ValueError, RecursionError):
        raise ErroLeitura("JSON contém valor numérico ou nível de aninhamento não suportado.") from None

    if chave_lista:
        if not isinstance(dados, dict) or chave_lista not in dados:
            raise ErroLeitura("O objeto JSON não contém a chave de lista configurada.")
        dados = dados[chave_lista]
    if not isinstance(dados, list):
        raise ErroLeitura("Estrutura incompatível. Era esperada uma lista de obstáculos.")
    return dados


def ler_arquivo(caminho):
    try:
        conteudo = caminho.read_bytes()
    except FileNotFoundError:
        raise ErroLeitura("Arquivo JSON inexistente.") from None
    except (OSError, ValueError):
        raise ErroLeitura("Não foi possível ler o arquivo JSON.") from None
    return _decodificar(conteudo)


def ler_api(url, chave_lista, timeout, tentativas, intervalo):
    for tentativa in range(1, tentativas + 1):
        repetir = True
        try:
            requisicao = Request(url, headers={"Accept": "application/json"})
            with urlopen(requisicao, timeout=timeout) as resposta:
                return _decodificar(resposta.read(), chave_lista)
        except HTTPError as erro:
            erro.close()
            motivo = f"HTTP {erro.code}"
            repetir = erro.code in {408, 429} or 500 <= erro.code < 600
        except URLError as erro:
            motivo = "timeout" if isinstance(erro.reason, TimeoutError) else "falha de conexão"
        except TimeoutError:
            motivo = "timeout"
        except (OSError, HTTPException):
            motivo = "falha de conexão ou de leitura da resposta"
        except (ValueError, OverflowError):
            motivo = "configuração de conexão inválida"
            repetir = False
        except ErroLeitura as erro:
            motivo = str(erro)

        LOGGER.warning("API, tentativa %d de %d. %s.", tentativa, tentativas, motivo.rstrip("."))
        if not repetir or tentativa == tentativas:
            break
        time.sleep(intervalo)
    raise ErroLeitura("Não foi possível obter uma lista de obstáculos da API.")


def carregar_registros(config):
    if config.arquivo is not None:
        return ler_arquivo(config.arquivo), "arquivo"
    try:
        registros = ler_api(config.api_url, config.chave_lista, config.timeout,
                            config.tentativas, config.intervalo)
    except ErroLeitura as erro:
        if config.contingencia is None:
            raise
        LOGGER.error("Falha na API. %s", erro)
        LOGGER.warning("Usando arquivo local de contingência após falha da API.")
        return ler_arquivo(config.contingencia), "contingencia"
    if config.adaptador_mvp:
        # A API do MVP fornece o tipo, mas não possui um campo de descrição.
        registros = [
            {"descricao": "Descrição não fornecida pela API do MVP.", **registro}
            if isinstance(registro, dict) else registro
            for registro in registros
        ]
    return registros, "api"
