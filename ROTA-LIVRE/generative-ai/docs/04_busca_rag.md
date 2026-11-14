# Etapa 4 · Recuperação semântica

Execute na raiz de `C:\Generative AI for Engineering` com Python 3.12 x64.

```powershell
py -3.12 -m venv .venv
$python = '.\.venv\Scripts\python.exe'
& $python -m pip install -r requirements.txt
& $python -m scripts.construir_indice --baixar-modelo
$env:HF_HUB_OFFLINE = '1'
& $python -m scripts.construir_indice
& $python -m scripts.avaliar_recuperacao
& $python -m rag.busca 'O que significa desenho universal segundo a LBI?' -k 3
& $python -m unittest discover -s tests -v
```

O primeiro comando de indexação com `--baixar-modelo` busca a revisão `e8f8c211226b894fcb81acc59f3b34ba3efd5f42` do [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/tree/e8f8c211226b894fcb81acc59f3b34ba3efd5f42). Um snapshot dessa revisão pode ser colocado em `.rag-local/model` para instalação offline. O modelo multilíngue roda em CPU e produz vetores de 384 dimensões.

O índice FAISS IndexFlatIP usa produto interno em vetores float32 unitários, equivalente ao cosseno. O arquivo local combina índice e manifesto de posições, IDs, revisão e hash dos registros documentais. O carregamento revalida a base e rejeita divergências. O índice é substituído atomicamente na reconstrução. Use apenas índices gerados localmente.

Recall@k é a média, por pergunta factual, de IDs relevantes recuperados divididos pelos IDs relevantes esperados. Hit@k é a proporção de perguntas com pelo menos um ID esperado recuperado. Ambas coincidem neste conjunto porque cada pergunta factual tem um único ID esperado. A busca recebe apenas o texto da pergunta. O avaliador aplica os IDs depois da recuperação e mantém perguntas ambíguas e sem evidência fora do denominador.

Os resultados por consulta ficam em [resultados_recuperacao.json](../avaliacao/resultados_recuperacao.json). A [análise](../avaliacao/analise_limiar.md) explica a calibração exploratória.
