"""Atualiza certificados do EduTrack sem desativar a validação TLS do ODBC."""
import argparse
import os
import socket
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--execute', action='store_true')
args = parser.parse_args()
if not args.execute or os.getuid() != 0 or socket.gethostname() != 'srv1834976':
    raise SystemExit('Exige root na VPS autorizada e --execute.')
source = Path('/etc/letsencrypt/live/edutrack')
target = Path('/opt/edutrack/secrets')
# A cadeia intermediária deve alcançar uma raiz já confiável no sistema.
subprocess.run(['openssl', 'verify', '-CAfile', '/etc/ssl/certs/ca-certificates.crt',
                '-untrusted', str(source/'chain.pem'), str(source/'cert.pem')], check=True)
subprocess.run(['openssl', 'x509', '-in', str(source/'cert.pem'), '-noout',
                '-checkhost', 'srv1834976.hstgr.cloud', '-checkend', '86400'], check=True)
for name in ('fullchain.pem', 'privkey.pem'):
    temporary = target / 'tls' / (name + '.pending')
    temporary.write_bytes((source/name).read_bytes())
    os.chown(temporary, 10001, 0)
    temporary.chmod(0o440)
    temporary.replace(target / 'tls' / name)
# SQL Server pode enviar somente o certificado folha. O cliente recebe as CAs
# intermediárias verificadas, preservando as raízes e a conferência do hostname.
trust = target / 'public-ca'
trust.mkdir(mode=0o755, exist_ok=True)
trust.chmod(0o755)
roots = subprocess.check_output(['docker', 'run', '--rm', '--entrypoint', 'cat',
                                 'edutrack-api:latest', '/etc/ssl/certs/ca-certificates.crt'])
bundle = trust / 'ca-certificates.crt'
temporary = bundle.with_suffix('.pending')
temporary.write_bytes(roots + b'\n' + (source/'chain.pem').read_bytes())
temporary.chmod(0o644)
temporary.replace(bundle)
print('Cadeia pública validada e instalada; chaves mantidas privadas.')
