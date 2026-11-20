"""Transfere apenas os campos SendGrid aprovados pelo canal SSH autenticado."""
import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path

from dotenv import dotenv_values

REMOTE = '''import json, os, pathlib, sys
os.umask(0o077)
p = pathlib.Path('/opt/edutrack/secrets/backend.env')
values = json.load(sys.stdin)
allowed = {'SENDGRID_API_KEY', 'EDUTRACK_EMAIL_FROM', 'EDUTRACK_EMAIL_FROM_NAME'}
assert set(values) == allowed
lines = [line for line in p.read_text().splitlines() if line.split('=',1)[0] not in allowed]
lines += [key+'='+json.dumps(value) for key,value in values.items()]
temp = p.with_suffix('.pending')
temp.write_text('\\n'.join(lines)+'\\n')
temp.chmod(0o600)
temp.replace(p)
print('Configuração SendGrid transferida; segredo não exibido.')
'''

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--execute', action='store_true')
args = parser.parse_args()
if not args.execute:
    raise SystemExit('Exige autorização prévia e --execute.')
source = dotenv_values(Path(os.environ['LOCALAPPDATA']) / 'EduTrack/backend.env')
keys = ['SENDGRID_API_KEY', 'EDUTRACK_EMAIL_FROM', 'EDUTRACK_EMAIL_FROM_NAME']
payload = {key: source.get(key) or ('EduTrack' if key.endswith('_NAME') else '') for key in keys}
if not all(payload.values()):
    raise SystemExit('Remetente ou credencial local ausente.')
command = ['ssh', '-i', str(Path.home()/'.ssh/id_ed25519_vps_antonio'),
           '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', 'root@179.197.79.177',
           'python3 -c ' + shlex.quote(REMOTE)]
result = subprocess.run(command, input=json.dumps(payload).encode(), capture_output=True, check=False)
if result.returncode:
    raise SystemExit('Transferência não concluída; conteúdo privado omitido.')
print(result.stdout.decode().strip())
