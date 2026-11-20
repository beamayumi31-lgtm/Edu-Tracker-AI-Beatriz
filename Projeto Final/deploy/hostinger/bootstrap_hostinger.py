"""Preparação restrita da VPS autorizada. Não modifica os outros projetos."""

import argparse
import hashlib
import json
import os
import secrets
import shutil
import socket
import subprocess
from pathlib import Path
from urllib.parse import quote

ROOT = Path('/opt/edutrack')
DOMAIN = 'srv1834976.hstgr.cloud'
SITE = Path('/etc/nginx/sites-available/edutrack')
ENABLED = Path('/etc/nginx/sites-enabled/edutrack')


def run(*args):
    subprocess.run(args, check=True)


def private_file(path, content):
    # Nunca sobrescreve uma credencial existente nem imprime seu conteúdo.
    with path.open('x', encoding='utf-8') as handle:
        handle.write(content)
    path.chmod(0o600)


def initialize():
    if ROOT.exists() or SITE.exists() or ENABLED.exists():
        raise SystemExit('Instalação já existe. Revisar antes de executar novamente.')
    ROOT.mkdir(mode=0o700)
    for folder in ('releases', 'secrets', 'backups'):
        (ROOT / folder).mkdir(mode=0o700)
    baseline = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in Path('/etc/nginx/sites-available').iterdir() if p.is_file()}
    private_file(ROOT / 'backups/nginx-baseline.json', json.dumps(baseline, indent=2))
    print('Diretórios isolados e inventário de Nginx preparados.')


def certificate():
    if SITE.exists() or ENABLED.exists():
        raise SystemExit('Arquivo Nginx já existe; não sobrescrito.')
    Path('/var/www/edutrack-acme').mkdir(mode=0o755, exist_ok=True)
    Path('/var/www/edutrack-acme').chmod(0o755)
    SITE.write_text('server {\n listen 80;\n listen [::]:80;\n'
                    f' server_name {DOMAIN};\n'
                    ' location ^~ /.well-known/acme-challenge/ { root /var/www/edutrack-acme; }\n'
                    ' location / { return 503; }\n}\n', encoding='utf-8')
    ENABLED.symlink_to(SITE)
    run('nginx', '-t')
    run('systemctl', 'reload', 'nginx')
    run('certbot', 'certonly', '--webroot', '-w', '/var/www/edutrack-acme',
        '--cert-name', 'edutrack', '-d', DOMAIN, '--key-type', 'rsa', '--rsa-key-size', '2048',
        '--non-interactive', '--account', '43918b7727ff900fb510fc6dbd8b430f')
    target = ROOT / 'secrets/tls'
    target.mkdir(mode=0o750, exist_ok=True)
    os.chown(target, 10001, 0)
    for name in ('fullchain.pem', 'privkey.pem'):
        shutil.copyfile(Path('/etc/letsencrypt/live/edutrack') / name, target / name)
        os.chown(target / name, 10001, 0)
        (target / name).chmod(0o440)
    print('Certificado emitido; cópias privadas instaladas para SQL Server.')


def credentials():
    sa = secrets.token_urlsafe(40) + 'Aa1!'
    app = secrets.token_urlsafe(40) + 'Aa1!'
    jwt = secrets.token_urlsafe(64)
    private_file(ROOT / 'secrets/compose.env', f'ACCEPT_MICROSOFT_EULA=Y\nMSSQL_SA_PASSWORD={sa}\n')
    private_file(ROOT / 'secrets/provision.env', f'MSSQL_SA_PASSWORD={sa}\nEDUTRACK_SQL_PASSWORD={app}\n')
    url = (f'mssql+pyodbc://edutrack_app:{quote(app, safe="")}@127.0.0.1:14330/EduTrackIA'
           '?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no'
           f'&HostNameInCertificate={DOMAIN}&LongAsMax=Yes')
    values = {'EDUTRACK_ENVIRONMENT': 'production', 'EDUTRACK_DB_WRITES_ENABLED': 'false',
              'EDUTRACK_TRUST_SERVER_CERTIFICATE': 'false', 'EDUTRACK_JWT_SECRET': jwt,
              'EDUTRACK_DATABASE_URL': url, 'EDUTRACK_FRONTEND_URL': f'https://{DOMAIN}',
              'EDUTRACK_CORS_ORIGINS': json.dumps([f'https://{DOMAIN}']),
              'EDUTRACK_EMAIL_VERIFICATION_ENABLED': 'false',
              'EDUTRACK_PASSWORD_RESET_ENABLED': 'false', 'EDUTRACK_EMAIL_FROM_NAME': 'EduTrack'}
    private_file(ROOT / 'secrets/backend.env', ''.join(f'{key}={value}\n' for key, value in values.items()))
    print('Credenciais aleatórias geradas em arquivos privados; nenhum segredo exibido.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['initialize', 'certificate', 'credentials'])
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute or socket.gethostname() != 'srv1834976' or os.getuid() != 0:
        raise SystemExit('Exige aprovação, --execute e execução root na VPS autorizada.')
    os.umask(0o077)
    globals()[args.step]()
