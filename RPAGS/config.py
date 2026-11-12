"""Configuração do robô por argumentos e variáveis de ambiente."""

import argparse
import math
import os
from pathlib import Path
from urllib.parse import urlsplit


RAIZ = Path(__file__).resolve().parent
ARQUIVO_EXEMPLO = RAIZ / "dados" / "obstaculos_exemplo.json"
PASTA_SAIDA = RAIZ / "dados" / "saida"
PASTA_LOGS = RAIZ / "logs"


def ler_configuracao():
    parser = argparse.ArgumentParser(description="Processa obstáculos do ROTA LIVRE.")
    origem = parser.add_mutually_exclusive_group()
    origem.add_argument("--arquivo", type=Path, help="Arquivo JSON de entrada.")
    origem.add_argument("--api-url", help="URL HTTP(S) de consulta.")
    parser.add_argument("--chave-lista", default=os.getenv("ROTA_CHAVE_LISTA"),
                        help="Chave de primeiro nível que contém a lista da API.")
    parser.add_argument("--contingencia", type=Path, default=os.getenv("ROTA_CONTINGENCIA") or None,
                        help="Arquivo local autorizado para falhas na API.")
    parser.add_argument("--timeout", type=float, default=os.getenv("ROTA_TIMEOUT", "5"),
                        help="Tempo limite da conexão/leitura, em segundos.")
    parser.add_argument("--tentativas", type=int, default=os.getenv("ROTA_TENTATIVAS", "3"),
                        help="Total de tentativas, incluindo a primeira.")
    parser.add_argument("--intervalo", type=float, default=os.getenv("ROTA_INTERVALO", "1"),
                        help="Espera entre tentativas, em segundos.")
    config = parser.parse_args()

    if config.arquivo is None:
        config.api_url = config.api_url or os.getenv("ROTA_API_URL")
        if not config.api_url:
            config.arquivo = ARQUIVO_EXEMPLO
    if config.api_url:
        try:
            url = urlsplit(config.api_url)
            url.port
            url_valida = (
                url.scheme in {"http", "https"} and url.hostname
                and url.username is None and url.password is None
                and not any(caractere.isspace() for caractere in config.api_url)
            )
        except ValueError:
            url_valida = False
        if not url_valida:
            parser.error("Informe uma URL HTTP(S) válida, sem credenciais embutidas.")

    if not math.isfinite(config.timeout) or config.timeout <= 0:
        parser.error("O timeout deve ser finito e maior que zero.")
    if config.tentativas < 1:
        parser.error("Informe pelo menos uma tentativa.")
    if not math.isfinite(config.intervalo) or config.intervalo < 0:
        parser.error("O intervalo deve ser finito e maior ou igual a zero.")
    return config
