from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from conftest import academic_data
from fastapi.testclient import TestClient
from pydantic import ValidationError

from edutrack.config import Settings
from edutrack.main import create_app
from edutrack.schemas import PlanInput, TimeEntryInput


def test_dates_return_utc(client, auth):
    _, _, task = academic_data(client, auth)
    assert task["data_prevista"] == "2030-01-02T23:00:00Z"
    assert task["criado_em"].endswith("Z")
    assert client.get("/api/me", headers=auth).json()["criado_em"].endswith("Z")
    assert client.get("/api/courses", headers=auth).json()["items"][0]["criado_em"].endswith("Z")


@pytest.mark.parametrize("minutes", [0, -1, 241])
def test_session_invalid_duration(minutes):
    end = datetime.now(timezone.utc) - timedelta(minutes=1)
    with pytest.raises(ValidationError):
        TimeEntryInput(
            tarefa_id=uuid4(), iniciado_em=end - timedelta(minutes=minutes), finalizado_em=end
        )


def test_future_session_rejected():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        TimeEntryInput(
            tarefa_id=uuid4(), iniciado_em=now, finalizado_em=now + timedelta(minutes=25)
        )


def test_invalid_plan_date_horizon():
    with pytest.raises(ValidationError):
        PlanInput(data_inicio="9999-12-31", dias=14)


@pytest.mark.parametrize(
    "extra",
    [
        {"jwt_secret": None},
        {"jwt_secret": "curta"},
        {"trust_server_certificate": True},
        {"cors_origins": ["*"]},
        {"cors_origins": ["http://localhost:3002"]},
    ],
)
def test_unsafe_production_settings_rejected(extra):
    options = {
        "environment": "production",
        "jwt_secret": "chave-ficticia-so-de-teste-com-mais-de-32-caracteres",
        "trust_server_certificate": False,
        "cors_origins": ["https://edutrack.example.com"],
    }
    options.update(extra)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **options)


def test_swagger_hidden_in_production():
    settings = Settings(
        _env_file=None,
        environment="production",
        jwt_secret="chave-ficticia-so-de-teste-com-mais-de-32-caracteres",
        cors_origins=["https://edutrack.example.com"],
        frontend_url="https://edutrack.example.com",
        trust_server_certificate=False,
    )
    # Não conecta ao banco: o engine só abre conexão quando consultado.
    with TestClient(create_app(settings)) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_completed_tasks_excluded_from_context(client, auth):
    _, discipline, task = academic_data(client, auth)
    updated = client.put(
        f"/api/tasks/{task['id']}",
        headers=auth,
        json={"titulo": "Concluída", "disciplina_id": discipline["id"], "status": "concluida"},
    )
    assert updated.status_code == 200
    assert client.get("/api/edu-ia/context", headers=auth).json()["tarefas"] == []


def test_rate_limit_login_endpoint(client):
    for _ in range(15):
        assert (
            client.post(
                "/api/auth/login", json={"email": "ninguem@example.com", "senha": "incorreta"}
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/auth/login", json={"email": "ninguem@example.com", "senha": "incorreta"}
        ).status_code
        == 429
    )
