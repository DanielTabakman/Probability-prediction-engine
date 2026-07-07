#!/bin/sh
set -e

if [ "$(id -u)" = "0" ]; then
  mkdir -p "${PPE_WEB_FEEDBACK_DIR:-/data}" "${PPE_PRODUCT_USAGE_DIR:-/data}"
  chown -R nextjs:nodejs /data 2>/dev/null || true
  exec su-exec nextjs "$@"
fi

exec "$@"
