#!/usr/bin/env bash
# Sync production .env keys from environment (GitHub Actions secrets → VPS).
# Called by Deploy VPS before docker compose. Idempotent.
#
# Env (optional):
#   PPE_RESEARCH_OFFER_URL   — full https:// or mailto: URL (wins over email)
#   PPE_RESEARCH_OFFER_EMAIL — builds mailto: URL when URL unset
#   PPE_RESEARCH_OFFER_LABEL — CTA button label (default when URL set)
#   PPE_VPS_ROOT             — default /opt/marketstructureos
set -euo pipefail
ROOT="${PPE_VPS_ROOT:-/opt/marketstructureos}"
cd "$ROOT"
ENV_FILE=".env"
touch "$ENV_FILE"

set_kv() {
  local key="$1"
  local val="$2"
  local quoted="${val//\"/\\\"}"
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    sed -i "s|^${key}=.*|${key}=\"${quoted}\"|" "$ENV_FILE"
  else
    echo "${key}=\"${quoted}\"" >>"$ENV_FILE"
  fi
}

if [[ -n "${PPE_RESEARCH_OFFER_URL:-}" ]]; then
  set_kv PPE_RESEARCH_OFFER_URL "${PPE_RESEARCH_OFFER_URL}"
elif [[ -n "${PPE_RESEARCH_OFFER_EMAIL:-}" ]]; then
  set_kv PPE_RESEARCH_OFFER_URL "mailto:${PPE_RESEARCH_OFFER_EMAIL}?subject=PPE%20research%20beta"
fi

if [[ -n "${PPE_RESEARCH_OFFER_LABEL:-}" ]]; then
  set_kv PPE_RESEARCH_OFFER_LABEL "${PPE_RESEARCH_OFFER_LABEL}"
elif grep -q '^PPE_RESEARCH_OFFER_URL=' "$ENV_FILE" 2>/dev/null; then
  if ! grep -q '^PPE_RESEARCH_OFFER_LABEL=' "$ENV_FILE" 2>/dev/null; then
    set_kv PPE_RESEARCH_OFFER_LABEL "Request research beta access"
  fi
fi

echo "vps_sync_production_env: synced $(grep -c '^PPE_' "$ENV_FILE" 2>/dev/null || echo 0) PPE_* keys in ${ENV_FILE}"
