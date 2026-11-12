# ROTA LIVRE — Robotic Process Automation

FIAP Global Solution 2026.2 · Etapa 3 — Logs e integração com FastAPI

Victoria Franceschini Pizza · RM 550609

O robô lê um lote de relatos de obstáculos urbanos, valida e classifica os itens e publica um relatório JSON com registros válidos, inválidos e duplicados. A execução gera logs operacionais. Um roteador FastAPI de exemplo disponibiliza uma projeção dos registros válidos para consumo pelo mapa.

## Estrutura e tecnologias

```text
RPAGS/
├── main.py e config.py
├── src/                 # Leitura, regras de triagem, relatório, logs e integração
├── dados/               # Entrada de exemplo e relatórios em saida/
├── logs/                # Log operacional e arquivos rotacionados
├── integracao_backend/  # Aplicação e roteador FastAPI de exemplo
├── tests/               # Regressão automatizada com unittest e HTTP local
└── evidencias/          # Resultados registrados das etapas 2 e 3
```

O robô usa Python 3.10+ e a biblioteca padrão, incluindo `logging`, `json` e `urllib`. A aplicação de exemplo e os testes HTTP usam FastAPI e Uvicorn, instalados separadamente.

## Execução no PowerShell do VS Code

Abra o PowerShell na pasta RPAGS do repositório clonado ou da cópia independente. Com Python 3.10 ou posterior, execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv\Scripts\python.exe .\main.py --arquivo .\dados\obstaculos_exemplo.json
```

O projeto usa a biblioteca padrão. O comando de instalação verifica o arquivo de dependências, que está vazio de pacotes externos. O exemplo gera seis itens, com quatro válidos, um inválido e um duplicado.

```powershell
.\.venv\Scripts\python.exe .\main.py --help
$LASTEXITCODE
```

O código de saída é `0` quando o relatório é gravado, inclusive se o lote contiver itens inválidos. Falhas de leitura ou escrita retornam `1` e erros nos argumentos retornam `2`.

## Origem dos dados

- **Arquivo local.** Use `--arquivo` com um JSON UTF-8 cuja raiz seja uma lista. Sem origem configurada, o robô usa o arquivo de exemplo.
- **API.** Use `--api-url` com a URL de consulta GET. A resposta deve ser uma lista JSON ou um objeto com a lista sob a chave de primeiro nível indicada por `--chave-lista`. Por exemplo, use `--chave-lista obstaculos` para uma resposta como `{"obstaculos": [...]}`.
- **Contingência.** Use `--contingencia` com um arquivo JSON local. O robô só lê esse arquivo após uma falha da API e identifica os dados como `contingencia` no relatório e no log.

Para consultar uma API com uma URL já definida na variável de ambiente `ROTA_API_URL`:

```powershell
.\.venv\Scripts\python.exe .\main.py --api-url $env:ROTA_API_URL --timeout 5 --tentativas 3 --intervalo 1
```

As variáveis em [.env.example](.env.example) podem ser definidas na sessão PowerShell com `$env:NOME = 'valor'`. O arquivo serve como referência de configuração. Argumentos explícitos têm precedência sobre as variáveis de ambiente.

## Regras de processamento

| Campo | Validação |
| --- | --- |
| `id` | Inteiro ou texto não vazio |
| `tipo`, `descricao`, `status` | Texto não vazio |
| `latitude` | Número entre −90 e 90, inclusive |
| `longitude` | Número entre −180 e 180, inclusive |

O robô valida todos os itens da lista e informa os motivos dos erros por registro. A primeira ocorrência válida de um ID recebe prioridade. As próximas ocorrências válidas do mesmo ID entram em `duplicados` com o motivo e a posição da primeira ocorrência válida. Na comparação, `101`, `"101"` e `" 101 "` representam o mesmo ID. O texto `"0101"` representa um ID distinto. A comparação usa apenas o ID e preserva os campos originais no relatório.

A prioridade é `alta` para rampa bloqueada ou travessia perigosa, `media` para calçada danificada e `baixa` para os demais tipos válidos. A classificação desconsidera diferenças de maiúsculas, acentos e espaços no tipo.

## Falhas e relatório

Uma entrada sem conteúdo, com sintaxe JSON inválida ou com estrutura incompatível gera uma mensagem de erro. Uma lista vazia é um lote válido com contagens zeradas. Respostas vazias ou inválidas da API, timeout, falhas de conexão e HTTP 408, 429 e 5xx permitem nova tentativa dentro do limite configurado. Outros erros HTTP encerram as tentativas. O log da API registra a causa sem imprimir URL, cabeçalhos ou corpo da resposta.

Cada execução bem-sucedida cria um novo arquivo `dados/saida/resultado_<id>.json` com a origem efetiva, as contagens e os itens de cada categoria. A posição dos registros começa em 1. Os arquivos de entrada permanecem disponíveis para conferência.

## Logs operacionais

O arquivo `logs/rota_livre.log` registra horário em UTC, nível, identificador da execução e mensagem. O encerramento inclui origem, totais do lote, quantidade de eventos de nível `ERROR` e situação. Registros inválidos e duplicados são advertências com posição e motivo. O caminho do relatório fica no log local, e o conteúdo da entrada, as credenciais e a URL da API ficam fora dos logs.

O log rotaciona em 1 MiB e retém três cópias. O Git ignora o arquivo ativo e as cópias. Consulte as linhas recentes no PowerShell:

```powershell
Get-Content -LiteralPath .\logs\rota_livre.log -Encoding utf8 -Tail 30
```

`sucesso` indica que o relatório foi publicado sem inválidos, duplicados ou contingência. `sucesso_parcial` indica que o relatório foi publicado com pelo menos uma dessas ocorrências. Ambas retornam código `0`. `falha` fica no log quando a execução não publica um relatório.

## Integração FastAPI de exemplo

O relatório mantém `origem`, `resumo`, `validos`, `invalidos` e `duplicados`. A Etapa 3 acrescenta `execucao_id`, `processado_em` em UTC e `situacao`. A gravação publica o arquivo completo de uma só vez para evitar que o consumidor leia JSON durante a escrita.

`ler_ultimo_relatorio(pasta)`, em `src.integracao`, seleciona o relatório compatível mais recente pela data de modificação. Ele verifica os metadados, as contagens e os obstáculos válidos e ignora candidatos incompletos, corrompidos, vinculados a outros arquivos ou anteriores ao formato da Etapa 3. Se for necessário consumir os dados de um lote anterior, execute novamente o robô com a entrada correspondente.

Instale as dependências opcionais e execute o servidor em um terminal:

```powershell
.\.venv\Scripts\python.exe -m pip install 'fastapi>=0.115,<1' 'uvicorn>=0.30,<1'
.\.venv\Scripts\python.exe -m uvicorn integracao_backend.exemplo_fastapi:app --host 127.0.0.1 --port 8000
```

Em outro terminal, gere o relatório e consulte os endpoints:

```powershell
.\.venv\Scripts\python.exe .\main.py --arquivo .\dados\obstaculos_exemplo.json
Invoke-RestMethod 'http://127.0.0.1:8000/rpa/obstaculos-processados' | ConvertTo-Json -Depth 8
Invoke-RestMethod 'http://127.0.0.1:8000/rpa/resumo' | ConvertTo-Json -Depth 8
```

Os endpoints retornam HTTP `200` com o relatório disponível, `404` quando nenhum relatório existe e `503` quando os relatórios estão inacessíveis ou nenhum candidato é válido. A consulta de obstáculos inclui ID, tipo, coordenadas, prioridade e `status_triagem`. Ambas incluem os totais por prioridade. A [resposta HTTP registrada](evidencias/09_saida_integracao.json) mostra o contrato efetivamente testado.

### Integração com o backend do MVP

No repositório principal, o backend registra o roteador quando `RPA_RELATORIOS_DIR` aponta para o diretório de saída do robô. A rota existente `/api/obstacles` retorna um objeto com a lista `obstaculos`. O adaptador explícito `--adaptador-mvp` lê essa lista e registra uma indicação de ausência quando a API omite `descricao`. Os demais campos continuam sujeitos às regras de validação do robô. A integração foi testada no backend real executado localmente.

A partir da raiz do repositório principal, prepare e inicie o backend:

```powershell
python -m venv .venv
$py = (Resolve-Path .\.venv\Scripts\python.exe).Path
& $py -m pip install -r .\ROTA-LIVRE\backend\requirements.txt
$env:PYTHONPATH = (Resolve-Path .\RPAGS).Path
$env:RPA_RELATORIOS_DIR = (Resolve-Path .\RPAGS\dados\saida).Path
& $py -m uvicorn main:app --app-dir .\ROTA-LIVRE\backend --host 127.0.0.1 --port 8000
```

Em outro PowerShell, na mesma raiz:

```powershell
& .\.venv\Scripts\python.exe .\RPAGS\main.py --api-url http://127.0.0.1:8000/api/obstacles --adaptador-mvp
Invoke-RestMethod 'http://127.0.0.1:8000/api/obstacles'
Invoke-RestMethod 'http://127.0.0.1:8000/rpa/obstaculos-processados' | ConvertTo-Json -Depth 8
Invoke-RestMethod 'http://127.0.0.1:8000/rpa/resumo'
```

Para verificar a configuração Docker, execute na raiz `docker compose -f ROTA-LIVRE/compose.yaml -f RPAGS/integracao_backend/compose.rpa.yaml config --quiet`. O override monta o código Python e o diretório de relatórios em modo somente leitura. O usuário do contêiner precisa ter permissão de leitura dos relatórios. A configuração base mantém a API em loopback e o proxy do mapa encaminha as rotas sob `/api/`.

A aplicação de exemplo foi projetada para loopback. Antes de publicar os endpoints, o backend precisa aplicar sua autenticação e autorização ao roteador, revisar a exposição de IDs, tipos e coordenadas e servir o tráfego por HTTPS. Os endpoints usam campos selecionados e mantêm descrições, erros individuais e caminhos internos no ambiente local. A documentação do roteador segue o [guia oficial de aplicações FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

## Testes de regressão

Com as dependências opcionais instaladas, execute no PowerShell:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

A suíte usa pastas temporárias e portas locais efêmeras. Ela exercita a CLI, os relatórios, os logs e requisições HTTP reais em `127.0.0.1`. O sistema precisa permitir conexões loopback. Veja o [resumo da Etapa 3](evidencias/resumo_etapa3.md) para as verificações e evidências.
