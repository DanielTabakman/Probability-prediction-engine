#!/usr/bin/env bash
# Enable research-beta CTA on apex MSOS shell (VPS one-liner).
# Usage (on VPS): bash scripts/vps_enable_research_cta.sh you@example.com
set -euo pipefail
EMAIL="${1:-}"
if [[ -z "$EMAIL" ]]; then
  echo "usage: $0 <contact-email>" >&2
  exit 1
fi
ROOT="${PPE_VPS_ROOT:-/opt/marketstructureos}"
cd "$ROOT"
ENV_FILE=".env"
touch "$ENV_FILE"
URL="mailto:${EMAIL}?subject=PPE%20research%20beta"
if grep -q '^PPE_RESEARCH_OFFER_URL=' "$ENV_FILE" 2>/dev/null; then
  sed -i "s|^PPE_RESEARCH_OFFER_URL=.*|PPE_RESEARCH_OFFER_URL=${URL}|" "$ENV_FILE"
else
  echo "PPE_RESEARCH_OFFER_URL=${URL}" >>"$ENV_FILE"
fi
if ! grep -q '^PPE_RESEARCH_OFFER_LABEL=' "$ENV_FILE" 2>/dev/null; then
  echo "PPE_RESEARCH_OFFER_LABEL=Request research beta access" >>"$ENV_FILE"
fi
docker compose up -d --build msos_web
echo "vps_enable_research_cta: rebuilt msos_web with research CTA"
