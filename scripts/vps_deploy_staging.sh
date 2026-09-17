#!/usr/bin/env bash
# Deploy the isolated MSOS shell and Options Market Read API staging stack on
# the VPS without rebuilding or recreating production services.
#
# Staging uses a separate git checkout under /opt/marketstructureos-staging and
# docker compose profile "staging". Caddy routes exact API paths to
# ppe_display_api_staging:8766 and all other staging host paths to
# msos_web_staging:3001.
#
# Usage (on VPS or via Deploy VPS Staging workflow):
#   bash scripts/vps_deploy_staging.sh                    # origin/main
#   bash scripts/vps_deploy_staging.sh origin/my-feature
#
# One-time VPS setup:
#   sudo mkdir -p /opt/marketstructureos-staging
#   sudo chown -R $USER:$USER /opt/marketstructureos-staging
#   git clone <repo> /opt/marketstructureos-staging   # or git worktree add
#   Cloudflare DNS: A staging → VPS IP (proxied)
#
set -euo pipefail

REF="${1:-origin/main}"
STAGING_ROOT="${PPE_STAGING_ROOT:-/opt/marketstructureos-staging}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -d "$STAGING_ROOT/.git" ]]; then
  bash "${SCRIPT_DIR}/vps_bootstrap_staging.sh"
fi

cd "$STAGING_ROOT"
git fetch origin
LOCAL_REF="${REF#origin/}"
if git show-ref --verify --quiet "refs/remotes/${REF}" 2>/dev/null; then
  # Deploy the remote commit directly. A detached checkout avoids local ref
  # namespace collisions such as an existing `staging` branch blocking a
  # remote `staging/my-feature` branch.
  git checkout --detach "$REF"
elif git show-ref --verify --quiet "refs/heads/${LOCAL_REF}" 2>/dev/null; then
  git checkout --detach "$LOCAL_REF"
elif [[ "$REF" != "origin/main" ]] && git show-ref --verify --quiet "refs/remotes/origin/main" 2>/dev/null; then
  echo "vps_deploy_staging: ref ${REF} not found — falling back to origin/main" >&2
  git checkout --detach origin/main
else
  echo "vps_deploy_staging: ref ${REF} not found" >&2
  exit 1
fi

echo "Staging deploy commit: $(git rev-parse HEAD)"

if [[ -f scripts/vps_sync_production_env.sh ]]; then
  bash scripts/vps_sync_production_env.sh
fi

RESEARCH_URL="$(grep '^PPE_RESEARCH_OFFER_URL=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '\"' || true)"
RESEARCH_LABEL="$(grep '^PPE_RESEARCH_OFFER_LABEL=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '\"' || true)"

PROD_ROOT="${PPE_VPS_ROOT:-/opt/marketstructureos}"
# Share the production compose project/network so Caddy can reach msos_web_staging:3001.
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-marketstructureos}"

docker compose --profile staging build ppe_display_api_staging
docker compose --profile staging build --no-cache msos_web_staging \
  --build-arg "NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL=${RESEARCH_URL}" \
  --build-arg "NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL=${RESEARCH_LABEL:-Request research beta access}"
# Remove orphan from prior marketstructureos-staging compose project (wrong network).
docker rm -f \
  msos_web_staging \
  ppe_display_api_staging \
  ppe_display_cache_refresh_staging \
  2>/dev/null || true
docker compose --profile staging up -d --force-recreate \
  ppe_display_api_staging \
  ppe_display_cache_refresh_staging \
  msos_web_staging

echo "Warming isolated staging display cache…"
docker compose --profile staging exec -T ppe_display_api_staging \
  python scripts/warm_display_payload_cache.py \
  --base-url http://127.0.0.1:8766 \
  || echo "staging display cache warm failed (non-fatal; first request may be slow)"

# Reload shared Caddy routes (avoid --force-recreate — races production deploy on :80).
if [[ -d "$PROD_ROOT" && "$PROD_ROOT" != "$STAGING_ROOT" ]]; then
  (cd "$PROD_ROOT" && git pull --ff-only origin main 2>/dev/null || true)
  (cd "$PROD_ROOT" && docker compose restart caddy) \
    || (cd "$PROD_ROOT" && docker compose up -d caddy) \
    || true
fi

echo "vps_deploy_staging: isolated staging up"
echo "  shell: https://staging.marketstructureos.com/"
echo "  API:   https://staging.marketstructureos.com/v1/options-market-read"
