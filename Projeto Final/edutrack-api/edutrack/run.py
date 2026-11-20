"""Inicialização local deliberadamente limitada a 127.0.0.1."""

import argparse
import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


def load_local_secrets():
    """Segredos privados fora do repositório/OneDrive, somente no iniciador local."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        # Variáveis explicitamente definidas pelo operador têm prioridade.
        load_dotenv(Path(local_app_data) / "EduTrack" / "backend.env", override=False)


def main():
    parser = argparse.ArgumentParser(description="Iniciar EduTrack API local")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--local-sql-certificate",
        action="store_true",
        help="Aceitar certificado local do SQL Server Express (somente desenvolvimento).",
    )
    args = parser.parse_args()
    load_local_secrets()
    if args.local_sql_certificate:
        os.environ.setdefault("EDUTRACK_TRUST_SERVER_CERTIFICATE", "true")
    print("EduTrack API: http://127.0.0.1:%s/docs" % args.port)
    print("Swagger: http://127.0.0.1:%s/docs" % args.port)
    print("Nenhuma migração é executada. O inicializador integrado habilita gravações locais.")
    uvicorn.run(
        "edutrack.main:app_factory",
        factory=True,
        host="127.0.0.1",
        port=args.port,
        proxy_headers=False,
        access_log=False,
    )


if __name__ == "__main__":
    main()
