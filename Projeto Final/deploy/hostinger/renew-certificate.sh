#!/bin/sh
# Hook Certbot: só reage ao certificado EduTrack. Breve reinício do SQL e da API.
set -eu
test "${RENEWED_LINEAGE:-}" = /etc/letsencrypt/live/edutrack || exit 0
python3 /opt/edutrack/current/deploy/hostinger/refresh_tls.py --execute
docker compose --env-file /opt/edutrack/secrets/compose.env \
  -f /opt/edutrack/current/deploy/hostinger/compose.yaml restart sql api
docker compose --env-file /opt/edutrack/secrets/compose.env \
  -f /opt/edutrack/current/deploy/hostinger/compose.yaml up -d --wait --wait-timeout 120
nginx -t
systemctl reload nginx
