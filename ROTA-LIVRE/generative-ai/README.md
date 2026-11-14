# ROTA LIVRE · Generative AI for Engineering

Entrega local das etapas 1 a 13 da Global Solution FIAP 2026.2, integrada ao frontend e ao backend do ROTA LIVRE. Para a gravação, consulte o [guia de execução](docs/guia_gravacao.md), o [roteiro](docs/roteiro_video.md) e o [checklist final](docs/checklist_entrega_final.md).

**Integrantes e RMs da disciplina: preencher após confirmação.**

| Etapa | Entrega |
| --- | --- |
| 1 | [Problema, tarefa e critérios de aceite](docs/01_problema_tarefa.md) |
| 2 | [Metodologia e 30 casos com gabarito](avaliacao/README.md) |
| 3 | [Curadoria e proveniência](docs/03_base_documental.md) e [base documental](base/README.md) |

Na pasta deste README, execute com Python 3.10 ou superior. A validação funciona offline com a biblioteca padrão.

```sh
python -B scripts/validar_base.py
python -B -m unittest discover -s tests -v
```

A entrega inclui o contrato do assistente, a base e os testes de integridade. A recuperação, geração JSON e avaliação local estão implementadas.
Os resultados locais das etapas posteriores estão no [relatório final](relatorio/relatorio_final.md).

## Demonstração e reprodução no Windows

A base está em `base/`, o gabarito e os históricos em `avaliacao/`, a implementação em `rag/`, `llm/` e `agente/`, e os notebooks em `notebooks/`. O backend e o frontend ficam nos diretórios irmãos. O assistente fornece orientação documental de acessibilidade, com citação ou recusa.

Ambiente testado: Windows x64, Python 3.12.14, Node 24.15.0, PyTorch 2.7.1 CPU, Sentence Transformers 4.1.0, FAISS 1.10.0, NumPy 1.26.4, Pydantic 2.14.3, FastAPI 0.162.2, Uvicorn 0.54.0 e Vite 8.3.7. Reserve espaço para cerca de 1 GB de pesos, além do ambiente e dos caches. A execução usou CPU com quatro threads e sem GPU. O mínimo de RAM não foi medido.

Na raiz de generative-ai:

```powershell
py -3.12 -m venv .venv
$python = (Resolve-Path '.venv/Scripts/python.exe').Path
& $python -m pip install -r requirements-entrega.txt
& $python -B scripts/validar_base.py
& $python -B -m scripts.construir_indice --baixar-modelo
$env:HF_HUB_OFFLINE = '1'
& $python -B -m scripts.avaliar_qualidade
& $python -B -m unittest discover -s tests -v
& $python -B -m scripts.executar_notebooks
```

Baixe os modelos das fontes indicadas nos guias de [embeddings](docs/04_busca_rag.md) e [geração](docs/05_geracao_json.md). A geração usa Qwen2.5-0.5B-Instruct Q4_K_M e llama.cpp b12329 em 127.0.0.1:18081. Após subir o runtime, execute o agente via CLI:

```powershell
& $python -B -m scripts.testar_geracao 'Em que espaços podem existir barreiras urbanísticas?' --modo agente
```

Para repetir as avaliações de recuperação e de geração, use uma cópia de trabalho descartável da disciplina, pois os scripts das etapas anteriores escrevem os respectivos JSON e CSV em avaliacao/. Os comandos são `python -B -m scripts.avaliar_recuperacao` e `python -B -m scripts.comparar_configuracoes`. O histórico auditado desta entrega deve ser preservado.

Inicie o backend em outro terminal, a partir de generative-ai, com o mesmo ambiente:

```powershell
$python = (Resolve-Path '.venv/Scripts/python.exe').Path
$env:ROTA_LIVRE_AI_LOCAL = '1'
Set-Location ../backend
& $python -B -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-proxy-headers --no-access-log
```

Inicie o frontend a partir de ROTA-LIVRE/frontend em outro terminal:

```powershell
npm.cmd ci
$env:VITE_AI_LOCAL = '1'
npm.cmd run dev -- --port 5173 --strictPort
```

Abra [o MVP local](http://127.0.0.1:5173). O chat e o mapa compartilham o proxy de desenvolvimento. Na raiz da disciplina, `python -B -m scripts.validar_api_reservada` testa as rotas reais com ambos os modos. POST /api/ai/ask recebe JSON com pergunta e modo opcional (agente ou rag). A demonstração é restrita ao loopback, rejeita origens externas, limita corpo e concorrência e dispensa logs de perguntas. Evite enviar dados pessoais.

Histórico: Recall@1 72,22%, Recall@3 94,44%. Acerto integral: baseline 8/30, RAG 19/30, agente 19/30. O limiar é exploratório. Citações autênticas ainda podem ser impertinentes. A [evidência de integração](evidencias/integracao_local.md) e o [relatório](relatorio/relatorio_final.md) detalham os limites e as correções.

Repositórios de referência: [GlobalSolution2026](https://github.com/victoriafpizza/GlobalSolution2026) e [Generative AI for Engineering](https://github.com/victoriafpizza/Generative-AI-for-Engineering). As etapas finais permanecem locais, sem publicação ou merge. **Vídeo ainda não gravado. Link a preencher após a gravação.**
