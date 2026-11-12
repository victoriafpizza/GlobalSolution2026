# ROTA LIVRE — Validação da Etapa 3

Global Solution FIAP 2026.2 · Robotic Process Automation

Victoria Franceschini Pizza · RM 550609

## Resultado

| Área | Situação | Resultado comprovado |
| --- | --- | --- |
| Logs | APROVADO | Horário UTC, ID por execução, origem, início e término, totais, advertências com motivo, erros operacionais e rotação com três cópias. |
| FastAPI de exemplo | APROVADO | Duas rotas testadas via HTTP em 127.0.0.1 com FastAPI 0.162.5 e Uvicorn 0.54.0. |
| Regressão | APROVADO | Oito testes automatizados concluídos com código 0. |

| Cenário | Esperado | Obtido | Situação |
| --- | --- | --- | --- |
| Lote de exemplo | 6 recebidos, 4 válidos, 1 inválido, 1 duplicado | Totais iguais no log, no relatório JSON e na resposta HTTP. Situação sucesso_parcial. | APROVADO |
| Execuções limpas | Publicar os relatórios com situação sucesso e IDs distintos | Duas execuções sobre o mesmo lote válido publicaram relatórios com IDs distintos, código 0 e erros=0. | APROVADO |
| Laço e prioridades | Visitar todas as posições e aplicar os três ramos de classificação | Posições 1 a 6. Prioridades alta, alta, média e baixa. | APROVADO |
| Inválido e duplicado | Registrar motivo e continuar o lote | Advertências para as posições 6 e 5. O duplicado referencia a posição 1. | APROVADO |
| JSON malformado | Informar linha e coluna e encerrar sem relatório | Erro na linha 1, coluna 12, código 1 e situação falha. | APROVADO |
| API indisponível | Limitar tentativas e registrar falha | Porta local sem serviço. Duas tentativas, evento ERROR, código 1 e situação falha. | APROVADO |
| Rotação | Manter o log ativo e até três cópias | Limite reduzido em teste isolado. Criados o arquivo ativo e os sufixos 1, 2 e 3. | APROVADO |
| Arquivo ausente, incompleto ou corrompido | Tratar falhas e recuperar o último compatível | 404 quando ausente, 503 quando só há arquivo corrompido. Candidatos mais novos incompletos e corrompidos foram descartados em favor do relatório válido. | APROVADO |
| Endpoints com relatório | HTTP 200 e prioridades corretas | Ambas as rotas retornaram 200. Contagem por prioridade de 2 altas, 1 média e 1 baixa. | APROVADO |
| Preservação dos arquivos | Manter entrada e evidências anteriores | SHA-256 da entrada de exemplo e das sete evidências anteriores permaneceu idêntico. | APROVADO |

## Evidências

- [07_logs_execucao_normal.txt](07_logs_execucao_normal.txt)
- [08_logs_erros.txt](08_logs_erros.txt)
- [09_saida_integracao.json](09_saida_integracao.json)
- [10_validacao_integracao.txt](10_validacao_integracao.txt)
- [11_testes_regressao.txt](11_testes_regressao.txt)

Os comandos de instalação, execução, consulta e teste estão no [README](../README.md). A API indisponível e os endpoints foram testados exclusivamente em loopback. A instalação no MVP real depende do acesso ao backend, da confirmação de rotas e contrato, do acesso ao diretório de relatórios e da configuração dos controles de acesso. O PDD estava indisponível no workspace.
