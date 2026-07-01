#!/usr/bin/env bash
# Post-deploy telemetry on VPS (pull usage JSONL, retention, deploy marker).
set -euo pipefail
ROOT="${PPE_VPS_ROOT:-/opt/marketstructureos}"
cd "$ROOT"
mkdir -p data
date -u +%Y-%m-%dT%H:%M:%SZ > data/last_vps_deploy.utc
python scripts/ppe_product_usage.py --pull-from-docker msos_web || echo "vps_post_deploy_telemetry: pull skipped"
python scripts/ppe_jsonl_retention.py --apply || echo "vps_post_deploy_telemetry: retention skipped"
echo "vps_post_deploy_telemetry: done ($(cat data/last_vps_deploy.utc))"
