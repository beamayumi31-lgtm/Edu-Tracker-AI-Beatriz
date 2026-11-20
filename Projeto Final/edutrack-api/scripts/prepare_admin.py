"""Reserva administrativa local após autorização humana; não cria senhas nem envia e-mail."""

import argparse
from datetime import timedelta

from pydantic import EmailStr, TypeAdapter
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from edutrack.admin_access import claim_admin_invitation
from edutrack.config import Settings
from edutrack.database import make_engine
from edutrack.models import AdminInvitation, User, utc_now


def reserve_admin(db: Session, email: str) -> str:
    email = str(TypeAdapter(EmailStr).validate_python(email.strip())).lower()
    invitation = db.get(AdminInvitation, email)
    user = db.scalar(select(User).where(User.email == email))
    if invitation and invitation.usado_em:
        return "Autorização já utilizada; nenhuma permissão foi alterada."
    if invitation is None:
        invitation = AdminInvitation(email=email, expira_em=utc_now() + timedelta(days=7))
        db.add(invitation)
    elif invitation.expira_em <= utc_now():
        invitation.expira_em = utc_now() + timedelta(days=7)
    db.flush()
    activated = user is not None and claim_admin_invitation(db, user)
    db.commit()
    return "Conta existente promovida a administrador." if activated else "Autorização reservada por sete dias; falta cadastro e/ou confirmação de e-mail."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--confirm-local-write", action="store_true")
    args = parser.parse_args()
    if not args.confirm_local_write:
        parser.error("Confirme autorização humana com --confirm-local-write.")
    # Destino literal, sem ler segredos ou aceitar configuração para outra base/servidor.
    settings = Settings(
        _env_file=None, environment="development", database_url=None,
        sql_server=r"localhost\SQLEXPRESS", sql_database="EduTrackIA",
        trust_server_certificate=True, email_verification_enabled=False,
    )
    engine = make_engine(settings)
    try:
        with Session(engine) as db:
            if db.scalar(text("SELECT DB_NAME()")) != "EduTrackIA":
                raise RuntimeError("Banco inesperado; nenhuma gravação foi realizada.")
            print(reserve_admin(db, args.email))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
