# Etapa 5 · Geração JSON

O cliente utiliza llama.cpp b12329 e [Qwen2.5-0.5B-Instruct GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/tree/9217f5db79a29953eb74d5343926648285ec7e67) na revisão indicada, quantização Q4_K_M. Ollama não foi encontrado no PATH. O executável portátil roda em CPU com quatro threads. Baixe o [pacote Windows CPU x64 do llama.cpp](https://github.com/ggml-org/llama.cpp/releases/tag/b12329) e o GGUF indicado antes de usar a integração offline.

```powershell
& .\.rag-local\llama\llama-server.exe -m .rag-local/qwen.gguf --host 127.0.0.1 --port 18081 -ngl 0 -t 4 -c 4096 --jinja
```

Em outro PowerShell com as dependências instaladas, execute na raiz:

```powershell
& .\.venv\Scripts\python.exe -m scripts.testar_geracao 'Em que espaços podem existir barreiras urbanísticas?'
& .\.venv\Scripts\python.exe -m scripts.testar_geracao 'O elevador da estação Paraíso está funcionando agora?'
```

O schema Pydantic exige status, pergunta, resposta, lista de citações e confiança nula. Os status são respondido, nao_consta e esclarecimento_necessario. A ausência de evidência produz literalmente `não consta`. O modelo retorna uma decisão estruturada interna. Respostas factuais do RAG exigem seleção de um ID fornecido e cópia exata do trecho. Título, URL e IDs são inseridos pela aplicação a partir do corpus. A igualdade textual verifica a origem das afirmações. A seleção pode continuar inadequada à pergunta, por isso relevância precisa ser medida à parte.

Filtros locais limitam tamanho, bloqueiam alguns padrões de instruções maliciosas e identificam consultas operacionais e ambiguidades comuns. São heurísticas, com cobertura limitada e risco de falso positivo. Falhas de inferência ou de validação retornam recusa e registram a classe do erro. A comparação preserva a distinção entre recusa legítima e erro de execução.
