#!/usr/bin/env bash
# Deploy MSOS staging shell on the VPS without touching production msos_web.
#
# Staging uses a separate git checkout under /opt/marketstructureos-staging and
# docker compose profile "staging" (msos_web_staging on port 3001).
# Caddy routes staging.marketstructureos.com → msos_web_staging:3001.
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
BRANCH="${REF#origin/}"
if git show-ref --verify --quiet "refs/remotes/${REF}" 2>/dev/null; then
  git checkout -B "$BRANCH" "$REF"
elif git show-ref --verify --quiet "refs/heads/${BRANCH}" 2>/dev/null; then
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH" 2>/dev/null || true
elif [[ "$REF" != "origin/main" ]] && git show-ref --verify --quiet "refs/remotes/origin/main" 2>/dev/null; then
  echo "vps_deploy_staging: ref ${REF} not found — falling back to origin/main" >&2
  git checkout -B staging origin/main
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

docker compose build --no-cache msos_web_staging \
  --build-arg "NEXT_PUBLIC_PPE_RESEARCH_OFFER_URL=${RESEARCH_URL}" \
  --build-arg "NEXT_PUBLIC_PPE_RESEARCH_OFFER_LABEL=${RESEARCH_LABEL:-Request research beta access}"
# Remove orphan from prior marketstructureos-staging compose project (wrong network).
docker rm -f msos_web_staging 2>/dev/null || true
docker compose --profile staging up -d --force-recreate msos_web_staging

# Reload shared Caddy routes (avoid --force-recreate — races production deploy on :80).
if [[ -d "$PROD_ROOT" && "$PROD_ROOT" != "$STAGING_ROOT" ]]; then
  (cd "$PROD_ROOT" && git pull --ff-only origin main 2>/dev/null || true)
  (cd "$PROD_ROOT" && docker compose restart caddy) \
    || (cd "$PROD_ROOT" && docker compose up -d caddy) \
    || true
fi

echo "vps_deploy_staging: msos_web_staging up — https://staging.marketstructureos.com/"
