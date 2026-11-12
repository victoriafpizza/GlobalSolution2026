# Índice de evidências da entrega final

**ROTA LIVRE · Victoria Franceschini Pizza · RM 550609 · Engenharia de Software 4ES**  
Secure DevOps Tools & Cloud Computing · FIAP Global Solution CitizenTech 2026.2  
Auditoria executada em **12/11/2026**, horário de Brasília.

A auditoria usa a rubrica de 14 pontos fornecida no enunciado desta missão. A pesquisa pública localizou o projeto pedagógico da FIAP, mas a versão oficial específica da rubrica CitizenTech 2026.2 não foi localizada para conferência independente. Os estados abaixo indicam cobertura por evidência. A atribuição de pontos cabe à FIAP.

**Revisão auditada e publicada** — `65ed7cf7baf3244a124c948cd866627e1090ce18`. O HEAD remoto de `main`, a execução aprovada e o marcador HTTP retornaram esse mesmo SHA. [Commit](https://github.com/victoriafpizza/GlobalSolution2026/commit/65ed7cf7baf3244a124c948cd866627e1090ce18) · [Execução](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43247960515) · [Marcador público](http://3.129.216.178/deploy-revision.txt)

## Evidências na ordem da rubrica

| # | Requisito | Estado | Origem, validação e resultado | Captura ou tela para o PDF | URL |
| --- | --- | --- | --- | --- | --- |
| 1 | Dockerfile seguro | **Concluído** | [API](../backend/dockerfile), [frontend](../frontend/dockerfile) e [hardening](devsecops.md). Builds Linux documentados, `docker exec id` com UID 10001 e 101, Trivy das duas imagens aprovado. Inspeção anterior de histórico e variáveis das imagens sem indícios de segredos. | Sem PNG dedicado. Capturar o job **Docker Build e Trivy** com as etapas de build e UID expandidas. | [Builds e scanners](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43241726597) |
| 2 | Docker Compose | **Concluído** | [Compose da aplicação](../compose.yaml) e [validação do deploy](cicd-observabilidade.md). `docker compose config --quiet` passou nesta auditoria para a aplicação e o monitoramento. O deploy documentado mostrou dois containers saudáveis e integração HTTP 200. | Sem PNG dedicado. Capturar a saída de `docker compose ps` com nomes, saúde e portas. | [Job de deploy final](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43247960515/job/131286044811) |
| 3 | Terraform e infraestrutura AWS | **Concluído** | [IaC](../infra/main.tf), [role SSM](../infra/ssm.tf), [hardening](devsecops.md). `terraform fmt -check -recursive` e `terraform validate` passaram. `plan -detailed-exitcode` retornou 2, com **0 a criar, 1 alteração in-place, 0 a destruir**. AWS CLI confirmou a EC2 t3.small `i-054604c12c64a62e9` em execução em `us-east-2`, Amazon Linux 2023, EBS gp3 criptografado e IMDSv2 obrigatório. A alteração de user data segue pendente. | Sem PNG dedicado. Capturar **EC2 → Instances → Details** com ID, região e estado, ou a saída reduzida de `describe-instances` e a linha de resumo do plano. | [Aplicação na EC2](http://3.129.216.178/) |
| 4 | Proteção do state e `.tfvars` | **Concluído** | [Regras de ignore](../../.gitignore), [backend local](../infra/versions.tf), [proteção e recuperação](devsecops.md). `git check-ignore` confirmou state, backup, `.tfvars`, `.env`, credenciais e segredo Grafana. Índice e histórico por nome tiveram zero ocorrências. ACLs NTFS confirmadas. | Sem PNG dedicado. Capturar apenas a saída de `git check-ignore -v` e o total de entradas do índice. | — |
| 5 | Portas administrativas restritas | **Concluído** | [Rede Terraform](../infra/main.tf), [portas do Compose](../compose.yaml). `describe-security-group-rules` confirmou uma única entrada pública, TCP 80 IPv4. A API escuta no loopback do host para o SSM, e a solicitação pública a `/metrics` retornou HTML da SPA sem métricas. | Sem PNG dedicado. Capturar **EC2 → Security Groups → Inbound rules** do grupo `sg-0e3859dfb4cb4b357` com a única regra HTTP. | [Frontend público](http://3.129.216.178/) |
| 6 | GitHub Actions | **Concluído** | [Workflow](../../.github/workflows/devsecops.yml). Gatilhos de push, pull request e manual. API do GitHub confirmou build, Gitleaks, Semgrep e Trivy de API e frontend aprovados no push do SHA publicado. Gitleaks local revisou 13 commits sem detectar vazamentos. | Sem PNG dedicado. Capturar a página **Summary** da execução final com os cinco jobs e o SHA. | [Execução final](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43247960515) |
| 7 | GitHub Secrets/Variables e deploy automático | **Parcial** | [CI/CD](cicd-observabilidade.md), [workflow](../../.github/workflows/devsecops.yml), [verificador na EC2](../infra/release_gate.py). Deploy `verified-pull` concluído e confirmado pela igualdade dos SHAs. Quatro Variables e ambiente restrito a `main`. Zero Secrets personalizados de repositório ou ambiente. A política AWS bloqueia a opção OIDC/SSM direta. | Sem PNG dedicado. Capturar o job **Deploy - EC2** com a validação do SHA e HTTP, e a tela do environment com a regra de branch `main`. Ao apresentar Variables, mostrar somente os nomes. | [Deploy final](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43247960515/job/131286044811) · [Variables](https://github.com/victoriafpizza/GlobalSolution2026/settings/variables/actions) |
| 8 | Execução reprovada | **Concluído** | [Relatório DevSecOps](devsecops.md). API do GitHub confirmou `failure` na etapa Trivy da API no commit `bc5e914`, com os dois builds aprovados e o scan frontend pulado. O relatório preserva a comparação local de CVEs. | Sem PNG dedicado. Capturar **Docker Build e Trivy** da execução histórica, com a falha do Trivy da API e o status `skipped` do frontend. | [Job reprovado](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43225822068/job/131208600599) |
| 9 | Execução corrigida | **Concluído** | [Relatório DevSecOps](devsecops.md). API do GitHub confirmou `success` para os quatro jobs do commit `d442466`, incluindo os dois scans Trivy. Na comparação local anterior, a API passou de 54 HIGH a 0, e o frontend de 12 HIGH e 1 CRITICAL a 0. | Sem PNG dedicado. Capturar **Summary** da execução corrigida, mostrando as duas variantes da matriz em verde. | [Execução corrigida](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43241726597) |
| 10 | Dashboard das quatro métricas | **Concluído** | [Dashboard JSON](../monitoring/grafana/dashboards/rota-livre.json), [Prometheus](../monitoring/prometheus/prometheus.yml) e [dados do teste](cicd-observabilidade.md). JSON válido, quatro painéis, target AWS `UP` e datasource Grafana `OK`. Amostra via Grafana da EC2 de 4,70 ms P95, 0,0946 req/s, 0 req/s de 5xx e 13,49% de memória. | [Grafana com dados AWS](observabilidade-aws.png) · [Réplica local](observabilidade-local.png). A captura AWS é de uma coleta posterior e tem valores ligeiramente diferentes. | [Grafana local](http://127.0.0.1:3000/d/rota-livre-devsecops) |
| 11 | Alerta disparado | **Concluído** | [Regra](../monitoring/prometheus/availability.yml) e [registro de teste](cicd-observabilidade.md). O Prometheus registrou `pending → firing → inactive` em uma **réplica local**. A consulta atual retornou regra `inactive`, saúde `ok` e target AWS `UP`. | [Prometheus em FIRING](alerta-local.png) | [Alertas locais](http://127.0.0.1:9090/alerts) |
| 12 | URL pública | **Concluído** | `Invoke-WebRequest` retornou HTTP 200 no frontend e na API. O JSON retornou dois obstáculos. O IP coincide com o inventário da EC2. O HTTP público opera sem TLS. | Sem PNG dedicado. Capturar o mapa aberto no navegador com o endereço visível. Para a API, capturar a resposta de `GET /api/obstacles` com status HTTP 200. | [Mapa](http://3.129.216.178/) · [API](http://3.129.216.178/api/obstacles) |
| 13 | Diagrama de arquitetura | **Concluído** | [Descrição e Mermaid](../docs/arquitetura/arquitetura.md) · [Fonte](../docs/arquitetura/arquitetura.mmd). Conferir os fluxos com o Compose, o workflow, o verificador da EC2, o túnel SSM e os recursos AWS inventariados. | [Diagrama vetorial para o PDF](../docs/arquitetura/arquitetura.svg) | — |
| 14 | Matriz de responsabilidade | **Concluído** | [Matriz](../docs/governanca/responsabilidade-compartilhada.md), revisada com o modelo da AWS e os controles confirmados neste índice. | Usar a tabela do documento. | [Modelo AWS](https://aws.amazon.com/compliance/shared-responsibility-model/) |
| 15 | LGPD | **Concluído** | [Análise](../docs/governanca/lgpd.md), confrontada com o código e as fontes oficiais. Documenta obstáculos de exemplo, metadados técnicos, Ohio, serviços externos do mapa, HTTP público e requisitos para tratamentos futuros. | Usar a análise como fonte textual. | [Lei nº 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm) |
| 16 | Estimativa de custos | **Concluído** | [Estimativa AWS](../docs/custos/estimativa-aws.md), com catálogo oficial, fórmula, região, hipóteses e itens variáveis. Base sob demanda de **USD 20,18 por 30 dias**, antes de créditos, impostos e excedentes. | Usar a tabela de preços e o cenário-base. | [Preços EC2](https://aws.amazon.com/ec2/pricing/on-demand/) |
| 17 | README reproduzível | **Pendente** | [README atual](../../README.md) descreve RPA. As instruções de monitoramento e o roteiro abaixo são material de origem para o README acadêmico desta disciplina. | Na entrega, vincular o README acadêmico concluído. | [Repositório público](https://github.com/victoriafpizza/GlobalSolution2026) |
| 18 | Repositório público | **Concluído** | API do GitHub retornou `visibility=public`. O branch remoto `main` coincide com a execução aprovada e o SHA público auditado. | Sem PNG dedicado. Capturar a página **Code** com a indicação **Public** e a branch `main`. | [GitHub](https://github.com/victoriafpizza/GlobalSolution2026) |

## Registro da auditoria técnica

### Segurança, IAM e state

- O grupo `sg-0e3859dfb4cb4b357` admite TCP 80 de `0.0.0.0/0` e tem saída IPv4 ampla. O SSM estava `Online`. A role `rota-livre-ec2-ssm` confia no principal de serviço `ec2.amazonaws.com` e tem uma política gerenciada anexada, `AmazonSSMManagedInstanceCore`, sem políticas inline. As permissões de operadores fora dessa role não fazem parte dessa verificação.
- O disco AWS é gp3 de 20 GiB, criptografado, com 3.000 IOPS e 125 MiB/s. O backend Terraform é local. Em `.terraform-state/`, cada ACL verificada contém somente a identidade local operacional, SYSTEM e Administradores locais. O arquivo `pre-migracao-terraform.tfstate.backup` tem conteúdo e coincide byte a byte com o state ativo. O arquivo legado `pre-migracao-terraform.tfstate` tem zero bytes. A verificação do BitLocker retornou acesso negado, e a existência de uma cópia independente da máquina segue sem confirmação.
- O plano registrou uma atualização in-place já conhecida de user data, com IP futuro computado pelo provider. A execução encerrou após o plano, preservando o IP e a instância em produção.
- `git ls-files -ci --exclude-standard` não retornou itens. A busca por nomes de state, tfvars, env e credenciais em `git log --all --name-only` retornou zero ocorrências. Gitleaks 8.30.1 com `--redact` retornou 0 e examinou 13 commits. A checagem confirma o resultado das regras aplicadas, dentro do alcance do scanner.

### Variables, Secrets e autorização do deploy

| Configuração auditada | Resultado |
| --- | --- |
| Nomes das GitHub Variables | `AWS_DEPLOY_AUTH`, `AWS_REGION`, `EC2_INSTANCE_ID`, `ROTA_LIVRE_PUBLIC_URL` |
| Secrets personalizados do repositório | Lista vazia |
| Secrets personalizados de `rota-livre-production` | Lista vazia |
| Regra de deploy do environment | Tipo branch, nome `main` |

O workflow fornece ao checkout o `GITHUB_TOKEN` temporário da própria execução. A EC2 consulta a API pública do GitHub por HTTPS e verifica SHA, branch, evento de push, aprovação dos quatro jobs e presença do job de deploy ativo. O script de publicação verifica novamente a referência de `main`. Esse transporte dispensa chaves AWS permanentes no GitHub. A modalidade OIDC e documento SSM restrito está prevista no Terraform, desativada. O simulador IAM da etapa anterior registrou `explicitDeny` pela política organizacional para criação/consulta do provedor e criação do documento SSM. Se a FIAP interpretar o item como exigência literal de um Secret personalizado, registrar essa ressalva acadêmica. [Validação e política documentadas](cicd-observabilidade.md)

### Rastreabilidade das capturas de observabilidade

| Arquivo | Conteúdo conferido | SHA-256 |
| --- | --- | --- |
| [observabilidade-aws.png](observabilidade-aws.png) | Quatro painéis com valores visíveis. Na captura, 4,72 ms, 0,0979 req/s em obstáculos, 0 req/s de 5xx e 13,5% de memória. | `6ce5749d67833b785673b9b326df6a33561dbbb02b79490d7cd8cc8eaa131f92` |
| [alerta-local.png](alerta-local.png) | Interface real de alertas do Prometheus com `RotaLivreAPIScrapeUnavailable` em **FIRING (1)**. | `a06087c1e7ebbb1d1a99afa27364d6b6fce8669e8dae617314dae5c0877ed003` |
| [observabilidade-local.png](observabilidade-local.png) | Captura da réplica local, preservada como evidência adicional do teste. | `240c38460cc16b8d8330e3fdb6afcc5e68a5fb82d03e7fcbbcb7cc8caf125957` |

No JSON, as unidades são segundos para P95, req/s para tráfego e 5xx e razão convertida em percentual para saturação. O alvo observado foi `host.docker.internal:19091/metrics` com rótulo `source=aws`. O teste de produção coletou métricas pelo SSM e preservou a disponibilidade da aplicação durante a auditoria. A validação do alerta reaproveitou o disparo real já documentado. [Alvo local](http://127.0.0.1:9090/targets) · [Grafana local](http://127.0.0.1:3000/d/rota-livre-devsecops)

## Auditoria da rubrica de 14 pontos

| Requisito | Status | Evidência | Pendência |
| --- | --- | --- | --- |
| Containerização e infraestrutura — até 5 pontos | **Concluído** | Itens 1–5. Dockerfiles, Compose, Terraform, state e rede verificados. | A atualização de user data ficou no plano. Criptografia do disco Windows e cópia independente do state seguem sem confirmação. |
| CI/CD e segurança — até 4 pontos | **Parcial** | Itens 6–9. Scanners, execução reprovada/corrigida e deploy automático comprovados. | Ressalva acadêmica de Secret personalizado. A opção direta OIDC/SSM depende da organização AWS. |
| Observabilidade — até 3 pontos | **Concluído** | Itens 10–11. Quatro métricas da EC2 e alerta real em réplica local. | Para visualizar dados ao vivo, a estação precisa manter o túnel SSM aberto. |
| Documentação — até 2 pontos | **Parcial** | Itens 12–18. Arquitetura, matriz, LGPD, custos, capturas e links reunidos. | README acadêmico e PDF técnico pertencem à etapa de entrega posterior. |

## Roteiro para quem elaborar o README e o PDF

1. Use a revisão `65ed7cf` como referência da aplicação auditada. No README, inclua propósito, arquitetura, requisitos locais, URLs e os comandos de reprodução. O [README de monitoramento](../monitoring/README.md) explica a senha local ignorada pelo Git, o Compose e a abertura do túnel SSM. Para a auditoria atual, a porta 9091 da EC2 foi encaminhada para a porta local 19091 e o target local foi ajustado.
2. No PDF, siga a ordem dos 18 itens e use o SVG de arquitetura como figura vetorial. Insira as duas capturas reais, com legendas que identifiquem **dados da EC2** no Grafana e **disparo em réplica local** no Prometheus. Use os links da execução reprovada, corrigida e publicada para permitir conferência. As telas sugeridas nas linhas sem captura são material opcional de apresentação.
3. Inclua a matriz, a análise LGPD e a estimativa com as fontes, a data de referência e as exclusões. Identifique o HTTP sem TLS, o escopo de verificação do state e a restrição OIDC/SSM na seção de limitações. Compare com a versão da rubrica disponível no portal da disciplina antes de atribuir pontos.
4. Na raiz do repositório, use os comandos abaixo para reproduzir a aplicação local. A porta 9091 do host atende à coleta da réplica. Para coletar da EC2, utilize o túnel e evite que os dois processos disputem a mesma porta local. O README de monitoramento documenta o override do arquivo de targets.

```powershell
docker compose -f ROTA-LIVRE/compose.yaml config --quiet
docker compose -f ROTA-LIVRE/compose.yaml up -d --build --wait
docker compose -f ROTA-LIVRE/compose.yaml ps
Invoke-RestMethod http://127.0.0.1:8080/api/obstacles
terraform -chdir=ROTA-LIVRE/infra fmt -check -recursive
terraform -chdir=ROTA-LIVRE/infra validate
```

O plano sobre a infraestrutura existente exige o perfil autorizado `rota-livre` e o backend local protegido já inicializado na estação operacional. Para o material acadêmico, use o resumo do plano e os metadados de inventário. Mantenha o conteúdo do state e as credenciais restritos à estação.
