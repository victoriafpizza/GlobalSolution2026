# ROTA LIVRE — evidências DevSecOps

Validação em 12/11/2026, horário de Brasília. Projeto FIAP CitizenTech 2026.2, Engenharia de Software 4ES.

## 1. Imagens e aplicação local

Os dois builds Linux passaram com `docker build --pull -f ROTA-LIVRE/<contexto>/dockerfile -t rota-livre-<contexto>:devsecops ROTA-LIVRE/<contexto>`, para os contextos `backend` e `frontend`.

| Imagem construída | ID do manifesto local | Usuário efetivo | Tamanho informado pelo Docker |
| --- | --- | --- | --- |
| API | `sha256:ffb200a46f94c21997f8db86484709113cdec35dcacb836ae99c75c07c8a9bf7` | UID 10001, GID 10001 | 22.853.714 bytes |
| Frontend | `sha256:bce1e67d6b929c18756235c828dfbb0a713649ee32a5e5d0a6776e9cc526314c` | UID 101, GID 101 | 28.137.258 bytes |

- A API passou a usar Python 3.13 Alpine com atualizações de pacotes, instalação apenas de wheels e `pip check` sem dependências quebradas. O build remove o instalador pip do ambiente de execução.
- O frontend mantém Node 24 Alpine no estágio de build e Nginx unprivileged Alpine no runtime. `npm ci` informou zero vulnerabilidades e o Vite compilou 2.102 módulos.
- Os Dockerfiles copiam caminhos explícitos e os `.dockerignore` restringem o contexto. O Compose remove capabilities e habilita `no-new-privileges` nos dois serviços, com filesystem somente leitura na API.
- `docker compose config --quiet` e `docker compose up --wait` passaram em um projeto isolado na porta local 18080, usando as imagens da tabela. `docker compose ps` mostrou os dois serviços saudáveis. `docker exec <container> id` confirmou os UIDs da tabela. `GET /` retornou HTTP 200 com o ponto de montagem do React, e `GET /api/obstacles` retornou HTTP 200 via Nginx com os dois obstáculos. A API usa somente a rede interna.
- `docker image inspect` e `docker history --no-trunc` retornaram zero indicadores de credenciais no ambiente e nas instruções de build, segundo os padrões verificados. A varredura Trivy de todas as severidades também retornou zero segredos detectados nas duas imagens.

Reprodução local pelo Compose, com a porta padrão 8080 disponível.

```sh
docker compose -f ROTA-LIVRE/compose.yaml config --quiet
docker compose -f ROTA-LIVRE/compose.yaml up -d --build --wait
docker compose -f ROTA-LIVRE/compose.yaml ps
docker compose -f ROTA-LIVRE/compose.yaml exec api id
docker compose -f ROTA-LIVRE/compose.yaml exec frontend id
curl -fsS http://127.0.0.1:8080/
curl -fsS http://127.0.0.1:8080/api/obstacles
```

## 2. Terraform e AWS

O Terraform usa `us-east-2` e o perfil local `rota-livre`. A consulta autenticada por AWS CLI retornou a EC2 `i-054604c12c64a62e9` em execução, tipo `t3.small`, IP `3.129.216.178`, IMDSv2 obrigatório e status de sistema e instância `ok`. O volume gp3 de 20 GiB está criptografado. A VPC padrão é `vpc-0c142748889d4b534`, a subnet é `subnet-0c01583f0ec97c087` e o security group é `sg-0e3859dfb4cb4b357`. A única regra de entrada observada foi TCP 80 em `0.0.0.0/0`. O refresh confirmou o perfil IAM `rota-livre-instance-profile`, a role `rota-livre-ec2-ssm` e a associação `AmazonSSMManagedInstanceCore`. O SSM retornou `Online`.

- O diagnóstico SSM `36b11b1d-c5ce-4e6a-9487-9be864491a1e` confirmou `Exec format error` em `part-001` durante `scripts-user`. O shell falhou antes da instalação do Docker. O bootstrap corrigido usa shebang na primeira linha, LF e UTF-8 sem BOM. O Terraform valida o cabeçalho e mantém proteção contra destruição da EC2. O script verifica o SHA-256 dos binários do Compose e Buildx e testa a API após o deploy.
- `terraform fmt -check -recursive`, `terraform validate`, `terraform state list` e `terraform plan -input=false -lock-timeout=10s` são os comandos de verificação. O plano da revisão prevê zero criações, uma atualização de user data e zero destruições. A atualização de user data pode exigir stop/start pelo provider e o cloud-init executa `scripts-user` uma vez por instância. A recuperação operacional usa SSM na EC2 existente.
- `git ls-files -ci --exclude-standard` e a busca por nomes sensíveis em `git log --all --name-only` não retornaram arquivos sensíveis rastreados. `git check-ignore -v` confirmou regras para state, backup, tfvars, `.env`, credenciais e `.npmrc`.

### Recuperação na instância existente

O Run Command `a83f1af5-4ad1-46d0-9db1-44d2f805f575` terminou com `Success`, código 0 e marcador `ROTA_LIVRE_BOOTSTRAP_CONCLUIDO`. Ambos os serviços ficaram saudáveis. A recuperação usou o commit base `bc5e914` e os arquivos locais testados em uma cópia de deploy na EC2. As tentativas anteriores expuseram um erro no argumento do checksum e a versão insuficiente do Buildx; a execução bem-sucedida usou o checksum verificado, Buildx v0.39.0 e caminho explícito para os plugins da sessão SSM.

Da estação local, três requisições externas retornaram HTTP 200 para o HTML, o JavaScript compilado e `/api/obstacles`. A API retornou dois obstáculos. Uma nova consulta AWS confirmou o mesmo ID, IP e estado `running`. O plano de alteração do user data ficou sem aplicação. [Aplicação pública](http://3.129.216.178/), [API pública](http://3.129.216.178/api/obstacles)


### Armazenamento e recuperação do state

O backend `local` aponta para `ROTA-LIVRE/infra/.terraform-state/terraform.tfstate`. A pasta está ignorada pelo Git e as ACLs NTFS verificadas permitem acesso ao proprietário operacional, SYSTEM e administradores locais. `terraform init -migrate-state -force-copy -input=false` preservou lineage e serial. O backup anterior foi preservado na pasta protegida. A criptografia do volume Windows e a existência de cópia independente da máquina não foram verificadas. Nenhum backend pago foi criado.

Para recuperação, use uma cópia íntegra do state em armazenamento criptografado aprovado, sob acesso restrito. Pare operações concorrentes, preserve a cópia atual, restaure a versão com lineage e serial conferidos no caminho do backend e execute `terraform init`, `terraform state list` e `terraform plan`. Em uma estação nova, configure as ACLs da pasta antes de restaurar. Se o plano apresentar criações ou destruições inesperadas, investigue o state e as credenciais antes de aplicar. Uma cópia cifrada fora desta máquina protege contra perda do disco.

## 3. GitHub Actions e scanners

O workflow dispara em `push`, `pull_request` e `workflow_dispatch`, com `contents: read` e checkout sem persistência do token. A matriz constrói e analisa as duas imagens de forma independente com `fail-fast: false`. Cada job mede o UID e o Trivy falha se detectar HIGH ou CRITICAL. O workflow usa referências imutáveis para as Actions e as imagens de Gitleaks e Semgrep.

| Validação local | Resultado |
| --- | --- |
| actionlint 1.7.12 | Workflow válido, saída 0 |
| Gitleaks 8.30.1, `git --redact` e `dir --redact` | Histórico e arquivos publicáveis sem vazamentos detectados |
| Semgrep 1.185.0, `scan --config p/default --error --metrics=off` | 448 regras executadas, 10 arquivos, zero achados |
| Trivy 0.76.2, `image --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1` | Ambas as imagens novas retornaram saída 0 |

## 4. Reprovação e comparação

A execução histórica por push `43225822068`, commit `bc5e9144b5ccbf6a1b0bfb498daead83865c81b2`, terminou em falha. Os metadados do GitHub registraram sucesso no Gitleaks, Semgrep, validação do Compose e nos dois builds. A etapa Trivy da API falhou e a etapa Trivy do frontend foi pulada. A API pública do GitHub retornou 403 para baixar os logs completos. [Execução reprovada](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43225822068), [job Docker e Trivy](https://github.com/victoriafpizza/GlobalSolution2026/actions/runs/43225822068/job/131208600599)

A comparação abaixo usa as imagens anteriores já presentes no Docker Desktop e as imagens reconstruídas, com a mesma base local do Trivy baixada em 12/11/2026.

| Alvo | Antes HIGH | Antes CRITICAL | Depois HIGH | Depois CRITICAL |
| --- | ---: | ---: | ---: | ---: |
| API, sistema operacional | 49 | 0 | 0 | 0 |
| API, dependências Python | 5 | 0 | 0 | 0 |
| Frontend, sistema operacional | 12 | 1 | 0 | 0 |

A API migrou de Debian para Alpine e atualizou FastAPI 0.115.12 → 0.162.2 e Uvicorn 0.34.2 → 0.54.0. O build resolveu Starlette 0.46.2 → 1.10.0, eliminando, entre outros achados, CVE-2025-62727, CVE-2026-48818 e CVE-2026-54283. As outras ocorrências HIGH em Python foram CVE-2026-23949 em jaraco.context 5.3.0 e CVE-2026-24049 em wheel 0.45.1. Esses pacotes deixaram de aparecer entre os achados da imagem reconstruída. No frontend, `apk upgrade --no-cache` atualizou o zlib 1.3.2-r0 → 1.4-r0, eliminando CVE-2026-85091. Os totais do frontend anterior vêm da reprodução local, pois o workflow histórico pulou esse scanner. [FastAPI 0.162.2](https://fastapi.tiangolo.com/release-notes/#01622-2026-11-07), [Starlette](https://pypi.org/project/starlette/1.10.0/), [Uvicorn](https://pypi.org/project/uvicorn/0.54.0/)

A URL da execução corrigida será registrada após a validação do push pelo GitHub Actions. A tabela registra a comparação reproduzida localmente.

## Arquivos para conferência

- `.github/workflows/devsecops.yml`
- `.gitignore` e `.gitattributes`
- `backend/dockerfile`, `backend/.dockerignore` e `backend/requirements.txt`
- `frontend/dockerfile`, `frontend/.dockerignore` e `compose.yaml`
- `infra/main.tf`, `infra/providers.tf`, `infra/ssm.tf`, `infra/bootstrap.sh` e `infra/versions.tf`
