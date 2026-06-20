#!/usr/bin/env bash
# Enable research-beta CTA on apex MSOS shell (VPS one-liner).
# Usage (on VPS): bash scripts/vps_enable_research_cta.sh you@example.com
set -euo pipefail
EMAIL="${1:-}"
if [[ -z "$EMAIL" ]]; then
  echo "usage: $0 <contact-email>" >&2
  exit 1
fi
export PPE_RESEARCH_OFFER_EMAIL="$EMAIL"
ROOT="${PPE_VPS_ROOT:-/opt/marketstructureos}"
cd "$ROOT"
bash scripts/vps_sync_production_env.sh
docker compose up -d --build msos_web
echo "vps_enable_research_cta: rebuilt msos_web with research CTA"
