from datetime import timedelta

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import select

from edutrack.cpf import valid_cpf
from edutrack.email_delivery import EmailDeliveryError, send_verification
from edutrack.models import EmailVerification, User, utc_now

BODY = {"nome": "Conta de teste", "email": "verificacao@example.com", "senha": "senha-teste-isolado-123", "cpf": "00000000191"}
CREDENTIALS = {key: BODY[key] for key in ("email", "senha")}


@pytest.fixture
def verification(client):
    settings = client.app.state.settings
    settings.email_verification_enabled = True
    settings.sendgrid_api_key = SecretStr("chave-ficticia-sem-acesso")
    settings.email_from = "sender@example.com"
    mailbox = []
    client.app.state.email_sender = lambda settings, email, code: mailbox.append((email, code))
    assert client.post("/api/auth/register", json=BODY).status_code == 201
    return client, mailbox


def request_code(client):
    return client.post("/api/auth/request-verification", json=CREDENTIALS)


def confirm(client, code):
    return client.post("/api/auth/verify-email", json={**CREDENTIALS, "codigo": code})


@pytest.mark.parametrize("cpf", ["", "123", "11111111111", "00000000181", "00000000190", "123.123.123-12", "0000000019x"])
def test_invalid_cpf_rejected_without_echo(client, cpf):
    result = client.post("/api/auth/register", json={**BODY, "cpf": cpf})
    assert result.status_code == 422
    if cpf:
        assert cpf not in result.text


def test_cpf_format_and_discard(client):
    assert valid_cpf("000.000.001-91")
    assert not valid_cpf("00000000000")
    result = client.post("/api/auth/register", json=BODY)
    assert result.status_code == 201
    assert "cpf" not in result.json()
    assert "cpf" not in User.__table__.columns


def test_complete_flow_and_replay(verification):
    client, mailbox = verification
    blocked = client.post("/api/auth/login", json=CREDENTIALS)
    assert blocked.status_code == 403
    assert blocked.json()["detail"]["code"] == "EMAIL_VERIFICATION_REQUIRED"
    sent = request_code(client)
    assert sent.status_code == 202
    code = mailbox[-1][1]
    assert code not in sent.text
    with client.app.state.session_factory() as db:
        row = db.scalar(select(EmailVerification))
        assert row.codigo_hash != code and len(row.codigo_hash) == 64
    assert confirm(client, code).status_code == 200
    assert confirm(client, code).status_code == 400
    login = client.post("/api/auth/login", json=CREDENTIALS)
    assert login.status_code == 200
    assert client.get("/api/me", headers={"Authorization": "Bearer " + login.json()["access_token"]}).status_code == 200
    assert request_code(client).json()["already_verified"]
    assert len(mailbox) == 1


def test_resend_invalidates_previous_code_and_cooldown(verification, monkeypatch):
    client, mailbox = verification
    codes = iter([123456, 654321])
    monkeypatch.setattr("edutrack.email_verification.secrets.randbelow", lambda _: next(codes))
    assert request_code(client).status_code == 202
    old = mailbox[-1][1]
    assert request_code(client).status_code == 429
    with client.app.state.session_factory() as db:
        row = db.scalar(select(EmailVerification))
        row.enviado_em -= timedelta(seconds=61)
        db.commit()
    assert request_code(client).status_code == 202
    with client.app.state.session_factory() as db:
        assert db.scalar(select(EmailVerification)).versao == 2
    assert confirm(client, old).status_code == 400
    assert confirm(client, mailbox[-1][1]).status_code == 200


def test_five_failures_lock_code(verification):
    client, mailbox = verification
    assert request_code(client).status_code == 202
    code = mailbox[-1][1]
    wrong = "111111" if code != "111111" else "222222"
    for _ in range(5):
        assert confirm(client, wrong).status_code == 400
    assert confirm(client, code).status_code == 400


def test_expired_code_and_hourly_limit(verification):
    client, mailbox = verification
    request_code(client)
    with client.app.state.session_factory() as db:
        row = db.scalar(select(EmailVerification))
        row.expira_em = utc_now() - timedelta(seconds=1)
        row.enviado_em -= timedelta(seconds=61)
        row.envios = 5
        db.commit()
    assert confirm(client, mailbox[-1][1]).status_code == 400
    assert request_code(client).status_code == 429


def test_wrong_credentials_never_send(verification):
    client, mailbox = verification
    for route in ("request-verification", "verify-email"):
        body = {**CREDENTIALS, "senha": "incorreta"}
        if route == "verify-email":
            body["codigo"] = "123456"
        assert client.post("/api/auth/" + route, json=body).status_code == 401
    assert mailbox == []


def test_sendgrid_failure_is_not_success(verification):
    client, mailbox = verification
    def failing(*args):
        raise EmailDeliveryError("Não expor detalhes de credenciais")
    client.app.state.email_sender = failing
    result = request_code(client)
    assert result.status_code == 503 and "credenciais" not in result.text
    with client.app.state.session_factory() as db:
        assert db.scalar(select(EmailVerification)).codigo_hash is None
    assert request_code(client).status_code == 429


def test_unconfigured_disabled_and_readonly(client):
    assert request_code(client).status_code == 503
    client.app.state.settings.email_verification_enabled = True
    assert request_code(client).status_code == 503
    assert client.post("/api/auth/register", json=BODY).status_code == 503
    client.app.state.settings.db_writes_enabled = False
    assert confirm(client, "123456").status_code == 503


def test_existing_tokens_require_confirmation_when_enabled(client):
    from conftest import register_and_login
    auth = register_and_login(client)
    client.app.state.settings.email_verification_enabled = True
    assert client.get("/api/me", headers=auth).status_code == 403


@pytest.mark.parametrize("status", [202, 400, 401, 403, 429, 500, 302])
def test_sendgrid_adapter_contract(monkeypatch, client, status):
    settings = client.app.state.settings
    settings.sendgrid_api_key = SecretStr("chave-ficticia")
    settings.email_from = "sender@example.com"
    def handler(request):
        import json
        body = json.loads(request.content)
        assert request.url == "https://api.sendgrid.com/v3/mail/send"
        assert request.headers["Authorization"] == "Bearer chave-ficticia"
        assert body["personalizations"][0]["to"] == [{"email": "recipient@example.com"}]
        assert not body["tracking_settings"]["open_tracking"]["enable"]
        return httpx.Response(status)
    original = httpx.Client
    monkeypatch.setattr("edutrack.email_delivery.httpx.Client", lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs))
    if status == 202:
        send_verification(settings, "recipient@example.com", "123456")
    else:
        with pytest.raises(EmailDeliveryError):
            send_verification(settings, "recipient@example.com", "123456")
