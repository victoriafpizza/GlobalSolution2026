#!/bin/bash
set -euo pipefail

exec > >(tee -a /var/log/rota-livre-bootstrap.log /dev/console) 2>&1
trap 'echo "ROTA_LIVRE_BOOTSTRAP_FALHOU linha $LINENO"' ERR
echo "ROTA_LIVRE_BOOTSTRAP_INICIADO"

dnf install -y docker git
systemctl enable --now docker

export DOCKER_CONFIG="${DOCKER_CONFIG:-/root/.docker}"
plugin_dir="$DOCKER_CONFIG/cli-plugins"

install_docker_plugin() (
  name=$1
  url=$2
  checksum=$3
  mkdir -p "$plugin_dir"
  download=$(mktemp "$plugin_dir/$name.XXXXXX")
  trap 'rm -f -- "$download"' EXIT
  curl --fail --silent --show-error --location --retry 3 "$url" --output "$download"
  printf '%s  %s\n' "$checksum" "$download" | sha256sum -c -
  install -m 0755 "$download" "$plugin_dir/$name"
)

if ! docker compose version >/dev/null 2>&1; then
  install_docker_plugin docker-compose \
    https://github.com/docker/compose/releases/download/v5.7.1/docker-compose-linux-x86_64 \
    af426722a8af5de812fcee30cc1c39f0639f5f723cbadefb25e5d4db054064cf
fi

if ! docker buildx version 2>/dev/null | grep -Eq '(^|[[:space:]])v0\.39\.0([[:space:]]|$)'; then
  install_docker_plugin docker-buildx \
    https://github.com/docker/buildx/releases/download/v0.39.0/buildx-v0.39.0.linux-amd64 \
    5fb31a097304fbf6dd4038649a0decf32c2b9510e4047acd7d68b9d700c46194
fi
docker compose version
docker buildx version

repo=/opt/rota-livre
if [[ -d "$repo/.git" ]]; then
  git -C "$repo" pull --ff-only
else
  git clone https://github.com/victoriafpizza/GlobalSolution2026.git "$repo"
fi

cd "$repo/ROTA-LIVRE"
ROTA_LIVRE_HTTP_BIND=0.0.0.0:80 docker compose -p rota-livre up -d --build --wait --wait-timeout 120
curl --fail --silent --show-error http://127.0.0.1/api/obstacles >/dev/null
echo "ROTA_LIVRE_BOOTSTRAP_CONCLUIDO"
