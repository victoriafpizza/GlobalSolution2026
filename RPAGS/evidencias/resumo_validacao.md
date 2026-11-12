# ROTA LIVRE — Validação da Etapa 2

O PDD não estava disponível no workspace. A referência usada foi o README do projeto. Os cenários executados ficaram de acordo com as regras documentadas. A implementação existente atendeu aos critérios e permaneceu sem alterações.

| Cenário | Resultado esperado | Resultado observado | Situação |
| --- | --- | --- | --- |
| Execução normal | 6 recebidos, 4 válidos, 1 inválido e 1 duplicado | Contagens confirmadas no relatório, com código de saída 0 | APROVADO |
| A — API indisponível | Limitar tentativas, respeitar timeout e encerrar com mensagem clara | Porta sem serviço confirmada por sondagem. Três tentativas, mensagem de falha e código 1 em 2,339 s. Com um servidor local que reteve a resposta, os intervalos foram de 0,735 s e 0,716 s | APROVADO |
| B — JSON inválido | Identificar a sintaxe inválida e preservar a entrada original | Erro com linha e coluna, código 1, nenhum relatório, nenhum traceback e SHA-256 original idêntico | APROVADO |
| C — Registro inválido | Rejeitar a latitude inválida e processar o restante | ID 202 rejeitado com motivo. IDs 201 e 203 processados, código 0 | APROVADO |
| D — Duplicidade | Processar o primeiro ID válido, marcar a repetição e preservar os dois registros | ID 101 válido. ID " 101 " duplicado com motivo e posição original. Dois registros e SHA-256 idêntico na entrada, código 0 | APROVADO |

## Condições e repetições

- [main.py](../main.py#L20) encaminha o lote lido a processar.
- [src/robo.py](../src/robo.py#L17) percorre os registros com for. Na linha 20, if erros registra o item inválido e continue avança o laço. Na linha 25, if chave in primeira_posicao identifica o ID já aceito.
- [src/classificador.py](../src/classificador.py#L11) usa if/elif/else para as prioridades alta, média e baixa. O relatório da execução normal comprova os três caminhos com as prioridades alta, alta, média e baixa.

## Evidências

1. [Execução normal](01_execucao_normal.txt)
2. [Condições e repetições](02_condicoes_repeticoes.txt)
3. [API indisponível e timeout](03_api_indisponivel.txt)
4. [JSON inválido](04_json_invalido.txt)
5. [Registro inválido](05_registro_invalido.txt)
6. [Duplicidade](06_duplicidade.txt)

## Reprodução no PowerShell do VS Code

Use Python 3.10 ou posterior. O bloco cria entradas temporárias fora de dados e mostra o código de saída de cada execução. Os relatórios das execuções bem-sucedidas ficam em dados\saida. Para reproduzir a medição complementar de timeout, use o bloco completo da evidência 03 e substitua o caminho do Python integrado por $py.

~~~powershell
Set-Location -LiteralPath 'C:\RPAGS'
$py = 'python' # Ou '.\.venv\Scripts\python.exe'
$env:PYTHONIOENCODING = 'utf-8'
$env:NO_PROXY = '127.0.0.1'
Remove-Item Env:\ROTA_CONTINGENCIA -ErrorAction SilentlyContinue

# Lote de exemplo
& $py -B .\main.py --arquivo .\dados\obstaculos_exemplo.json
$LASTEXITCODE

# A. Confirme que a porta local 65534 está livre antes de usar.
if (Get-NetTCPConnection -State Listen -LocalPort 65534 -ErrorAction SilentlyContinue) {
    throw 'Escolha outra porta local sem serviço.'
}
& $py -B .\main.py --api-url http://127.0.0.1:65534/obstaculos --timeout 0.5 --tentativas 3 --intervalo 0.2
$LASTEXITCODE

$pasta = Join-Path ([IO.Path]::GetTempPath()) ('rota-livre-' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $pasta

# B. JSON malformado
$arquivo = Join-Path $pasta 'malformado.json'
Set-Content -LiteralPath $arquivo -Value '[{"id":900,}]' -Encoding utf8
Get-FileHash .\dados\obstaculos_exemplo.json
& $py -B .\main.py --arquivo $arquivo
$LASTEXITCODE
Get-FileHash .\dados\obstaculos_exemplo.json

# C. Latitude inválida
$arquivo = Join-Path $pasta 'latitude.json'
$base = @{tipo='Rampa bloqueada'; descricao='Relato de teste'; longitude=-46; status='aberto'}
@(
    ($base + @{id=201; latitude=-23})
    ($base + @{id=202; latitude=91})
    ($base + @{id=203; latitude=-23})
) | ConvertTo-Json | Set-Content -LiteralPath $arquivo -Encoding utf8
& $py -B .\main.py --arquivo $arquivo
$LASTEXITCODE

# D. IDs equivalentes
$arquivo = Join-Path $pasta 'duplicado.json'
@(
    ($base + @{id=101; latitude=-23})
    ($base + @{id=' 101 '; latitude=-23})
) | ConvertTo-Json | Set-Content -LiteralPath $arquivo -Encoding utf8
Get-FileHash -LiteralPath $arquivo
& $py -B .\main.py --arquivo $arquivo
$LASTEXITCODE
Get-FileHash -LiteralPath $arquivo
~~~
