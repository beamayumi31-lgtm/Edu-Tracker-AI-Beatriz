"""Prepara credenciais locais sem ativar integração, acessar banco ou imprimir segredos."""

import getpass
import os
import re
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import dotenv_values, set_key


def main():
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise SystemExit("No Linux, use o arquivo privado do serviço. Consulte CLASSROOM_E_GEMINI.md.")
    target = Path(local) / "EduTrack" / "backend.env"
    values = dotenv_values(target) if target.exists() else {}
    if str(values.get("EDUTRACK_CLASSROOM_ENABLED", "false")).lower() == "true":
        raise SystemExit("A integração já está ativa. Revise as conexões existentes antes de trocar o cliente OAuth.")
    print("Crie um cliente OAuth do tipo Aplicativo da Web no Google Cloud.")
    print("Redirect local exato: http://localhost:3002/integracoes/google/callback")
    client_id = input("Client ID: ").strip()
    if not re.fullmatch(r"[a-zA-Z0-9._-]+\.apps\.googleusercontent\.com", client_id):
        raise SystemExit("Client ID inválido. Nenhuma alteração foi feita.")
    secret = getpass.getpass("Client secret (entrada oculta): ").strip()
    if len(secret) < 16 or any(c.isspace() for c in secret):
        raise SystemExit("Client secret inválido. Nenhuma alteração foi feita.")
    key = values.get("EDUTRACK_INTEGRATION_ENCRYPTION_KEY")
    if key:
        try:
            Fernet(key.encode())
        except (ValueError, TypeError):
            raise SystemExit("Chave de criptografia existente inválida. Revise-a antes de continuar.") from None
    else:
        key = Fernet.generate_key().decode()
    target.parent.mkdir(parents=True, exist_ok=True)
    set_key(str(target), "EDUTRACK_GOOGLE_CLIENT_ID", client_id)
    set_key(str(target), "EDUTRACK_GOOGLE_CLIENT_SECRET", secret)
    set_key(str(target), "EDUTRACK_INTEGRATION_ENCRYPTION_KEY", key)
    set_key(str(target), "EDUTRACK_CLASSROOM_ENABLED", "false")
    print("Credenciais preparadas fora do Git e do OneDrive. Nenhuma conexão ao Google foi realizada.")
    print("A integração permanece desativada até aprovação e aplicação da migração 004.")


if __name__ == "__main__":
    main()
