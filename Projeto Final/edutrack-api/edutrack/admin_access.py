"""Permissões administrativas independentes de campos enviados pelo navegador."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from edutrack.database import get_db
from edutrack.models import AdminInvitation, EmailVerification, User, utc_now
from edutrack.schemas import AdminAccessOut
from edutrack.security import current_user

router = APIRouter(prefix="/api/admin", tags=["Administração"])


def claim_admin_invitation(db: Session, user: User) -> bool:
    """Consumir e promover na mesma transação; o chamador confirma o commit."""
    confirmed = db.scalar(select(EmailVerification.confirmado_em).where(
        EmailVerification.usuario_id == user.id,
    ))
    if not confirmed:
        return False
    now = utc_now()
    result = db.execute(update(AdminInvitation).where(
        AdminInvitation.email == user.email.lower(),
        AdminInvitation.usado_em.is_(None),
        AdminInvitation.expira_em > now,
    ).values(usado_em=now, usuario_id=user.id).execution_options(synchronize_session=False))
    if result.rowcount != 1:
        return False
    user.role = "admin"
    return True


def require_admin(user: User = Depends(current_user), db: Session = Depends(get_db)) -> User:
    # O papel é lido do SQL Server em cada chamada, nunca de claims ou storage do cliente.
    if user.role != "admin":
        raise HTTPException(403, "Acesso exclusivo para administradores.")
    verified = db.scalar(select(EmailVerification.confirmado_em).where(
        EmailVerification.usuario_id == user.id,
    ))
    # Mesmo com a verificação geral desativada, administradores precisam comprovar o e-mail.
    if not verified:
        raise HTTPException(403, "Confirme seu e-mail antes de acessar a administração.")
    return user


@router.get("/access", response_model=AdminAccessOut)
def admin_access(admin: User = Depends(require_admin)):
    """Confirma acesso sem expor cadastros ou dados acadêmicos de outros usuários."""
    return {"role": admin.role, "email_verificado": True, "gestao_usuarios_disponivel": False}
