"""Configura o log operacional e contabiliza eventos de erro da execução."""

import logging
import time
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler


LOGGER = logging.getLogger("rota_livre")


class ContextoExecucao(logging.Filter):
    def __init__(self, execucao_id):
        super().__init__()
        self.execucao_id = execucao_id
        self.erros = 0

    def filter(self, registro):
        registro.execucao_id = self.execucao_id
        if registro.levelno >= logging.ERROR:
            self.erros += 1
        return True


@contextmanager
def configurar_logs(pasta, execucao_id):
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = RotatingFileHandler(
        pasta / "rota_livre.log", maxBytes=1_048_576, backupCount=3,
        encoding="utf-8", errors="backslashreplace",
    )
    contexto = ContextoExecucao(execucao_id)
    formato = logging.Formatter(
        "%(asctime)sZ | %(levelname)s | %(execucao_id)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    formato.converter = time.gmtime
    arquivo.setFormatter(formato)
    arquivo.addFilter(contexto)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(levelname)s %(message)s"))

    nivel_anterior, propagacao_anterior = LOGGER.level, LOGGER.propagate
    LOGGER.setLevel(logging.INFO)
    LOGGER.propagate = False
    for handler in (arquivo, console):
        LOGGER.addHandler(handler)
    try:
        yield contexto
    finally:
        for handler in (arquivo, console):
            LOGGER.removeHandler(handler)
            handler.close()
        LOGGER.setLevel(nivel_anterior)
        LOGGER.propagate = propagacao_anterior
