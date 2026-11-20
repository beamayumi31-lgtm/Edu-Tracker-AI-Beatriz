"""Recuperação por link opaco de uso único; respostas não enumeram contas."""

import hashlib
import hmac
import logging
import secrets
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import EmailStr, Field, SecretStr
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from edutrack.database import require_writes
from edutrack.email_delivery import EmailDeliveryError
from edutrack.models import PasswordReset, User, utc_now
from edutrack.schemas import Contract
from edutrack.security import password_hasher

router = APIRouter(prefix="/api/auth", tags=["Recuperação de senha"], dependencies=[Depends(require_writes)])
NOTICE = "Se houver uma conta com esse e-mail, você receberá um link para redefinir a senha. Confira também o spam."


class ResetRequest(Contract):
    email: EmailStr = Field(max_length=255)


class ResetConfirm(Contract):
    token: str = Field(pattern=r"^[A-Za-z0-9_-]{43}$")
    senha: SecretStr = Field(min_length=10, max_length=128)


def require_reset(request: Request):
    settings = request.app.state.settings
    if not settings.password_reset_enabled or not settings.email_configured:
        raise HTTPException(503, "Recuperação por e-mail temporariamente indisponível.")


def prepare_and_send(app, email: str):
    # A tarefa começa após a mesma resposta 202 para e-mails existentes e desconhecidos.
    # Em múltiplas instâncias, usar fila persistente e limitador distribuído.
    try:
        with app.state.session_factory() as db:
            user = db.scalar(select(User).where(User.email == email))
            if not user:
                return
            now = utc_now()
            recent = db.scalar(select(PasswordReset.id).where(
                PasswordReset.usuario_id == user.id, PasswordReset.criado_em > now - timedelta(seconds=60)
            ).limit(1))
            if recent:
                return
            token = secrets.token_urlsafe(32)
            # Qualquer link anterior deixa de valer; não alterar a senha nesta etapa.
            db.execute(update(PasswordReset).where(
                PasswordReset.usuario_id == user.id, PasswordReset.usado_em.is_(None)
            ).values(usado_em=now))
            record = PasswordReset(usuario_id=user.id, token_hash=hashlib.sha256(token.encode()).hexdigest(),
                                   criado_em=now, expira_em=now + timedelta(minutes=15))
            db.add(record)
            db.commit()
            # Fragmento não vai aos logs HTTP do servidor de páginas nem ao Referer.
            link = app.state.settings.frontend_url.rstrip("/") + "/recuperar-senha#token=" + token
            try:
                app.state.password_reset_sender(app.state.settings, user.email, link)
            except EmailDeliveryError:
                record.usado_em = utc_now()
                db.commit()
                logging.getLogger("edutrack").warning("Não foi possível entregar um e-mail de recuperação.")
    except SQLAlchemyError:
        logging.getLogger("edutrack").error("Recuperação não concluída: banco indisponível.")


@router.post("/forgot-password", status_code=202, dependencies=[Depends(require_reset)])
def forgot_password(body: ResetRequest, request: Request, background: BackgroundTasks):
    email = str(body.email).lower()
    host = request.client.host if request.client else "local"
    request.app.state.limiter.check("reset-ip:" + host, 10, 900)
    # E-mails não ficam em texto nas chaves de limitação.
    digest = hmac.new(request.app.state.jwt_secret.encode(), email.encode(), hashlib.sha256).hexdigest()
    request.app.state.limiter.check("reset-email:" + digest, 3, 900)
    background.add_task(prepare_and_send, request.app, email)
    return {"message": NOTICE}


@router.post("/reset-password", dependencies=[Depends(require_reset)])
def reset_password(body: ResetConfirm, request: Request):
    host = request.client.host if request.client else "local"
    request.app.state.limiter.check("reset-confirm:" + host, 10, 900)
    digest = hashlib.sha256(body.token.encode()).hexdigest()
    now = utc_now()
    invalid = HTTPException(400, "Link inválido, expirado ou já utilizado. Solicite um novo link.")
    with request.app.state.session_factory() as db:
        record = db.scalar(select(PasswordReset).where(PasswordReset.token_hash == digest))
        if not record or record.usado_em is not None or record.expira_em <= now:
            raise invalid
        new_hash = password_hasher.hash(body.senha.get_secret_value())
        # Consumo condicional e senha na mesma transação: duas tentativas não reutilizam o token.
        consumed = db.execute(update(PasswordReset).where(
            PasswordReset.id == record.id, PasswordReset.usado_em.is_(None), PasswordReset.expira_em > now
        ).values(usado_em=now))
        if consumed.rowcount != 1:
            db.rollback()
            raise invalid
        db.execute(update(User).where(User.id == record.usuario_id).values(senha_hash=new_hash, atualizado_em=now))
        db.execute(update(PasswordReset).where(
            PasswordReset.usuario_id == record.usuario_id, PasswordReset.usado_em.is_(None)
        ).values(usado_em=now))
        db.commit()
    return {"message": "Senha redefinida. Entre novamente com a nova senha."}
