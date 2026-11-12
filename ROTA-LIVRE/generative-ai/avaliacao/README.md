# Etapa 2 · Casos de teste com gabarito

[`casos_teste.jsonl`](casos_teste.jsonl) contém 30 casos. Cada linha é um objeto UTF-8 com pergunta, classificação, resposta de referência, estado, evidência e critério de aprovação.

| Categoria | Quantidade | Gabarito |
| --- | ---: | --- |
| `respondível` | 12 | Perguntas documentais diretas, com resposta e referências. |
| `parafrase` | 6 | Consultas independentes em linguagem cotidiana, com resposta e referências. |
| `ambigua` | 6 | Quatro pedidos de esclarecimento e duas recusas. |
| `sem_evidencia` | 6 | Resposta literal `não consta`. |

Os 18 casos factuais usam 18 unidades de evidência distintas. O gabarito registra literalmente o texto do chunk para tornar a verificação de integridade determinística. Na avaliação futura, aceite paráfrases fiéis que cumpram o critério individual, preservem as condições relevantes e citem a evidência. Perguntas de esclarecimento podem variar em formulação e devem pedir o contexto indicado. Recusas e casos sem evidência exigem o texto literal e listas vazias de referências.

## Avaliação futura

Para recuperação, medir Recall@k dos chunks esperados nos 18 casos factuais. Para geração, medir acerto do estado por categoria, cobertura das afirmações exigidas, fidelidade das citações e taxa de cumprimento da resposta literal. Revisar manualmente a relação pergunta–resposta–fonte e registrar erros por caso. A validação automática cobre estrutura e correspondência textual entre gabarito e corpus.

O processo de indexação deve ler apenas `base/chunks.jsonl` e os metadados de `base/fontes.json`. O avaliador envia a pergunta pelo mesmo caminho de uma consulta real. Manter resposta esperada, estado, IDs esperados, justificativa e critérios no avaliador até receber a saída. Excluir o diretório `avaliacao/` da indexação, dos exemplos do prompt e de qualquer treino. Se estes casos forem usados para ajustes, reservar novos casos independentes para a medição final.
