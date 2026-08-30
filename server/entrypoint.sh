#!/bin/sh
# Railway adapter: Railway mounts volumes root-owned, but the upstream image is
# built to run Boop as uid 1000. When started as root (Railway default), fix the
# ownership of /data once and drop to uid 1000 via su-exec. When started as a
# non-root user (plain `docker run` / docker compose), run unchanged.
set -e

if [ "$(id -u)" = "0" ]; then
  chown -R 1000:1000 /data
  exec su-exec 1000:1000 /usr/local/bin/boop
fi

exec /usr/local/bin/boop
