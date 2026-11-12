# ROTA LIVRE — Robotic Process Automation

**Disciplina:** Robotic Process Automation — FIAP, Global Solution CitizenTech 2026.2  
**Autora:** Victoria Franceschini Pizza | **RM:** 550609

## Problema e objetivo

Registros de obstáculos urbanos chegam ao MVP com categorias, descrições e coordenadas que precisam de verificação. A automação coleta um lote, valida, identifica reprocessamentos, sinaliza relatos geograficamente próximos, atribui prioridade preliminar e produz arquivo estruturado, logs e resumo. O processo está especificado em `docs/PDD_ROTA_LIVRE.docx`.

## Estrutura

- `main.py`: comando de execução e orquestração.
- `src/processor.py`: validação, regras de prioridade e proximidade.
- `src/io_utils.py`: JSON, requisições HTTP, timeout e tentativas.
- `src/storage.py`: estado persistente SQLite/idempotência.
- `examples/`: entrada sintética e JSON propositalmente inválido.
- `tests/`: testes automatizados com `unittest`.
- `integracao_backend/rotas_rpa.py`: exemplo de rota FastAPI para ler a saída.
- `saida/`, `logs/`, `evidencias/`: arquivos locais ignorados pelo Git.

## Requisitos

Python 3.11 ou superior. O núcleo do RPA não precisa de bibliotecas externas. Executar os comandos abaixo **dentro da pasta `rpa`**.

## Executar com entrada local

```powershell
python main.py --source file --input examples/obstaculos.json
```

Arquivos gerados: `saida/obstaculos_processados.json`, `saida/resumo_execucao.json`, `saida/estado.sqlite3` e `logs/execucao.jsonl`. O estado SQLite permite que uma segunda execução identifique IDs já processados. Para repetir a primeira execução do zero, exclua `saida/estado.sqlite3` (apenas para teste).

## Executar com a API existente

Com FastAPI ligada, contendo `GET /obstaculos`:

```powershell
python main.py --source api --api-url http://localhost:8000/obstaculos
```

Aceita uma lista JSON ou um objeto JSON com a chave `obstaculos` que contenha uma lista. O esquema esperado por item é `id`, `tipo`, `descricao`, `latitude`, `longitude` e opcionalmente `criado_em`. Verificar compatibilidade do endpoint real antes da demonstração.

## Contingência, falhas e testes

```powershell
# API indisponível: usar JSON sintético de contingência
python main.py --source api --api-url http://localhost:9999/obstaculos --fallback examples/obstaculos.json

# JSON inválido: deve retornar código de erro 2 e registrar falha
python main.py --source file --input examples/invalido.json

# Testes unitários e de pipeline
python -m unittest discover -s tests -v
```

`--retries 3`, `--timeout 8` e `--distance 20` são configuráveis. HTTP 401/403 e 4xx não recuperáveis não acionam contingência automática. O robô não exclui registros com coordenadas próximas: somente sinaliza possível duplicidade.

## Integração com o MVP

**Modo já disponível no código:** gerar `saida/obstaculos_processados.json` (API/arquivo estruturado atende ao contrato de saída). Para tornar os resultados visíveis na interface React/Leaflet, a equipe precisa conectar o backend à saída e ajustar o frontend.

**Exemplo para FastAPI:** `integracao_backend/rotas_rpa.py` disponibiliza `GET /rpa/obstaculos-processados` lendo o arquivo. Copiar o módulo para uma pasta importável pelo backend, adicionar `app.include_router(router)` e configurar `RPA_RESULT_FILE` para o caminho real. O arquivo precisa estar acessível pelo processo da API, inclusive via volume se estiver em contêiner.

**Publicação HTTP opcional:** `--publish-url http://localhost:8000/obstaculos/{id}/triagem` usa PUT, mas exige criar o endpoint de escrita no backend; a rota atual `GET /obstaculos` não oferece escrita. Não ativar antes de implementar.

## Regras e exceções

- Campos obrigatórios e intervalos de latitude/longitude são validados.
- Categoria `rampa bloqueada` ou `travessia obstruída`: prioridade `alta`.
- Categoria `calçada danificada`: prioridade `media`.
- Outras categorias válidas: prioridade `normal`.
- Mesmo ID e mesmo conteúdo: reprocessamento ignorado.
- Mesmo tipo e distância até 20 m: possível duplicidade para revisão.
- API com erro temporário: até três tentativas exponenciais.
- JSON inválido: erro controlado; item inválido: rejeição individual.
- Todos os registros e eventos são identificados por id de execução e horário.

A triagem é preliminar: não substitui inspeção em campo. Nenhum token deve ser incluído em código, logs, exemplos ou capturas. Usar dados sintéticos nas evidências.

## Evidências e pendências da entrega

1. Executar o pipeline e salvar captura do terminal, JSON e resumo.
2. Executar a mesma entrada duas vezes e mostrar idempotência.
3. Demonstrar arquivo inválido, API indisponível e item rejeitado.
4. Conectar a rota RPA ao backend e consumir a saída na tela do MVP.
5. Preparar PDF técnico com arquitetura, regras, testes, LGPD e links.
6. Gravar vídeo com no máximo 3 minutos e inserir seu link no relatório.

**Estado:** implementação fornecida; testes e integração ao frontend ainda precisam ser executados/confirmados no ambiente do projeto. Não declarar resultados de teste antes da execução.
