"""Optional closed adult deployment; no inferred age and no automatic enrollment."""
from fastapi import HTTPException

from edutrack.models import EmailVerification

DENIED = {"code": "CLOSED_ACCESS_REQUIRED", "message": "Acesso restrito a adultos previamente autorizados pelo responsavel."}


def require_closed_invitation(request, user):
    settings = request.app.state.settings
    if not settings.closed_adult_access:
        return
    allowed = {str(email).lower() for email in settings.adult_access_emails}
    if settings.ai_audience != "adults_only" or user.email.lower() not in allowed:
        raise HTTPException(403, DENIED)


def require_closed_access(request, db, user):
    if not request.app.state.settings.closed_adult_access:
        return
    require_closed_invitation(request, user)
    record = db.get(EmailVerification, user.id)
    if not record or not record.confirmado_em:
        from edutrack.email_verification import REQUIRED

        raise HTTPException(403, REQUIRED)
