"""Prévia manual isolada: Google simulado, banco temporário, sem conexão ao SQL Server."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import httpx
from cryptography.fernet import Fernet
from preview_app import build_preview
from pydantic import SecretStr
from sqlalchemy import select
from test_classroom import FakeGoogle
from test_classroom_full import FullGoogle

from edutrack.google_classroom import GoogleClassroom, seal
from edutrack.integration_models import GoogleConnection
from edutrack.models import User


def build_integration_preview(path):
    if os.environ.get("EDUTRACK_QA_PREVIEW") != "1":
        raise RuntimeError("Esta prévia deve ser explicitamente ativada; nunca implantar.")
    app = build_preview(path, populate=os.environ.get("EDUTRACK_QA_EMPTY_ACCOUNT") != "1")
    settings = app.state.settings
    settings.classroom_enabled = True
    settings.classroom_full_import_enabled = os.environ.get("EDUTRACK_QA_FULL_CLASSROOM") == "1"
    settings.google_client_id = "cliente-ficticio.apps.googleusercontent.com"
    settings.google_client_secret = SecretStr("segredo-google-ficticio")
    settings.integration_encryption_key = SecretStr(Fernet.generate_key().decode())
    fake = FullGoogle() if settings.classroom_full_import_enabled else FakeGoogle()
    fail_first_search = os.environ.get("EDUTRACK_QA_CLASSROOM_FAIL_FIRST_SEARCH") == "1"

    def preview_transport(request):
        nonlocal fail_first_search
        if fail_first_search and request.url.path == "/v1/courses":
            fail_first_search = False
            return httpx.Response(503, json={"error": "Falha simulada da primeira busca"})
        return fake.handle(request)

    app.state.google_client_factory = lambda config: GoogleClassroom(config, httpx.MockTransport(preview_transport))
    with app.state.session_factory() as db:
        user = db.scalar(select(User))
        user.nome = "QA local — Google simulado"
        db.add(GoogleConnection(usuario_id=user.id, google_sub=fake.sub, email="google-simulado@example.com", refresh_cifrado=seal(settings, user.id, "refresh-ficticio"), versao=uuid4(), conteudo_autorizado=settings.classroom_full_import_enabled))
        db.commit()
    return app


if __name__ == "__main__":
    import uvicorn

    with TemporaryDirectory(prefix="edutrack-integrations-qa-") as directory:
        uvicorn.run(build_integration_preview(Path(directory) / "preview.db"), host="127.0.0.1", port=8014, access_log=False, proxy_headers=False)
