# ROTA LIVRE — CI/CD e observabilidade

Validação de 12/11/2026 para a FIAP CitizenTech 2026.2. As evidências de hardening e da primeira correção do pipeline estão em [DevSecOps](devsecops.md).

## Deploy automático após aprovação

```text
push em main → Gitleaks + Semgrep + build/Trivy API e frontend → Deploy - EC2
                                         ↑                            ↓
                                 GitHub Actions API            verifica SHA e HTTP
                                         ↑                            ↓
EC2 existente → serviço systemd verifica SHA, execução e jobs → Docker Compose
```

A conta AWS recusou consultas ao provedor OIDC. O IAM Policy Simulator retornou `explicitDeny` pela política da organização para `iam:CreateOpenIDConnectProvider`, `iam:GetOpenIDConnectProvider` e `ssm:CreateDocument`. A revisão automática também rejeitou a tentativa de criar o provedor antes do envio à AWS por exigir autorização explícita para a mudança de confiança da conta. O Terraform contém a opção OIDC/SSM desativada, validada com `terraform validate`. Quando habilitada em uma conta que permita essas operações, a role confia na audiência AWS STS e no subject imutável do environment do repositório. `ssm:SendCommand` fica limitado ao documento `RotaLivre-Deploy` e à EC2 existente. `ssm:GetCommandInvocation` permite consultar o resultado, pois a AWS não oferece escopo por recurso para essa ação. [OIDC na AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws) · [Permissões SSM](https://docs.aws.amazon.com/service-authorization/latest/reference/list_ssm.html)

A configuração ativa usa `verified-pull`. Um timer na EC2 consulta a referência `main` e a API pública do GitHub por HTTPS. O serviço aceita apenas execução por push do workflow `devsecops.yml`, com SHA idêntico ao HEAD, quatro jobs obrigatórios aprovados na mesma tentativa e job de deploy em execução. O Run Command `5060106a-9a14-4f21-ae33-abc03af7c10a` instalou o executor e o timer. O processo de publicação usa o timer e o job do GitHub. O Run Command foi usado para instalar a automação.

O environment `rota-livre-production` aceita somente a branch `main`. As GitHub Variables configuradas são `AWS_DEPLOY_AUTH`, `AWS_REGION`, `EC2_INSTANCE_ID` e `ROTA_LIVRE_PUBLIC_URL`. A região e a instância são metadados operacionais e também alimentam a opção OIDC. O ARN só é necessário na opção OIDC. O checkout continua usando o `GITHUB_TOKEN` temporário fornecido pelo GitHub Actions. O transporte ativo consulta metadados públicos por HTTPS e dispensa credenciais AWS ou secrets personalizados no GitHub. [Variables](https://github.com/victoriafpizza/GlobalSolution2026/settings/variables/actions) · [Environment](https://github.com/victoriafpizza/GlobalSolution2026/settings/environments)

O executor extrai o SHA validado, monta as imagens antes de trocar os containers e usa um lock do host além da concorrência do workflow. A imagem da API pode ser reutilizada quando sua árvore de código não muda. O frontend inclui o SHA em `/deploy-revision.txt`. Uma falha na troca ou no teste de saúde aciona a recuperação pela configuração e pelos IDs das imagens anteriores. A troca usa o projeto Compose existente e preserva a mesma instância e o IP. O job compara o SHA publicado e verifica as respostas HTTP do frontend e da API. O endpoint público do projeto usa HTTP.

Validações pré-publicação executadas: `actionlint`, `bash -n`, ShellCheck, cinco cenários de aceite e rejeição da barreira, e recuperação isolada por ID de imagem com os dois serviços saudáveis e HTTP 200. [Workflow](../../.github/workflows/devsecops.yml) · [Barreira](../infra/release_gate.py) · [Executor](../infra/deploy.sh) · [Terraform OIDC opcional](../infra/github_oidc.tf)

**Publicação automática comprovada.** O push de `1968d1a76bbd6e72b7d30b36d1895fff44f90fd3` para `main` disparou a execução `43247199380`, tentativa 1. Gitleaks, Semgrep, build/Trivy da API e do frontend e o job `Deploy - EC2` terminaram com sucesso. O teste de instrumentação também passou no job da API. O journal da instância registrou as linhas abaixo, confirmadas por uma consulta de diagnóstico SSM `e45d063f-8026-4542-8741-2df43086ff55`.

```text
ROTA_LIVRE_RELEASE_GATE run=43247199380 attempt=1 commit=1968d1a76bbd6e72b7d30b36d1895fff44f90fd3
ROTA_LIVRE_DEPLOY_OK 1968d1a76bbd6e72b7d30b36d1895fff44f90fd3
```

O job e a consulta externa confirmaram o marcador do SHA, frontend HTTP 200 e API HTTP 200 com dois obstáculos. A EC2 `i-054604c12c64a62e9` manteve o IP `3.129.216.178` e somente TCP 80 de entrada pública no Security Group. A consulta capturou a fase de recriação do Compose antes de o frontend voltar a ficar saudável. A verificação final mostrou os dois containers saudáveis e o listener de métricas restrito ao loopback. [Execução aprovada](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43247199380) · [Job de deploy](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43247199380/job/131283340127) · [Commit](https://github.com/victoriafpizza/GlobalSolution2026/commit/1968d1a76bbd6e72b7d30b36d1895fff44f90fd3)

## Dashboard e coleta

A FastAPI expõe `/metrics` na rede interna. O Compose disponibiliza o listener de coleta somente no loopback em `127.0.0.1:9091`. O acesso à EC2 usa o túnel autenticado pelo AWS Systems Manager. Prometheus e Grafana rodam na estação em `127.0.0.1:9090` e `127.0.0.1:3000`. A medição local de memória mostrou 37,79 MiB no Prometheus e 328,3 MiB no Grafana. Mantive esses serviços fora da EC2 de 2 GiB. O Grafana usa uma senha inicial em arquivo local ignorado pelo Git.

O contador registra método conhecido, rota cadastrada e classe HTTP. Rotas desconhecidas usam o rótulo `unmatched`. O histograma mede a duração com relógio monotônico. A saturação divide o uso real de memória do cgroup v2 pelo limite de 256 MiB da API. Os endpoints `/health` e `/api/obstacles` preservam o contrato.

| Painel | PromQL | Verificação local |
| --- | --- | --- |
| Latência P95 | `histogram_quantile(0.95, sum by (le) (rate(rota_livre_http_request_duration_seconds_bucket{job="rota-livre-api"}[5m])))` | 2,27 ms na consulta ao datasource do Grafana |
| Tráfego | `sum by (method, route) (rate(rota_livre_http_requests_total{job="rota-livre-api"}[5m]))` | 20 requisições 2xx controladas fizeram o contador de obstáculos avançar de 1 para 21. A série registrou cerca de 0,086 req/s |
| Erros | `sum(rate(rota_livre_http_requests_total{job="rota-livre-api",status_class="5xx"}[5m]))` | 0 req/s na réplica saudável. Em um teste separado, uma rota injetada somente no processo isolado retornou HTTP 500 e elevou o contador 5xx para 1 |
| Saturação | `rota_livre_container_memory_usage_ratio{job="rota-livre-api"}` | 13,93% de memória na consulta ao datasource do Grafana |

`promtool check config`, a saúde do datasource, o target `UP` e o provisionamento dos quatro painéis foram confirmados. Os três testes unitários da instrumentação passaram. O Trivy retornou saída 0 para a imagem instrumentada da API. [Captura real do Grafana](observabilidade-local.png) · [Dashboard JSON](../monitoring/grafana/dashboards/rota-livre.json) · [Configuração Prometheus](../monitoring/prometheus/prometheus.yml) · [Dashboard local](http://127.0.0.1:3000/d/rota-livre-devsecops)

### Medições da EC2 pelo túnel SSM

O túnel autenticado encaminhou a porta local 19091 para o loopback 9091 da EC2. `GET /metrics` pelo túnel retornou HTTP 200 com métricas Prometheus. Pelo endereço público, `/metrics` serviu HTML do frontend sem métricas. A instância local de Prometheus usada nesta validação tinha histórico separado da réplica e mostrou `host.docker.internal:19091/metrics` como `UP`, com rótulo `source=aws`. O Grafana retornou datasource `OK` e quatro painéis provisionados.

Vinte requisições de verificação ao endpoint público elevaram o contador de sucessos de 3 para 23. As consultas feitas pelo datasource do Grafana retornaram **4,70 ms** de P95, **0,0946 req/s** em `GET /api/obstacles`, **0 req/s** de 5xx e **13,49%** do limite de memória do container. A captura foi feita após outra coleta e mostra a variação dos valores. [Captura real com métricas da AWS](observabilidade-aws.png)

## Alerta

`RotaLivreAPIScrapeUnavailable` verifica `up{job="rota-livre-api"} == 0` por 30 segundos. A regra cobre o caminho de coleta, incluindo API e túnel. O teste interrompeu apenas o container da réplica isolada. O Prometheus registrou `pending` às 12:18:04 e `firing` às 12:18:34, com valor 0. Após reiniciar a réplica, a coleta voltou a `UP` e o alerta a inativo às 12:20:13, horário de Brasília. [Captura do disparo](alerta-local.png) [Regra](../monitoring/prometheus/availability.yml) · [Alertas locais](http://127.0.0.1:9090/alerts)

## Reprodução

1. Siga o [README de monitoramento](../monitoring/README.md) para configurar a senha local, subir Prometheus e Grafana e abrir o túnel SSM. O mesmo README documenta a coleta usando uma réplica local.
2. Confira o environment restrito a `main` e as Variables do projeto. Para reprovisionar o executor, instale `deploy.sh` como `/usr/local/sbin/rota-livre-deploy` e `release_gate.py` como `/usr/local/libexec/rota-livre-release-gate.py`, sob propriedade de root. Instale os dois arquivos de unidade em `/etc/systemd/system/`, execute `systemctl daemon-reload` e `systemctl enable --now rota-livre-release-gate.timer` na EC2 existente por um operador autorizado do SSM.
3. Envie um commit autorizado a `main`. Acompanhe `Deploy - EC2` depois dos quatro jobs de segurança. Na EC2, `journalctl -u rota-livre-release-gate.service` registra execução, tentativa e SHA. `/opt/rota-livre-deploy/current` registra o último deploy bem-sucedido. Consulte também o marcador público e a API. [GitHub Actions](https://github.com/victoriafpizza/GlobalSolution2026/actions) · [Revisão pública](http://3.129.216.178/deploy-revision.txt) · [Frontend](http://3.129.216.178/) · [API](http://3.129.216.178/api/obstacles)
