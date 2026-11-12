#!/bin/bash
set -euo pipefail
umask 027

commit=${1:-}
if [[ ! "$commit" =~ ^[0-9a-f]{40}$ ]]; then
  echo 'Informe o SHA completo do commit.' >&2
  exit 2
fi

export DOCKER_CONFIG="${DOCKER_CONFIG:-/root/.docker}"
export ROTA_LIVRE_HTTP_BIND=0.0.0.0:80
export GIT_TERMINAL_PROMPT=0
repository=https://github.com/victoriafpizza/GlobalSolution2026.git
deploy_dir=/opt/rota-livre-deploy
repo="$deploy_dir/repository.git"
release="$deploy_dir/releases/$commit"
install -d -m 0750 "$deploy_dir" "$deploy_dir/releases"

exec 9>"$deploy_dir/deploy.lock"
flock -w 60 9

if [[ ! -d "$repo" ]]; then
  git init --bare --quiet "$repo"
fi

current_main() {
  git ls-remote --exit-code "$repository" refs/heads/main | cut -f 1
}

git --git-dir="$repo" fetch --no-tags --quiet "$repository" refs/heads/main
if [[ $(git --git-dir="$repo" rev-parse FETCH_HEAD) != "$commit" ]]; then
  echo "ROTA_LIVRE_DEPLOY_STALE $commit"
  exit 0
fi

if [[ ! -d "$release" ]]; then
  checkout=$(mktemp -d "$deploy_dir/releases/.checkout.XXXXXX")
  trap 'rm -rf -- "$checkout"' EXIT
  git --git-dir="$repo" archive "$commit" | tar -xf - -C "$checkout"
  mv -- "$checkout" "$release"
  trap - EXIT
fi

revision_file="$release/ROTA-LIVRE/frontend/public/deploy-revision.txt"
printf '%s\n' "$commit" > "$revision_file"
chmod 0644 "$revision_file"

write_images() {
  cat > "$1" <<EOF
services:
  api:
    image: $2
  frontend:
    image: $3
EOF
}

api_tree=$(git --git-dir="$repo" rev-parse "$commit:ROTA-LIVRE/backend")
api_image="rota-livre-api:$api_tree"
frontend_image="rota-livre-frontend:$commit"
write_images "$release/docker-images.yaml" "$api_image" "$frontend_image"
compose=(docker compose -p rota-livre --project-directory "$release/ROTA-LIVRE"
  -f "$release/ROTA-LIVRE/compose.yaml" -f "$release/docker-images.yaml")
"${compose[@]}" config --quiet

services_to_build=()
if ! docker image inspect "$api_image" >/dev/null 2>&1; then
  services_to_build+=(api)
fi
if ! docker image inspect "$frontend_image" >/dev/null 2>&1; then
  services_to_build+=(frontend)
fi

if (( ${#services_to_build[@]} )); then
  echo "Construindo imagens: ${services_to_build[*]}"
  build_log="$release/build.log"
  if ! "${compose[@]}" build --pull "${services_to_build[@]}" > "$build_log" 2>&1; then
    tail -n 40 "$build_log" >&2
    exit 1
  fi
fi

running_api=$(docker ps -q --filter label=com.docker.compose.project=rota-livre \
  --filter label=com.docker.compose.service=api)
running_frontend=$(docker ps -q --filter label=com.docker.compose.project=rota-livre \
  --filter label=com.docker.compose.service=frontend)
if [[ ! "$running_api" =~ ^[0-9a-f]{12,64}$ || ! "$running_frontend" =~ ^[0-9a-f]{12,64}$ ]]; then
  echo 'O projeto em produção precisa de um container em execução para cada serviço.' >&2
  exit 1
fi

working_dir=$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project.working_dir" }}' "$running_frontend")
config_files=$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project.config_files" }}' "$running_frontend")
if [[ ! -d "$working_dir" || -z "$config_files" ]]; then
  echo 'Configuração do Compose em produção indisponível para recuperação.' >&2
  exit 1
fi

rollback=(docker compose -p rota-livre --project-directory "$working_dir")
IFS=, read -r -a previous_files <<< "$config_files"
for file in "${previous_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "Arquivo de recuperação indisponível: $file" >&2
    exit 1
  fi
  rollback+=(-f "$file")
done

rollback_file=$(mktemp "$deploy_dir/rollback.XXXXXX.yaml")
write_images "$rollback_file" \
  "$(docker inspect --format '{{.Image}}' "$running_api")" \
  "$(docker inspect --format '{{.Image}}' "$running_frontend")"
rollback+=(-f "$rollback_file")
"${rollback[@]}" config --quiet

healthy() {
  local page revision
  page=$(curl -fsS --max-time 10 http://127.0.0.1/) || return 1
  [[ "$page" == *'id="root"'* ]] || return 1
  if [[ -n "${1:-}" ]]; then
    revision=$(curl -fsS --max-time 10 http://127.0.0.1/deploy-revision.txt) || return 1
    [[ "$revision" == "$1" ]] || return 1
  fi
  curl -fsS --max-time 10 http://127.0.0.1/api/obstacles | python3 -c '
import json, sys
response = json.load(sys.stdin)
if not isinstance(response.get("obstaculos"), list) or response.get("total") != len(response["obstaculos"]):
    sys.exit("Resposta de obstáculos inválida")
'
}

observed_main=$(current_main)
if [[ "$observed_main" != "$commit" ]]; then
  rm -f -- "$rollback_file"
  echo "ROTA_LIVRE_DEPLOY_STALE $commit"
  exit 0
fi

log="$release/deploy.log"
if ! "${compose[@]}" up -d --no-build --pull never --wait --wait-timeout 120 > "$log" 2>&1 || ! healthy "$commit"; then
  tail -n 40 "$log" >&2
  echo "ROTA_LIVRE_ROLLBACK_INICIADO $commit" >&2
  if "${rollback[@]}" up -d --no-build --pull never --wait --wait-timeout 120 >> "$log" 2>&1 && healthy; then
    echo "ROTA_LIVRE_ROLLBACK_OK $commit" >&2
  else
    tail -n 40 "$log" >&2
    echo "ROTA_LIVRE_ROLLBACK_FALHOU $commit" >&2
  fi
  exit 1
fi

rm -f -- "$rollback_file"
printf '%s\n' "$commit" > "$deploy_dir/current.tmp"
mv -- "$deploy_dir/current.tmp" "$deploy_dir/current"
"${compose[@]}" ps --format 'table {{.Service}}\t{{.Status}}'
echo "ROTA_LIVRE_DEPLOY_OK $commit"
