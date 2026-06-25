#!/bin/sh
set -e
# Fix volume ownership when the container starts as root (named volumes default to root).
if [ "$(id -u)" = "0" ] && [ -d /data ]; then
  chown -R ppe:ppe /data 2>/dev/null || true
fi
if [ "$(id -u)" = "0" ]; then
  exec runuser -u ppe -- "$@"
fi
exec "$@"
