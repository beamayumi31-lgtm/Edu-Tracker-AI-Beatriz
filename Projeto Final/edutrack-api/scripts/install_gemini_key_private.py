"""Prepare/install only GEMINI_API_KEY over verified SSH stdin. Dry run by default."""
import argparse
import getpass
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

HOST = "root@179.197.79.177"
KEY_PATH = Path.home() / ".ssh/id_ed25519_vps_antonio"
REMOTE = r"""
import json,os,re,stat,sys,tempfile
from pathlib import Path
try:
    data=json.loads(sys.stdin.buffer.read(4096))
    key=data['key']
    if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{20,256}',key):raise ValueError()
    path=Path('/opt/edutrack/secrets/backend.env')
    if path.is_symlink():raise ValueError()
    st=path.stat()
    if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode)!=0o600:raise ValueError()
    original=path.read_bytes()
    lines=original.decode('utf-8').splitlines(keepends=True)
    flag=[line.split('=',1)[1].strip().strip(chr(34)+chr(39)).lower() for line in lines if line.split('=',1)[0].strip()=='EDUTRACK_GEMINI_ENABLED']
    if flag != ['false']:raise ValueError()
    if any(re.match(r'\s*(?:export\s+)?GEMINI_API_KEY\s*=',line) and not line.startswith('GEMINI_API_KEY=') for line in lines):raise ValueError()
    if any(re.match(r'\s*export\s+EDUTRACK_GEMINI_ENABLED\s*=',line) for line in lines):raise ValueError()
    matches=[i for i,line in enumerate(lines) if line.startswith('GEMINI_API_KEY=')]
    if len(matches)>1:raise ValueError()
    replacement='GEMINI_API_KEY='+key+'\n'
    if matches:lines[matches[0]]=replacement
    else:
        if lines and not lines[-1].endswith(('\n','\r')):lines[-1]+='\n'
        lines.append(replacement)
    fd,tmp=tempfile.mkstemp(prefix='.gemini-key-',dir=path.parent)
    try:
        os.fchmod(fd,stat.S_IMODE(st.st_mode));os.fchown(fd,st.st_uid,st.st_gid)
        with os.fdopen(fd,'wb') as out:
            out.write(''.join(lines).encode('utf-8'));out.flush();os.fsync(out.fileno())
        if path.read_bytes()!=original:raise ValueError()
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print('KEY_INSTALLED_NO_RESTART')
except Exception:
    print('INSTALL_FAILED_NO_DETAILS');sys.exit(1)
"""


def install_key(key, *, run=subprocess.run):
    if not re.fullmatch(r"[A-Za-z0-9_.-]{20,256}", key):
        raise ValueError("Invalid key format; no connection attempted.")
    command = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
               "-o", "ConnectTimeout=12", "-i", str(KEY_PATH), HOST,
               "python3 -c " + shlex.quote(REMOTE)]
    try:
        result = run(command, input=json.dumps({"key": key}).encode(),
                     capture_output=True, timeout=30, check=False)
    except Exception:
        raise RuntimeError("Installation could not be confirmed; inspect server state before retrying.") from None
    if result.returncode != 0 or result.stdout.strip() != b"KEY_INSTALLED_NO_RESTART":
        raise RuntimeError("Installation failed or uncertain. No remote details displayed.")
    return "Key installed privately; no flags changed, no restart or model request performed."


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install-authorized", action="store_true",
                        help="Use only after approval of permanent key storage at this server.")
    args = parser.parse_args(argv)
    if not args.install_authorized:
        print("DRY RUN: no prompt, connection or write. Target: existing EduTrack private server configuration.")
        return
    if not sys.stdin.isatty():
        parser.error("An interactive private terminal is required; no piped credentials.")
    key = getpass.getpass("Authorized Gemini key (hidden, never logged): ").strip()
    try:
        print(install_key(key))
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, str(exc) + "\n")
    finally:
        key = None


if __name__ == "__main__":
    main()
