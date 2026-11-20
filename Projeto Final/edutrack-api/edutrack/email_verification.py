"""Confirmação de conta com desafio de uso único e limites persistidos no banco."""

import hashlib
import hmac
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from edutrack.closed_access import require_closed_invitation
from edutrack.database import get_db, require_writes
from edutrack.email_delivery import EmailDeliveryError
from edutrack.models import EmailVerification, User, utc_now
from edutrack.schemas import EmailConfirmation, Login
from edutrack.security import DUMMY_HASH, limit_auth, password_hasher

router = APIRouter(prefix="/api/auth", tags=["Verificação de e-mail"])
REQUIRED = {"code": "EMAIL_VERIFICATION_REQUIRED", "message": "Confirme seu e-mail antes de entrar."}


def require_verified(request, db, user):
    if request.app.state.settings.email_verification_enabled:
        record = db.get(EmailVerification, user.id)
        if not record or not record.confirmado_em:
            raise HTTPException(403, REQUIRED)


def authenticate(db, body):
    user = db.scalar(select(User).where(User.email == str(body.email).lower()))
    valid = password_hasher.verify(body.senha.get_secret_value(), user.senha_hash if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, "E-mail ou senha inválidos.")
    return user


def code_digest(request, user_id, version, code):
    return hmac.new(
        request.app.state.jwt_secret.encode(),
        f"edutrack-email:{user_id}:{version}:{code}".encode(),
        hashlib.sha256,
    ).hexdigest()


def enabled(request):
    if not request.app.state.settings.email_verification_enabled:
        raise HTTPException(503, "Verificação por e-mail ainda não ativada neste servidor.")


@router.get("/options")
def options(request: Request):
    settings = request.app.state.settings
    return {
        "restricted_adults_mode": settings.closed_adult_access,
        "registration_enabled": not settings.closed_adult_access,
        "email_verification_required": settings.email_verification_enabled or settings.closed_adult_access,
        "email_delivery_configured": settings.email_configured,
        "password_reset_available": settings.password_reset_enabled and settings.email_configured,
        "cpf_validation": "digitos_verificadores_sem_armazenamento",
    }


@router.post("/request-verification", status_code=202, dependencies=[Depends(limit_auth), Depends(require_writes)])
def request_verification(body: Login, request: Request, db=Depends(get_db)):
    enabled(request)
    if not request.app.state.settings.email_configured:
        raise HTTPException(503, "SendGrid não configurado. Solicite a configuração ao responsável pelo EduTrack.")
    user = authenticate(db, body)
    require_closed_invitation(request, user)
    record = db.get(EmailVerification, user.id)
    if record is None:
        record = EmailVerification(usuario_id=user.id)
        db.add(record)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(429, "Solicitação em andamento. Aguarde e tente novamente.") from None
    if record.confirmado_em:
        return {"message": "Sua conta já está confirmada. Faça login.", "already_verified": True}
    now = utc_now()
    if record.enviado_em and record.enviado_em > now - timedelta(seconds=60):
        raise HTTPException(429, "Aguarde 60 segundos entre os envios.", headers={"Retry-After": "60"})
    same_window = record.janela_em and record.janela_em > now - timedelta(hours=1)
    if same_window and record.envios >= 5:
        raise HTTPException(429, "Limite de cinco envios por hora atingido.", headers={"Retry-After": "3600"})
    code = f"{secrets.randbelow(1_000_000):06d}"
    version = record.versao + 1
    # A reserva é atômica: requisições concorrentes não podem ultrapassar os limites.
    result = db.execute(update(EmailVerification).where(
        EmailVerification.usuario_id == user.id,
        EmailVerification.versao == record.versao,
        EmailVerification.confirmado_em.is_(None),
    ).values(
        versao=version, codigo_hash=code_digest(request, user.id, version, code),
        expira_em=now + timedelta(minutes=10), tentativas=0, enviado_em=now,
        janela_em=record.janela_em if same_window else now,
        envios=record.envios + 1 if same_window else 1,
    ).execution_options(synchronize_session=False))
    db.commit()
    if result.rowcount != 1:
        raise HTTPException(429, "Solicitação em andamento. Aguarde e tente novamente.")
    try:
        request.app.state.email_sender(request.app.state.settings, user.email, code)
    except EmailDeliveryError:
        # Código de envio falho/ambíguo não é utilizável. Preservar o limite de reenvio.
        db.execute(update(EmailVerification).where(
            EmailVerification.usuario_id == user.id, EmailVerification.versao == version,
            EmailVerification.confirmado_em.is_(None),
        ).values(codigo_hash=None, expira_em=None))
        db.commit()
        raise HTTPException(503, "Não foi possível enviar o código. Confira a configuração do SendGrid e tente reenviar após 60 segundos.") from None
    return {"message": "Código aceito pelo serviço de envio. Confira sua caixa de entrada e spam.", "expires_in": 600, "resend_after": 60}


@router.post("/verify-email", dependencies=[Depends(limit_auth), Depends(require_writes)])
def verify_email(body: EmailConfirmation, request: Request, db=Depends(get_db)):
    enabled(request)
    user = authenticate(db, body)
    require_closed_invitation(request, user)
    record = db.get(EmailVerification, user.id)
    now = utc_now()
    invalid = HTTPException(400, "Código inválido, expirado ou já utilizado. Solicite um novo código se necessário.")
    if not record or record.confirmado_em or not record.codigo_hash or not record.expira_em or record.expira_em <= now or record.tentativas >= 5:
        raise invalid
    correct = hmac.compare_digest(record.codigo_hash, code_digest(request, user.id, record.versao, body.codigo))
    values = {"tentativas": EmailVerification.tentativas + 1}
    if correct:
        values.update(confirmado_em=now, codigo_hash=None, expira_em=None)
    result = db.execute(update(EmailVerification).where(
        EmailVerification.usuario_id == user.id,
        EmailVerification.versao == record.versao,
        EmailVerification.confirmado_em.is_(None),
        EmailVerification.codigo_hash == record.codigo_hash,
        EmailVerification.tentativas < 5,
        EmailVerification.expira_em > now,
    ).values(**values).execution_options(synchronize_session=False))
    if result.rowcount == 1 and correct:
        # A confirmação e a concessão autorizada são atômicas: sem promoção parcial.
        from edutrack.admin_access import claim_admin_invitation

        claim_admin_invitation(db, user)
    db.commit()
    if result.rowcount != 1 or not correct:
        raise invalid
    return {"message": "E-mail confirmado. Você já pode entrar no EduTrack."}
