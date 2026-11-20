"""E-mails capturados e SQLite em memória: nenhuma conta ou mensagem real é alterada."""
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

import pytest
from pydantic import SecretStr
from sqlalchemy import select

from edutrack.email_delivery import EmailDeliveryError
from edutrack.models import PasswordReset, utc_now

EMAIL = "aluno1@example.com"
NEW_PASSWORD = "Nova-senha-exclusiva-teste-123"


@pytest.fixture
def recovery(client, auth):
    settings = client.app.state.settings
    settings.password_reset_enabled = True
    settings.sendgrid_api_key = SecretStr("chave-ficticia")
    settings.email_from = "sender@example.com"
    mailbox = []
    client.app.state.password_reset_sender = lambda settings, email, link: mailbox.append((email, link))
    return client, auth, mailbox


def token_from(mailbox):
    link = mailbox[-1][1]
    assert not urlsplit(link).query
    return parse_qs(urlsplit(link).fragment)["token"][0]


def request_link(client, email=EMAIL):
    return client.post("/api/auth/forgot-password", json={"email": email})


def confirm(client, token):
    return client.post("/api/auth/reset-password", json={"token": token, "senha": NEW_PASSWORD})


def test_complete_reset_revokes_existing_session_and_preserves_account(recovery):
    client, old_session, mailbox = recovery
    before = client.get("/api/me", headers=old_session).json()
    response = request_link(client)
    assert response.status_code == 202
    token = token_from(mailbox)
    assert token not in response.text
    with client.app.state.session_factory() as db:
        record = db.scalar(select(PasswordReset))
        assert record.token_hash != token and len(record.token_hash) == 64
    assert confirm(client, token).status_code == 200
    assert confirm(client, token).status_code == 400
    assert client.get("/api/me", headers=old_session).status_code == 401
    assert client.post("/api/auth/login", json={"email": EMAIL, "senha": "Senha-forte-exemplo-123"}).status_code == 401
    login = client.post("/api/auth/login", json={"email": EMAIL, "senha": NEW_PASSWORD})
    assert login.status_code == 200
    assert login.json()["user"]["id"] == before["id"]
    assert login.json()["user"]["role"] == before["role"]


def test_unknown_email_is_indistinguishable_and_not_sent(recovery):
    client, _, mailbox = recovery
    known = request_link(client)
    unknown = request_link(client, "inexistente@example.com")
    assert known.status_code == unknown.status_code == 202
    assert known.json() == unknown.json()
    assert len(mailbox) == 1


def test_expired_or_random_token_does_not_change_password(recovery):
    client, auth, mailbox = recovery
    request_link(client)
    token = token_from(mailbox)
    with client.app.state.session_factory() as db:
        record = db.scalar(select(PasswordReset))
        record.criado_em = utc_now() - timedelta(minutes=30)
        record.expira_em = utc_now() - timedelta(minutes=1)
        db.commit()
    assert confirm(client, token).status_code == 400
    assert confirm(client, "a" * 43).status_code == 400
    assert client.get("/api/me", headers=auth).status_code == 200


def test_resend_cooldown_and_new_link_invalidates_previous(recovery):
    client, _, mailbox = recovery
    request_link(client)
    old = token_from(mailbox)
    assert request_link(client).status_code == 202
    assert len(mailbox) == 1
    with client.app.state.session_factory() as db:
        record = db.scalar(select(PasswordReset))
        record.criado_em = utc_now() - timedelta(minutes=2)
        db.commit()
    request_link(client)
    assert len(mailbox) == 2
    assert confirm(client, old).status_code == 400
    assert confirm(client, token_from(mailbox)).status_code == 200


def test_delivery_failure_does_not_expose_account_or_leave_valid_token(recovery):
    client, _, _ = recovery
    def fail(*args):
        raise EmailDeliveryError("erro fictício")
    client.app.state.password_reset_sender = fail
    assert request_link(client).status_code == 202
    with client.app.state.session_factory() as db:
        assert db.scalar(select(PasswordReset)).usado_em is not None


def test_disabled_reset_and_database_writes_are_respected(client):
    assert request_link(client).status_code == 503
    client.app.state.settings.db_writes_enabled = False
    assert confirm(client, "a" * 43).status_code == 503


def test_invalid_body_is_sanitized_and_rate_limit_applies(recovery):
    client, _, _ = recovery
    response = client.post("/api/auth/reset-password", json={"token": "segredo-invalido", "senha": "curta"})
    assert response.status_code == 422
    assert "segredo-invalido" not in response.text
    assert "curta" not in response.text
    for _ in range(3):
        assert request_link(client, "desconhecido@example.com").status_code == 202
    assert request_link(client, "desconhecido@example.com").status_code == 429


def test_reset_does_not_verify_email(recovery):
    client, auth, mailbox = recovery
    request_link(client)
    client.app.state.settings.email_verification_enabled = True
    assert confirm(client, token_from(mailbox)).status_code == 200
    response = client.post("/api/auth/login", json={"email": EMAIL, "senha": NEW_PASSWORD})
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "EMAIL_VERIFICATION_REQUIRED"
