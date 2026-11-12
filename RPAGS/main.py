"""Ponto de entrada da automação ROTA LIVRE."""

import sys
from datetime import datetime, timezone
from uuid import uuid4

from config import PASTA_LOGS, PASTA_SAIDA, ler_configuracao
from src.gerenciador_logs import LOGGER, configurar_logs
from src.leitor import ErroLeitura, carregar_registros
from src.robo import gravar_relatorio, processar


def main():
    execucao_id = uuid4().hex
    resumo = dict(total=0, validos=0, invalidos=0, duplicados=0)
    origem = "indisponivel"
    situacao = "falha"
    try:
        with configurar_logs(PASTA_LOGS, execucao_id) as log:
            LOGGER.info("Execução iniciada.")
            try:
                try:
                    config = ler_configuracao()
                except SystemExit as erro:
                    if erro.code:
                        LOGGER.error("Configuração inválida.")
                    else:
                        situacao = "sucesso"
                    raise

                origem = "arquivo" if config.arquivo is not None else "api"
                registros, origem = carregar_registros(config)
                relatorio = processar(registros, origem)
                resumo = relatorio["resumo"]

                for item in relatorio["invalidos"]:
                    LOGGER.warning("Registro inválido na posição %d. %s",
                                   item["posicao"], " ".join(item["motivos"]))
                for item in relatorio["duplicados"]:
                    LOGGER.warning("Registro duplicado na posição %d. %s Posição original: %d.",
                                   item["posicao"], item["motivo"], item["posicao_original"])

                situacao_prevista = "sucesso"
                if resumo["invalidos"] or resumo["duplicados"] or origem == "contingencia":
                    situacao_prevista = "sucesso_parcial"
                relatorio.update(
                    execucao_id=execucao_id,
                    processado_em=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                    situacao=situacao_prevista,
                )
                caminho = gravar_relatorio(relatorio, PASTA_SAIDA)
                situacao = situacao_prevista
                LOGGER.info("Origem dos dados: %s. Relatório: %s", origem, caminho)
                return 0
            except ErroLeitura as erro:
                LOGGER.error("Falha na entrada. %s", erro)
                return 1
            except (OSError, ValueError, RecursionError):
                LOGGER.error("Não foi possível gerar o relatório JSON.")
                return 1
            except KeyboardInterrupt:
                LOGGER.error("Execução interrompida.")
                return 130
            finally:
                LOGGER.info(
                    "Execução finalizada. origem=%s total=%d validos=%d invalidos=%d "
                    "duplicados=%d erros=%d situacao=%s",
                    origem, resumo["total"], resumo["validos"], resumo["invalidos"],
                    resumo["duplicados"], log.erros, situacao,
                )
    except OSError:
        print("ERROR Não foi possível inicializar o log operacional.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
