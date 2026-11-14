# Guia de gravação no Windows

Abra o [MVP local](http://127.0.0.1:5173/). Se já estiver funcionando, use os serviços existentes. As portas verificadas foram 18081 para llama.cpp, 8000 para FastAPI e 5173 para Vite. Inicie apenas os serviços ausentes.

## Preparação

Use PowerShell, Python 3.12 x64 e Node.js. No ambiente auditado, os pesos GGUF e o executável estão em `C:\Generative AI for Engineering\.rag-local`. Use os comandos abaixo para essa instalação. Em outra máquina, siga os [guias de embeddings](04_busca_rag.md) e [do Qwen e llama.cpp](05_geracao_json.md) para obter as revisões indicadas. Ajuste a variável de runtime para a pasta escolhida.

Para criar um ambiente novo, na raiz de `generative-ai`:

```powershell
Set-Location 'C:\GSIA\ROTA-LIVRE\generative-ai'
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-entrega.txt
& .\.venv\Scripts\python.exe -B scripts/validar_base.py
& .\.venv\Scripts\python.exe -B -m scripts.construir_indice --baixar-modelo
```

## Terminal 1 · Modelo

```powershell
$runtime = 'C:\Generative AI for Engineering\.rag-local'
& "$runtime\llama\llama-server.exe" -m "$runtime\qwen.gguf" --host 127.0.0.1 --port 18081 -ngl 0 -t 4 -c 4096 --jinja
```

## Terminal 2 · Backend

```powershell
Set-Location 'C:\GSIA\ROTA-LIVRE\generative-ai'
$python = (Resolve-Path '.venv/Scripts/python.exe').Path
$env:ROTA_LIVRE_AI_LOCAL = '1'
$env:HF_HUB_OFFLINE = '1'
Set-Location ../backend
& $python -B -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-proxy-headers --no-access-log
```

## Terminal 3 · Frontend

```powershell
Set-Location 'C:\GSIA\ROTA-LIVRE\frontend'
npm.cmd ci
$env:VITE_AI_LOCAL = '1'
npm.cmd run dev -- --port 5173 --strictPort
```

## Conferência antes de gravar

```powershell
Invoke-RestMethod 'http://127.0.0.1:18081/health'
Invoke-RestMethod 'http://127.0.0.1:8000/api/obstacles'
(Invoke-WebRequest 'http://127.0.0.1:5173/').StatusCode
```

O modelo deve retornar `ok`, a API deve listar dois obstáculos e o Vite deve retornar HTTP 200. Abra o navegador e siga o [roteiro com as três perguntas e suas respostas](roteiro_video.md). Para testar o endpoint diretamente:

```powershell
$body = @{ pergunta = 'Em que espaços podem existir barreiras urbanísticas?'; modo = 'agente' } | ConvertTo-Json
Invoke-RestMethod 'http://127.0.0.1:8000/api/ai/ask' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

Repita com `modo = 'rag'` se quiser comparar. Aguarde pelo menos um segundo entre envios.

## Se algo falhar

- **Porta ocupada:** confira se o serviço esperado já está respondendo antes de abrir outro. O proxy do Vite aponta para 8000 e a origem autorizada usa 5173.
- **Chat ausente:** confira `VITE_AI_LOCAL=1` e reinicie o Vite. Para HTTP 404 na rota de IA, confira `ROTA_LIVRE_AI_LOCAL=1` e reinicie o backend.
- **HTTP 503:** confira o health do modelo, o ambiente Python e o índice em `.rag-local/indice.zip`. Se necessário, reconstrua com `python -B -m scripts.construir_indice` na pasta da disciplina.
- **HTTP 429:** aguarde o processamento anterior e o intervalo de um segundo.
- **Marcadores sem fundo do mapa:** confira a conectividade com OpenStreetMap. O carregamento dos obstáculos usa a API local.
- **`.venv` ausente:** execute a preparação acima antes de reiniciar o backend. A auditoria usou o Python 3.12 empacotado no Codex e dependências locais já instaladas. A criação de uma nova `.venv` não fez parte deste ensaio.

Após gravar, pressione Ctrl+C nos terminais do Vite, do Uvicorn e do llama.cpp que você tiver iniciado.
