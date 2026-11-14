# Checklist da entrega final

| Área | Estado | Verificação |
| --- | --- | --- |
| Desenvolvimento | Concluído e verificado | 19 testes aprovados, zero reprovados. Build Vite 8.3.7 concluído. GET de obstáculos retornou dois itens. |
| Desenvolvimento | Concluído e verificado | Seis POSTs reais passaram, três em RAG e três no agente. No navegador foram observados dois marcadores, popup e as três respostas do roteiro. |
| Dados e histórico | Concluído e verificado | Corpus, gabarito e comparação histórica conferidos por SHA-256. Quatro notebooks com saídas salvas. |
| Documentação | Concluído e verificado | README, relatório, roteiro, guia e links relativos conferidos. |
| Identificação acadêmica | Parcial | Projeto, disciplina e instituição identificados. Preencher integrantes e respectivos RMs após confirmação. |
| GitHub | Pendente | Publicação das mudanças locais fora do escopo desta revisão. Repositórios de referência constam no README. |
| Vídeo | Pendente | Vídeo ainda não gravado. Gravar localmente e preencher o link quando existir. |
| Bloqueios para gravar localmente | Concluído e verificado | Nenhum bloqueio observado no fluxo testado. |

## Evidência da revisão

- `python -B scripts/validar_base.py` confirmou 3 fontes, 30 chunks e 30 casos.
- `python -B -m unittest discover -s tests -v` passou em 19 testes.
- `npm.cmd run build` com `VITE_AI_LOCAL=1` passou.
- [Respostas HTTP dos dois modos](../evidencias/consultas_gravacao.json) e [roteiro](roteiro_video.md).
- SHA-256 do corpus: `d96b730e168e1c4222bed2d64808219c0727e77116b84522ce876c16de90e222`.
- SHA-256 do gabarito: `32898ca73bc88f6e9390176e46f080cdd39a1573d93da706ee36073a43ee2051`.
- SHA-256 da comparação histórica: `7ef99ccc236aad8816f1a1058b77595642073a84d947dd7eacb71ff4932ff075`.

O relatório de consolidação preserva as duas versões documentais divergentes. A revisão não encontrou conflito que impedisse a gravação. O teste emite um aviso de depreciação do TestClient, com a suíte aprovada. [Manifesto](manifesto_consolidacao.json)
