from uuid import UUID

import pytest
from conftest import register_and_login
from pydantic import SecretStr

from edutrack.config import Settings
from edutrack.models import EmailVerification, utc_now


def close(client, emails):
    s = client.app.state.settings
    s.closed_adult_access = True
    s.ai_audience = "adults_only"
    s.adult_access_emails = emails


def verify(client, auth):
    uid = UUID(client.get("/api/me", headers=auth).json()["id"])
    with client.app.state.session_factory() as db:
        db.add(EmailVerification(usuario_id=uid, confirmado_em=utc_now()))
        db.commit()


def test_closed_default_unchanged_and_options_do_not_expose_list(client):
    options = client.get("/api/auth/options").json()
    assert options["registration_enabled"] and not options["restricted_adults_mode"]
    close(client, ["private@example.com"])
    options = client.get("/api/auth/options").json()
    assert not options["registration_enabled"] and options["restricted_adults_mode"]
    assert "private@example.com" not in str(options)


def test_closed_denies_all_registration_even_allowlisted(client):
    close(client, ["adult@example.com"])
    response = client.post("/api/auth/register", json={"nome": "Adult", "email": "adult@example.com", "senha": "test-password-123", "cpf": "00000000191"})
    assert response.status_code == 403


@pytest.mark.parametrize("path", ["/api/me", "/api/courses", "/api/disciplines", "/api/tasks", "/api/study-sessions", "/api/dashboard", "/api/edu-ia/status", "/api/edu-ia/context", "/api/integrations/google/status", "/api/admin/access"])
def test_old_sessions_cannot_bypass_closed_access(client, auth, path):
    close(client, [])
    r = client.get(path, headers=auth)
    assert r.status_code == 403 and r.json()["detail"]["code"] == "CLOSED_ACCESS_REQUIRED"


def test_only_allowlisted_verified_adults_login_and_revocation_is_immediate(client, auth):
    verify(client, auth)
    other = register_and_login(client, 2)
    verify(client, other)
    close(client, ["ALUNO1@example.com"])
    body = {"email": "aluno1@example.com", "senha": "Senha-forte-exemplo-123"}
    assert client.post("/api/auth/login", json=body).status_code == 200
    assert client.get("/api/me", headers=auth).status_code == 200
    assert client.post("/api/auth/login", json={**body, "email": "aluno2@example.com"}).status_code == 403
    assert client.get("/api/me", headers=other).status_code == 403
    client.app.state.settings.adult_access_emails = []
    assert client.get("/api/me", headers=auth).status_code == 403


def test_unverified_allowlisted_account_denied_even_when_email_feature_off(client, auth):
    close(client, ["aluno1@example.com"])
    assert not client.app.state.settings.email_verification_enabled
    r = client.get("/api/me", headers=auth)
    assert r.status_code == 403 and r.json()["detail"]["code"] == "EMAIL_VERIFICATION_REQUIRED"
    assert client.post("/api/auth/login", json={"email": "aluno1@example.com", "senha": "Senha-forte-exemplo-123"}).status_code == 403


def test_wrong_audience_fails_closed(client, auth):
    verify(client, auth)
    close(client, ["aluno1@example.com"])
    client.app.state.settings.ai_audience = "includes_teens"
    assert client.get("/api/me", headers=auth).status_code == 403


def test_google_and_ai_actions_denied_before_external_clients(client, auth, monkeypatch):
    close(client, [])
    def unexpected(*args, **kwargs):
        raise AssertionError("No external client may be created")
    client.app.state.google_client_factory = unexpected
    monkeypatch.setattr("edutrack.ai_routes.GeminiClient", unexpected)
    for path, body in [("/api/integrations/google/start", {}),
                       ("/api/integrations/google/callback", {"state": "x" * 32, "code": "synthetic"}),
                       ("/api/edu-ia/chat", {"messages": [{"role": "user", "text": "SQL?"}], "enviar_dados_ia": True, "maior_de_idade": True})]:
        assert client.post(path, json=body, headers=auth).status_code == 403


def test_production_gemini_requires_closed_nonempty_adult_allowlist():
    s = Settings(_env_file=None, environment="production", jwt_secret="test-only-secret-never-used-123456789", frontend_url="https://example.com", cors_origins=["https://example.com"], ai_provider="gemini", ai_audience="adults_only", gemini_enabled=True, GEMINI_API_KEY="synthetic-key", GEMINI_MODEL="synthetic-model")
    assert not s.ai_configured
    s.closed_adult_access = True
    assert not s.ai_configured
    s.adult_access_emails = ["adult@example.com"]
    assert s.ai_configured


def test_closed_gemini_context_stays_off_even_with_paid_flag():
    s = Settings(_env_file=None, ai_provider="gemini", closed_adult_access=True, gemini_paid_service=True)
    assert not s.ai_context_allowed


def test_invited_account_verifies_email_without_reopening_signup(client, auth):
    s = client.app.state.settings
    s.email_verification_enabled = True
    s.sendgrid_api_key = SecretStr("synthetic-test-key")
    s.email_from = "sender@example.com"
    mailbox = []
    client.app.state.email_sender = lambda settings, email, code: mailbox.append((email, code))
    close(client, ["aluno1@example.com"])
    body = {"email": "aluno1@example.com", "senha": "Senha-forte-exemplo-123"}
    assert client.get("/api/me", headers=auth).status_code == 403
    assert client.post("/api/auth/request-verification", json=body).status_code == 202
    assert len(mailbox) == 1
    assert client.post("/api/auth/verify-email", json={**body, "codigo": mailbox[0][1]}).status_code == 200
    assert client.post("/api/auth/login", json=body).status_code == 200
    assert client.get("/api/me", headers=auth).status_code == 200
    assert not client.get("/api/auth/options").json()["registration_enabled"]


def test_excluded_account_cannot_request_email_verification(client, auth):
    s = client.app.state.settings
    s.email_verification_enabled = True
    s.sendgrid_api_key = SecretStr("synthetic-test-key")
    s.email_from = "sender@example.com"
    mailbox = []
    client.app.state.email_sender = lambda *args: mailbox.append(args)
    close(client, [])
    body = {"email": "aluno1@example.com", "senha": "Senha-forte-exemplo-123"}
    assert client.post("/api/auth/request-verification", json=body).status_code == 403
    assert not mailbox
