"""Permissões testadas somente em SQLite descartável; nenhum e-mail real é enviado."""

from datetime import timedelta
from uuid import UUID

import pytest
from conftest import academic_data, register_and_login
from pydantic import SecretStr
from sqlalchemy import select

from edutrack.admin_access import claim_admin_invitation
from edutrack.models import AdminInvitation, EmailVerification, User, utc_now
from scripts.prepare_admin import reserve_admin

BODY = {"nome": "Admin de teste", "email": "admin@example.com", "senha": "senha-teste-admin-123", "cpf": "00000000191"}
CREDENTIALS = {key: BODY[key] for key in ("email", "senha")}


def invitation(db, email=BODY["email"], expired=False):
    now = utc_now()
    db.add(AdminInvitation(email=email, criado_em=now - timedelta(days=2), expira_em=now + timedelta(days=-1 if expired else 1)))
    db.commit()


def verified_admin(client, headers):
    user_id = UUID(client.get("/api/me", headers=headers).json()["id"])
    with client.app.state.session_factory() as db:
        db.get(User, user_id).role = "admin"
        db.add(EmailVerification(usuario_id=user_id, confirmado_em=utc_now()))
        db.commit()
    return user_id


def test_registration_and_profile_cannot_assign_role(client, auth):
    assert client.post("/api/auth/register", json={**BODY, "role": "admin"}).status_code == 422
    assert client.post("/api/auth/register", json=BODY).json()["role"] == "student"
    assert client.put("/api/me", headers=auth, json={"nome": "Aluno", "role": "admin"}).status_code == 422
    assert client.get("/api/me", headers=auth).json()["role"] == "student"


def test_admin_endpoint_authentication_and_live_revocation(client, auth):
    assert client.get("/api/admin/access").status_code == 401
    assert client.get("/api/admin/access", headers=auth).status_code == 403
    user_id = verified_admin(client, auth)
    # Token anterior funciona, pois o papel vem do banco, não de claims estáticos.
    response = client.get("/api/admin/access", headers=auth)
    assert response.status_code == 200
    assert response.json() == {"role": "admin", "email_verificado": True, "gestao_usuarios_disponivel": False}
    assert client.get("/api/me", headers=auth).json()["role"] == "admin"
    with client.app.state.session_factory() as db:
        db.get(User, user_id).role = "student"
        db.commit()
    assert client.get("/api/admin/access", headers=auth).status_code == 403


def test_unverified_admin_blocked_even_when_email_setting_disabled(client, auth):
    with client.app.state.session_factory() as db:
        db.scalar(select(User)).role = "admin"
        db.commit()
    assert client.get("/api/admin/access", headers=auth).status_code == 403


def test_admin_does_not_bypass_academic_ownership(client, auth):
    course, discipline, task = academic_data(client, auth)
    admin = register_and_login(client, 2)
    verified_admin(client, admin)
    for path, record in (("courses", course), ("disciplines", discipline), ("tasks", task)):
        assert client.get("/api/" + path, headers=admin).json()["total"] == 0
        assert client.get("/api/" + path + "/" + record["id"], headers=admin).status_code == 404


@pytest.mark.parametrize("expired,other_email", [(False, False), (True, False), (False, True)])
def test_invitation_requires_actual_verification_and_matching_email(client, expired, other_email):
    settings = client.app.state.settings
    settings.email_verification_enabled = True
    settings.sendgrid_api_key = SecretStr("chave-ficticia")
    settings.email_from = "sender@example.com"
    mailbox = []
    client.app.state.email_sender = lambda settings, email, code: mailbox.append(code)
    with client.app.state.session_factory() as db:
        invitation(db, "other@example.com" if other_email else BODY["email"], expired)
    registered = client.post("/api/auth/register", json=BODY)
    assert registered.json()["role"] == "student"
    assert client.post("/api/auth/login", json=CREDENTIALS).status_code == 403
    with client.app.state.session_factory() as db:
        user = db.scalar(select(User))
        assert not claim_admin_invitation(db, user)
        db.rollback()
    assert client.post("/api/auth/request-verification", json=CREDENTIALS).status_code == 202
    wrong = "000000" if mailbox[-1] != "000000" else "111111"
    assert client.post("/api/auth/verify-email", json={**CREDENTIALS, "codigo": wrong}).status_code == 400
    with client.app.state.session_factory() as db:
        assert db.scalar(select(User)).role == "student"
        assert db.scalar(select(AdminInvitation)).usado_em is None
    assert client.post("/api/auth/verify-email", json={**CREDENTIALS, "codigo": mailbox[-1]}).status_code == 200
    login = client.post("/api/auth/login", json=CREDENTIALS)
    expected = "student" if expired or other_email else "admin"
    assert login.json()["user"]["role"] == expected
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    assert client.get("/api/admin/access", headers=headers).status_code == (200 if expected == "admin" else 403)
    with client.app.state.session_factory() as db:
        user = db.scalar(select(User))
        user.role = "student"
        db.commit()
        assert not claim_admin_invitation(db, user)  # Uso único não desfaz revogação.
        db.rollback()


def test_operator_reservation_promotes_existing_verified_account_without_password_changes(client, auth):
    user_id = UUID(client.get("/api/me", headers=auth).json()["id"])
    with client.app.state.session_factory() as db:
        user = db.get(User, user_id)
        original = user.senha_hash
        db.add(EmailVerification(usuario_id=user_id, confirmado_em=utc_now()))
        db.commit()
        assert "promovida" in reserve_admin(db, user.email.upper())
        assert user.role == "admin" and user.senha_hash == original
        assert "já utilizada" in reserve_admin(db, user.email)


def test_operator_reservation_does_not_create_password_or_account(client):
    with client.app.state.session_factory() as db:
        assert "reservada" in reserve_admin(db, BODY["email"])
        assert db.scalar(select(User)) is None
        assert db.get(AdminInvitation, BODY["email"]).usado_em is None


def test_admin_documented_in_swagger(client):
    spec = client.get("/openapi.json").json()
    assert spec["paths"]["/api/admin/access"]["get"]["security"] == [{"HTTPBearer": []}]
    assert "role" not in spec["components"]["schemas"]["Registration"]["properties"]
