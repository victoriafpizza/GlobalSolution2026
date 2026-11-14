# Etapas 7 e 8 · Placar auditado

Os 90 registros contêm os mesmos 30 casos, com perguntas e IDs na mesma ordem e IDs de execução únicos. O histórico declara um único modelo Qwen2.5-0.5B-Instruct Q4_K_M e uma revisão comum. O código usa o mesmo cliente, temperatura 0, seed 42, limite de 340 tokens e timeout de 25 s. A versão e os parâmetros foram conferidos no código e no relatório histórico. Os eventos não guardam o corpo HTTP nem uma identificação do modelo por requisição, o que limita a verificação retrospectiva.

| Métrica | Baseline | RAG simples | Agente |
| --- | ---: | ---: | ---: |
| Status correto | 13/30 (43,33%) | 25/30 (83,33%) | 25/30 (83,33%) |
| Acerto integral | 8/30 (26,67%) | 19/30 (63,33%) | 19/30 (63,33%) |
| Acerto factual | 0/18 (0%) | 9/18 (50%) | 9/18 (50%) |
| Citação esperada entre factuais | 0/18 (0%) | 9/18 (50%) | 9/18 (50%) |
| Citação existente e rastreável | N/A (0 emitidas) | 13/13 (100%) | 13/13 (100%) |
| Citação pertinente | N/A (0 emitidas) | 9/13 (69,23%) | 9/13 (69,23%) |
| Resposta correta e fundamentada | 0/30 (0%) | 9/30 (30%) | 9/30 (30%) |
| Alucinação factual observada | 1/5 (20%) | 0/13 (0%) | 0/13 (0%) |
| Resposta sem evidência textual verificável | 5/5 (100%) | 0/13 (0%) | 0/13 (0%) |
| Recusa adequada | 8/8 (100%) | 8/8 (100%) | 8/8 (100%) |
| Recusa indevida | 17/25 (68%) | 5/13 (38,46%) | 5/13 (38,46%) |
| JSON final válido | 30/30 (100%) | 30/30 (100%) | 30/30 (100%) |
| JSON do modelo válido, conforme evento | 29/30 (96,67%) | 17/17 (100%) | 17/17 (100%) |
| Latência média / p50 / p95 | 1,317 / 0,853 / 3,256 s | 1,414 / 1,894 / 2,950 s | 1,337 / 1,899 / 2,860 s |

O [CSV](placar_configuracoes.csv) abre todas as métricas por categoria. O [JSON de qualidade](metricas_qualidade.json) inclui percentis e contagens dos rótulos. A [auditoria](auditoria_respostas.jsonl) registra a decisão, a justificativa, o evento e o gabarito de cada execução.

Os números históricos de status, igualdade textual factual, citações esperadas, recusas e média de latência coincidem. O histórico chamava 13 respostas de fundamentadas a partir do suporte textual. A auditoria confirma a origem textual das 13 e a pertinência de nove. As quatro restantes têm conteúdo documental, porém respondem a outro requisito. Nos modos documentais, qa-021 e qa-022 acertam o estado de esclarecimento, mas pedem contexto genérico demais para acerto integral.

O agente e o RAG simples compartilham modelo, índice, top-3, limiar e validação extrativa. As ferramentas adicionais do agente conferem procedência, e os trechos errados eram registros autênticos. Houve diferenças individuais de seleção e recusa, sem ganho agregado. A latência inclui retornos anteriores à inferência e reflete uma execução sequencial. Ela não demonstra vantagem de desempenho.

Recall@1 de 13/18 e Recall@3 de 17/18 pertencem à recuperação bruta, anterior ao limiar e à geração. O acerto factual de 9/18 é da resposta final. O conjunto foi usado na calibração exploratória anterior e não constitui validação independente.
