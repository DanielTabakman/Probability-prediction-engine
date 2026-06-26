#!/usr/bin/env bash
# One-time (idempotent) MSOS staging checkout on the VPS.
#
# Usage:
#   bash scripts/vps_bootstrap_staging.sh
#
# Env:
#   PPE_STAGING_ROOT  — default /opt/marketstructureos-staging
#   PPE_VPS_ROOT      — production checkout (default /opt/marketstructureos)
#   PPE_GITHUB_REPO   — clone URL
set -euo pipefail

STAGING_ROOT="${PPE_STAGING_ROOT:-/opt/marketstructureos-staging}"
PROD_ROOT="${PPE_VPS_ROOT:-/opt/marketstructureos}"
REPO_URL="${PPE_GITHUB_REPO:-https://github.com/DanielTabakman/Probability-prediction-engine.git}"

if [[ -d "${STAGING_ROOT}/.git" ]]; then
  echo "vps_bootstrap_staging: already present at ${STAGING_ROOT}"
  exit 0
fi

echo "vps_bootstrap_staging: creating ${STAGING_ROOT}"
sudo mkdir -p "${STAGING_ROOT}"
sudo chown -R "${USER}:${USER}" "${STAGING_ROOT}"
git clone "${REPO_URL}" "${STAGING_ROOT}"
cd "${STAGING_ROOT}"
git fetch origin
git checkout -B staging origin/main
if [[ -f "${PROD_ROOT}/.env" ]]; then
  cp "${PROD_ROOT}/.env" .env
  echo "vps_bootstrap_staging: copied .env from ${PROD_ROOT}"
fi
echo "vps_bootstrap_staging: ready ($(git rev-parse --short HEAD))"
