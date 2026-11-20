"""Contratos usados pela interface conectada, com banco isolado em memória."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from conftest import academic_data, register_and_login


def test_profile_updates_only_current_user(client, auth):
    other = register_and_login(client, 2)
    response = client.put("/api/me", headers=auth, json={"nome": "Nome atualizado"})
    assert response.status_code == 200
    assert client.get("/api/me", headers=auth).json()["nome"] == "Nome atualizado"
    assert client.get("/api/me", headers=other).json()["nome"] == "Aluno 2"
    assert client.put("/api/me", headers=auth, json={"nome": "X", "role": "admin"}).status_code == 422


def test_swagger_documents_authentication_and_alias(client):
    page = client.get("/docs")
    assert page.status_code == 200
    assert '"persistAuthorization": false' in page.text
    assert client.get("/swagger", follow_redirects=False).headers["location"] == "/docs"
    schema = client.get("/openapi.json").json()
    assert "Como testar" in schema["info"]["description"]
    assert schema["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
    assert schema["paths"]["/api/me"]["put"]["security"] == [{"HTTPBearer": []}]


def test_account_switch_does_not_write_in_another_account(client, auth):
    other = register_and_login(client, 2)
    old_user = client.get("/api/me", headers=auth).json()["id"]
    headers = {**other, "X-EduTrack-User": old_user}
    assert client.post("/api/courses", headers=headers, json={"nome": "Não criar"}).status_code == 409
    assert client.get("/api/courses", headers=other).json()["total"] == 0


def test_study_session_retry_is_idempotent(client, auth):
    _, _, task = academic_data(client, auth)
    end = datetime.now(timezone.utc).replace(microsecond=123000) - timedelta(seconds=5)
    body = {"tarefa_id": task["id"], "iniciado_em": (end - timedelta(minutes=25)).isoformat(), "finalizado_em": end.isoformat()}
    key = str(uuid4())
    headers = {**auth, "Idempotency-Key": key}
    first = client.post("/api/study-sessions", headers=headers, json=body)
    second = client.post("/api/study-sessions", headers=headers, json=body)
    assert first.status_code == second.status_code == 201
    assert first.json() == second.json()
    assert first.json()["id"] == key
    assert client.get("/api/study-sessions", headers=auth).json()["total"] == 1
    changed = {**body, "iniciado_em": (end - timedelta(minutes=30)).isoformat()}
    assert client.post("/api/study-sessions", headers=headers, json=changed).status_code == 409
    other = register_and_login(client, 2)
    _, _, other_task = academic_data(client, other)
    assert client.post("/api/study-sessions", headers={**other, "Idempotency-Key": key}, json={**body, "tarefa_id": other_task["id"]}).status_code == 409
    assert client.get("/api/study-sessions", headers=other).json()["total"] == 0
