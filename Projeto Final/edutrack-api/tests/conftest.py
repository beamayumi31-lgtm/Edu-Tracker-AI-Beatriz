import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from edutrack.config import Settings
from edutrack.main import create_app
from edutrack.models import Base


@pytest.fixture
def client():
    # Exclusivamente SQLite em memória. Nunca usar a configuração real nestes testes.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    settings = Settings(
        _env_file=None,
        environment="test",
        db_writes_enabled=True,
        jwt_secret="chave-exclusiva-de-testes-sem-validade-fora-dos-testes",
        OPENAI_API_KEY=None,
        OPENAI_MODEL=None,
        ai_provider="openai",
        GEMINI_API_KEY=None,
        GEMINI_MODEL=None,
        classroom_enabled=False,
        gemini_paid_service=False,
        email_verification_enabled=False,
        SENDGRID_API_KEY=None,
        email_from=None,
    )
    app = create_app(settings, engine)
    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client, number=1):
    body = {
        "nome": f"Aluno {number}",
        "email": f"aluno{number}@example.com",
        "senha": "Senha-forte-exemplo-123",
        "cpf": "00000000191",
    }
    response = client.post("/api/auth/register", json=body)
    assert response.status_code == 201, response.text
    token = client.post("/api/auth/login", json={"email": body["email"], "senha": body["senha"]})
    assert token.status_code == 200, token.text
    return {"Authorization": "Bearer " + token.json()["access_token"]}


@pytest.fixture
def auth(client):
    return register_and_login(client)


def academic_data(client, auth):
    course = client.post("/api/courses", headers=auth, json={"nome": "Ciência da Computação"})
    assert course.status_code == 201, course.text
    discipline = client.post(
        "/api/disciplines",
        headers=auth,
        json={"nome": "Banco de Dados", "curso_id": course.json()["id"]},
    )
    assert discipline.status_code == 201, discipline.text
    task = client.post(
        "/api/tasks",
        headers=auth,
        json={
            "titulo": "Modelo relacional",
            "disciplina_id": discipline.json()["id"],
            "data_prevista": "2030-01-02T20:00:00-03:00",
            "minutos_estimados": 90,
        },
    )
    assert task.status_code == 201, task.text
    return course.json(), discipline.json(), task.json()
