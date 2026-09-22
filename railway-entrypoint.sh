#!/bin/bash
# Railway entrypoint for Crafty Controller 4: state on the one volume, the panel behind
# Caddy on $PORT, and on first boot a Paper server that players can join right away.
set -euo pipefail

# Railway volumes mount root-owned; Crafty runs as crafty (uid 1000, group root).
# Top level only: everything inside is created by Crafty itself.
mkdir -p /data/config /data/servers /data/backups /data/logs /data/import
chown crafty:root /data /data/*

# First boot: Crafty creates its admin from default.json, so the password is the
# Railway variable instead of a random one buried in default-creds.txt.
if [ -z "$(ls -A /data/config)" ]; then
  [ ${#CRAFTY_ADMIN_PASSWORD} -ge 8 ] || { echo "CRAFTY_ADMIN_PASSWORD needs 8+ characters"; exit 1; }
  cp -r /crafty/app/config_original/. /data/config/
  python3 -c 'import json, os; print(json.dumps({"username": "admin", "password": os.environ["CRAFTY_ADMIN_PASSWORD"]}))' > /data/config/default.json
  chown -R crafty:root /data/config
fi

if [ -n "${RAILWAY_TCP_PROXY_DOMAIN:-}" ]; then
  echo "railway: players join at $RAILWAY_TCP_PROXY_DOMAIN:$RAILWAY_TCP_PROXY_PORT"
fi

# Crafty stops every Minecraft server cleanly on SIGTERM (world saved); pass it on
# and wait. RAILWAY_DEPLOYMENT_DRAINING_SECONDS gives it the time.
trap 'kill $(jobs -p) 2>/dev/null; wait; exit 0' TERM INT

XDG_CONFIG_HOME=/tmp XDG_DATA_HOME=/tmp setpriv --reuid=crafty --regid=root --init-groups \
  caddy run --config /etc/caddy/Caddyfile --adapter caddyfile &
caddy_pid=$!
/crafty/docker_launcher.sh -d -i &
crafty_pid=$!

[ -e /data/config/.first-server-done ] || python3 /first-server.py &

# Caddy or Crafty exiting means the service is broken: exit so Railway restarts it.
wait -n "$caddy_pid" "$crafty_pid"
exit 1
