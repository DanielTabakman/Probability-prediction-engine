#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_FILE="${ENV_FILE:-$HERE/env.local}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  echo "Create it from: $HERE/env.example"
  exit 2
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

if [[ -z "${RESTIC_REPOSITORY:-}" || -z "${RESTIC_PASSWORD:-}" ]]; then
  echo "RESTIC_REPOSITORY and RESTIC_PASSWORD must be set in $ENV_FILE"
  exit 2
fi

TS="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="${APP_ROOT:-/opt/marketstructureos}"

echo "Backing up at $TS"

# Back up the persisted snapshots volume + minimal config.
# The compose stack pins the snapshots volume name to `ppe_snapshots` in `docker-compose.yml`.
# We mount it into a disposable container to sanity-check visibility.
docker run --rm \
  -v ppe_snapshots:/data:ro \
  -v "$ROOT":/app:ro \
  alpine:3.20 \
  sh -c "ls -la /data >/dev/null && ls -la /app >/dev/null"

VOL_MOUNTPOINT="$(docker volume inspect ppe_snapshots --format '{{ .Mountpoint }}')"
if [[ -z "$VOL_MOUNTPOINT" || ! -d "$VOL_MOUNTPOINT" ]]; then
  echo "Could not resolve docker volume mountpoint for ppe_snapshots"
  exit 2
fi

restic backup \
  --tag marketstructureos \
  --tag snapshots \
  --tag config \
  "$VOL_MOUNTPOINT" \
  "$ROOT/docker-compose.yml" \
  "$ROOT/Caddyfile"

restic forget \
  --tag marketstructureos \
  --prune \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 6

restic check

echo "Backup complete."

