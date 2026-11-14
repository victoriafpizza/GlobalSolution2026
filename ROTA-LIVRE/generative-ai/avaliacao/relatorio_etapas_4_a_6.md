# Evidências da execução local

Windows x64, Python 3.12, PyTorch 2.7.1 CPU, Sentence Transformers 4.1.0, FAISS 1.10.0 e Qwen2.5-0.5B-Instruct Q4_K_M em llama.cpp b12329. Uma instalação sobre o diretório anterior falhou com WinError 5 ao substituir uma DLL do PyTorch. Uma instalação limpa em `.rag-local/runtime` resolveu a falha.

## Comandos executados

- `python -B scripts/validar_base.py` — 3 fontes, 30 chunks e 30 casos.
- `python -B -m scripts.construir_indice` — 30 vetores persistidos.
- `python -B -m scripts.avaliar_recuperacao` — 30 consultas com scores reais.
- `python -B -m unittest discover -s tests -v` — 12 testes aprovados, zero falhas na execução final. Casos de falha e entradas hostis da camada de geração usam clientes simulados.
- `python -B -m scripts.comparar_configuracoes` — 90 casos executados, com inferência real onde a política precisou do modelo.
- `python -B -m scripts.testar_geracao 'O elevador da estação Paraíso está funcionando agora?'` — recusa literal com lista de citações vazia.

## Comparação

| Configuração | Status correto | Texto e citação esperados nos factuais | Respostas com suporte textual | Recusas adequadas | JSON válido do modelo | Latência média |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 13/30 | 0/18 | 0 | 8/8 | 29/30 | 1,32 s |
| RAG simples | 25/30 | 9/18 | 13 | 8/8 | 17/17 | 1,41 s |
| Agente | 25/30 | 9/18 | 13 | 8/8 | 17/17 | 1,34 s |

A saída final passou pelo schema nos 90 casos. As recusas e pedidos de esclarecimento podem ocorrer antes da inferência. Os dois modos documentais rejeitaram as decisões de qa-006 e qa-011 por suporte textual ou citação inválida. Dos 13 resultados com suporte textual, quatro citaram trechos diferentes dos esperados. Em qa-001, por exemplo, o agente citou um trecho sobre adaptação de projetos para uma pergunta sobre a definição de desenho universal. A verificação da fonte funcionou, mas a escolha não respondeu à pergunta.

Em qa-002, o agente recuperou lbi-02, ace-02 e ace-05, executou buscar_documentos, validar_evidencias, obter_chunk e verificar_fonte e citou lbi-02, conforme o gabarito. O evento teve quatro chamadas de ferramenta e uma inferência. A trilha por caso está em [comparacao_configuracoes.json](comparacao_configuracoes.json). A latência veio de uma execução sequencial em CPU e não demonstra vantagem de desempenho do agente.

A próxima avaliação deve reservar um conjunto independente para calibrar o limiar, auditar semanticamente respostas e citações, medir alucinações e testar ataques mais variados. A coincidência textual e a acurácia de status são insuficientes para aprovar uso público.
