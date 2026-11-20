"""Ativa recursos após readiness; exige aprovação explícita da implantação."""
import argparse
import json
import os
import socket
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--execute', action='store_true')
args = parser.parse_args()
if not args.execute or os.getuid() != 0 or socket.gethostname() != 'srv1834976':
    raise SystemExit('Exige --execute e root na VPS autorizada.')
with urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=10) as response:
    assert response.status == 200
path = Path('/opt/edutrack/secrets/backend.env')
lines = path.read_text().splitlines()
keys = {'EDUTRACK_DB_WRITES_ENABLED', 'EDUTRACK_EMAIL_VERIFICATION_ENABLED', 'EDUTRACK_PASSWORD_RESET_ENABLED'}
assert keys.issubset({line.split('=',1)[0] for line in lines})
assert any(line.startswith('SENDGRID_API_KEY=') for line in lines)
lines = [line.split('=',1)[0]+'=true' if line.split('=',1)[0] in keys else line for line in lines]
os.umask(0o077)
temporary = path.with_suffix('.pending')
temporary.write_text('\n'.join(lines)+'\n')
temporary.chmod(0o600)
temporary.replace(path)
print(json.dumps({'gravacoes': True, 'verificacao_email': True, 'recuperacao_senha': True}))
