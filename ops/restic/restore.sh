#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-$HERE/env.local}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE"
  exit 2
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

if [[ -z "${RESTIC_REPOSITORY:-}" || -z "${RESTIC_PASSWORD:-}" ]]; then
  echo "RESTIC_REPOSITORY and RESTIC_PASSWORD must be set in $ENV_FILE"
  exit 2
fi

SNAPSHOT_ID="${1:-}"
if [[ -z "$SNAPSHOT_ID" ]]; then
  echo "Usage: $0 <restic_snapshot_id|latest>"
  exit 2
fi

TARGET="${TARGET:-/tmp/marketstructureos-restore}"
mkdir -p "$TARGET"

echo "Restoring snapshot '$SNAPSHOT_ID' into $TARGET"
restic restore "$SNAPSHOT_ID" --target "$TARGET"

cat <<EOF

Restore staged in: $TARGET

To restore the snapshots volume onto a VPS:
1) Stop the stack:   docker compose down
2) Copy data into the named volume's _data folder (careful!) OR mount volume and copy in:
   docker run --rm -v ppe_snapshots:/data -v "$TARGET":/restore alpine:3.20 sh -c "cp -av /restore/var/lib/docker/volumes/ppe_snapshots/_data/. /data/"
3) Start the stack:  docker compose up -d

EOF

