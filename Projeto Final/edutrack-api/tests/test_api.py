from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from conftest import academic_data, register_and_login
from sqlalchemy import select

from edutrack.models import User
from edutrack.security import RateLimiter


@pytest.mark.parametrize(
    "path",
    [
        "/api/me",
        "/api/courses",
        "/api/disciplines",
        "/api/tasks",
        "/api/edu-ia/context",
        "/api/study-sessions",
        "/api/dashboard",
    ],
)
def test_authentication_required(client, path):
    assert client.get(path).status_code == 401


def test_registration_login_password_hash(client, auth):
    me = client.get("/api/me", headers=auth)
    assert me.json()["role"] == "student"
    assert "senha_hash" not in me.text
    with client.app.state.session_factory() as db:
        user = db.scalar(select(User))
        assert user.senha_hash.startswith("$argon2id$")
    duplicate = client.post(
        "/api/auth/register",
        json={"nome": "Aluno", "email": "ALUNO1@example.com", "senha": "Senha-forte-exemplo-123", "cpf": "00000000191"},
    )
    assert duplicate.status_code == 409
    for email in ("aluno1@example.com", "inexistente@example.com"):
        denied = client.post("/api/auth/login", json={"email": email, "senha": "incorreta"})
        assert denied.status_code == 401
        assert denied.json()["detail"] == "E-mail ou senha inválidos."


def test_registration_cannot_escalate(client):
    response = client.post(
        "/api/auth/register",
        json={
            "nome": "Aluno",
            "email": "teste@example.com",
            "senha": "Senha-forte-exemplo-123",
            "role": "admin",
        },
    )
    assert response.status_code == 422
    assert "Senha-forte" not in response.text
    assert client.get("/api/admin/users").status_code == 404


def test_validation_does_not_echo_secrets(client):
    response = client.post(
        "/api/auth/register", json={"nome": "Aluno", "email": "email-invalido", "senha": "segredo"}
    )
    assert response.status_code == 422
    assert "segredo" not in response.text
    assert "email-invalido" not in response.text


def test_crud_and_completion(client, auth):
    course, discipline, task = academic_data(client, auth)
    for resource, obj in (("courses", course), ("disciplines", discipline), ("tasks", task)):
        assert client.get(f"/api/{resource}/{obj['id']}", headers=auth).status_code == 200
        assert client.get(f"/api/{resource}", headers=auth).json()["total"] == 1
    update = {"nome": "Curso atualizado", "instituicao": "Faculdade"}
    assert (
        client.put(f"/api/courses/{course['id']}", headers=auth, json=update).json()["nome"]
        == "Curso atualizado"
    )
    assert (
        client.put(
            f"/api/disciplines/{discipline['id']}",
            headers=auth,
            json={"nome": "SQL", "curso_id": course["id"], "carga_horaria": 80},
        ).status_code
        == 200
    )
    update = {"titulo": "Modelo revisado", "disciplina_id": discipline["id"], "status": "concluida"}
    done = client.put(f"/api/tasks/{task['id']}", headers=auth, json=update)
    assert done.status_code == 200
    assert done.json()["concluido_em"] is not None
    assert client.get("/api/dashboard", headers=auth).json()["progresso_percentual"] == 100
    update["status"] = "pendente"
    assert (
        client.put(f"/api/tasks/{task['id']}", headers=auth, json=update).json()["concluido_em"]
        is None
    )
    assert client.delete(f"/api/courses/{course['id']}", headers=auth).status_code == 409
    assert client.delete(f"/api/disciplines/{discipline['id']}", headers=auth).status_code == 409
    for resource, obj in (("tasks", task), ("disciplines", discipline), ("courses", course)):
        assert client.delete(f"/api/{resource}/{obj['id']}", headers=auth).status_code == 204
        assert client.get(f"/api/{resource}/{obj['id']}", headers=auth).status_code == 404


def test_user_isolation_for_all_resources(client, auth):
    course, discipline, task = academic_data(client, auth)
    other = register_and_login(client, 2)
    bodies = {
        "courses": {"nome": "Tentativa"},
        "disciplines": {"nome": "Tentativa", "curso_id": course["id"]},
        "tasks": {"titulo": "Tentativa", "disciplina_id": discipline["id"]},
    }
    for resource, obj in (("courses", course), ("disciplines", discipline), ("tasks", task)):
        assert client.get(f"/api/{resource}", headers=other).json()["items"] == []
        assert client.get(f"/api/{resource}/{obj['id']}", headers=other).status_code == 404
        assert (
            client.put(
                f"/api/{resource}/{obj['id']}", headers=other, json=bodies[resource]
            ).status_code
            == 404
        )
        assert client.delete(f"/api/{resource}/{obj['id']}", headers=other).status_code == 404
    assert (
        client.post("/api/disciplines", headers=other, json=bodies["disciplines"]).status_code
        == 404
    )
    assert client.post("/api/tasks", headers=other, json=bodies["tasks"]).status_code == 404
    assert client.get("/api/edu-ia/context", headers=other).json()["tarefas"] == []
    assert client.get("/api/dashboard", headers=other).json()["cursos"] == 0


def test_owner_injection_rejected(client, auth):
    response = client.post(
        "/api/courses", headers=auth, json={"nome": "Teste", "usuario_id": str(uuid4())}
    )
    assert response.status_code == 422


def test_time_entry_and_history_preserved(client, auth):
    _, _, task = academic_data(client, auth)
    end = datetime.now(timezone.utc) - timedelta(minutes=1)
    body = {
        "tarefa_id": task["id"],
        "iniciado_em": (end - timedelta(minutes=25)).isoformat(),
        "finalizado_em": end.isoformat(),
    }
    assert (
        client.post("/api/study-sessions", headers=auth, json=body).json()["duracao_minutos"] == 25
    )
    assert client.get("/api/study-sessions", headers=auth).json()["total"] == 1
    assert client.get("/api/dashboard", headers=auth).json()["minutos_estudados"] == 25
    assert client.delete(f"/api/tasks/{task['id']}", headers=auth).status_code == 409
    other = register_and_login(client, 2)
    assert client.post("/api/study-sessions", headers=other, json=body).status_code == 404
    assert client.get("/api/study-sessions", headers=other).json()["items"] == []


def test_constraints_and_pagination(client, auth):
    assert client.post("/api/courses", headers=auth, json={"nome": "  "}).status_code == 422
    assert (
        client.post(
            "/api/courses",
            headers=auth,
            json={"nome": "Teste", "data_inicio": "2030-02-01", "data_fim": "2030-01-01"},
        ).status_code
        == 422
    )
    assert client.get("/api/tasks?limit=10000", headers=auth).status_code == 422
    assert client.get("/api/tasks?status=nao_existe", headers=auth).status_code == 422
    assert client.get("/api/courses/id-invalido", headers=auth).status_code == 422
    for name in ("A", "B", "C"):
        client.post("/api/courses", headers=auth, json={"nome": name})
    first = client.get("/api/courses?limit=2", headers=auth).json()
    second = client.get("/api/courses?limit=2&offset=2", headers=auth).json()
    assert first["total"] == 3 and len(first["items"]) == 2 and len(second["items"]) == 1


def test_read_only_guard(client, auth):
    client.app.state.settings.db_writes_enabled = False
    assert client.post("/api/courses", headers=auth, json={"nome": "Bloqueado"}).status_code == 503
    assert (
        client.post(
            "/api/auth/register",
            json={"nome": "Aluno", "email": "novo@example.com", "senha": "Senha-forte-1234"},
        ).status_code
        == 503
    )
    assert client.get("/api/courses", headers=auth).json()["items"] == []


def test_expired_or_invalid_tokens(client, auth):
    for token in ("token-invalido", auth["Authorization"][7:] + "invalid"):
        assert (
            client.get("/api/me", headers={"Authorization": "Bearer " + token}).status_code == 401
        )
    claims = jwt.decode(auth["Authorization"][7:], options={"verify_signature": False})
    claims["exp"] = 1
    expired = jwt.encode(claims, client.app.state.jwt_secret, algorithm="HS256")
    assert client.get("/api/me", headers={"Authorization": "Bearer " + expired}).status_code == 401


def test_health_openapi_headers_and_body_size(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").status_code == 200
    assert client.get("/docs").status_code == 200
    assert "/api/edu-ia/study-plan" in client.get("/openapi.json").json()["paths"]
    assert client.get("/health").headers["cache-control"] == "no-store"
    assert client.post("/api/auth/login", content=b"a" * 70000).status_code == 413
    assert (
        client.post("/api/auth/login", content=iter([b"a" * 40000, b"b" * 40000])).status_code
        == 413
    )


def test_limiter():
    from fastapi import HTTPException

    limiter = RateLimiter()
    limiter.check("user", 1, 60)
    with pytest.raises(HTTPException) as raised:
        limiter.check("user", 1, 60)
    assert raised.value.status_code == 429


def test_cors(client):
    for origin, allowed in (("http://localhost:3002", True), ("https://invasor.example", False)):
        response = client.options(
            "/api/courses", headers={"Origin": origin, "Access-Control-Request-Method": "GET"}
        )
        assert ("access-control-allow-origin" in response.headers) is allowed
