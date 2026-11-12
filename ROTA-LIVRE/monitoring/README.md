# Observabilidade do ROTA LIVRE

O Prometheus e o Grafana rodam na estação local. Na EC2 de 2 GiB, apenas a API expõe métricas em um listener de loopback. O Security Group continua com a porta HTTP pública para o frontend. O túnel autenticado pelo AWS Systems Manager leva as métricas à estação sem reservar memória para os dois servidores de monitoramento na instância.

```text
FastAPI /metrics → EC2 127.0.0.1:9091 → túnel SSM → estação 127.0.0.1:9091
                                                       ↓
                                              Prometheus → Grafana
```

## Iniciar na estação

Na raiz do repositório, crie a senha inicial do Grafana em arquivo local ignorado pelo Git. Reutilize o arquivo e o volume nas próximas execuções.

```powershell
$secretDir = 'ROTA-LIVRE/monitoring/secrets'
New-Item -ItemType Directory -Path $secretDir -Force | Out-Null
$passwordFile = Join-Path (Resolve-Path $secretDir).Path 'grafana-admin-password'
if (-not (Test-Path -LiteralPath $passwordFile)) {
    $passwordBytes = [byte[]]::new(24)
    [Security.Cryptography.RandomNumberGenerator]::Fill($passwordBytes)
    [IO.File]::WriteAllText($passwordFile, [Convert]::ToHexString($passwordBytes))
}

docker compose -f ROTA-LIVRE/monitoring/compose.yaml config --quiet
docker compose -f ROTA-LIVRE/monitoring/compose.yaml up -d
```

Acesse o Grafana com o usuário `admin` e a senha do arquivo. O Compose monta o segredo em modo somente leitura, e a senha inicial é aplicada na criação do banco local do Grafana. [Dashboard local](http://127.0.0.1:3000/d/rota-livre-devsecops) · [Targets do Prometheus](http://127.0.0.1:9090/targets)

## Coletar métricas da EC2

Em um terminal separado com AWS CLI, plugin do Session Manager e perfil `rota-livre` autenticado, mantenha o túnel aberto. A porta local 9091 deve estar disponível. Use o ID atual de `terraform output -raw instance_id`.

```powershell
$instanceId = terraform -chdir=ROTA-LIVRE/infra output -raw instance_id
aws ssm start-session --profile rota-livre --region us-east-2 --target $instanceId --document-name AWS-StartPortForwardingSession --parameters 'portNumber=9091,localPortNumber=9091'
```

No Docker Desktop, o target padrão é `host.docker.internal:9091`. Para outro endpoint acessível ao container, defina `ROTA_LIVRE_PROMETHEUS_TARGETS_FILE` com o caminho de um arquivo no formato de [targets.yml](prometheus/targets.yml) e execute o Compose com `up -d`. [Guia do túnel SSM](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html) · [Rede do Docker Desktop](https://docs.docker.com/desktop/features/networking/networking-how-tos/)

Para coletar métricas de uma réplica local, inicie a aplicação com `docker compose -f ROTA-LIVRE/compose.yaml up -d --build --wait` e use o mesmo target. A réplica e o túnel usam a mesma porta local. Encerre a origem anterior antes de alternar e registre a origem ao comparar resultados, pois o histórico local usa o mesmo rótulo de instância.

## Verificar coleta e alerta

1. Abra o Prometheus e confirme que `rota-livre-api` aparece como **UP**. O endpoint de coleta é `http://127.0.0.1:9091/metrics` na estação.
2. Faça algumas requisições a `/api/obstacles` no frontend correspondente. Aguarde pelo menos duas coletas de 10 segundos e abra o dashboard. Uma série de erros em zero representa ausência de 5xx na janela. Painéis sem dados indicam falta de amostras.
3. O alerta `RotaLivreAPIScrapeUnavailable` muda para **FIRING** se o Prometheus perder o acesso ao target por 30 segundos. Para o teste controlado, encerre o túnel SSM ou pare apenas a réplica de teste. Reabra o túnel ou inicie a réplica e confira o retorno a **Inactive**. A regra monitora o caminho de coleta, que inclui a API e o túnel. O estado fica disponível na interface do Prometheus, sem envio para destinatários externos. [Alertas do Prometheus](http://127.0.0.1:9090/alerts)

| Painel | Fonte e unidade |
| --- | --- |
| Latência HTTP P95 | Histograma de duração em segundos |
| Tráfego HTTP por rota | Contador de requisições, taxa por segundo |
| Erros HTTP 5xx | Contador com classe 5xx, taxa por segundo |
| Saturação de memória do container | Memória usada dividida pelo limite do cgroup da API, em percentual |

As consultas PromQL estão no [dashboard provisionado](grafana/dashboards/rota-livre.json). Para desligar o monitoramento local preservando o histórico, execute `docker compose -f ROTA-LIVRE/monitoring/compose.yaml down`.
