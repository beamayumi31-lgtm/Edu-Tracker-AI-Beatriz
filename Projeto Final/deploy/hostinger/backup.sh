#!/bin/sh
# Execução exclusiva da instalação EduTrack; não remove backups automaticamente.
set -eu
test "$(hostname)" = srv1834976
umask 077
name="EduTrackIA_$(date -u +%Y%m%dT%H%M%SZ).bak"
mkdir -p /opt/edutrack/backups/sql
docker exec --user 10001 edutrack-sql-1 mkdir -p /var/opt/mssql/backup
docker run --rm --network host --env-file /opt/edutrack/secrets/provision.env \
  -e SSL_CERT_FILE=/etc/edutrack-ca/ca-certificates.crt \
  -v /opt/edutrack/secrets/public-ca:/etc/edutrack-ca:ro \
  -v /opt/edutrack/current/deploy/hostinger/backup_sql.py:/backup_sql.py:ro \
  --entrypoint python edutrack-api:latest /backup_sql.py "$name"
docker cp "edutrack-sql-1:/var/opt/mssql/backup/$name" "/opt/edutrack/backups/sql/$name"
chmod 600 "/opt/edutrack/backups/sql/$name"
