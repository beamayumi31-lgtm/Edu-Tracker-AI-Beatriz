import hashlib
import hmac
from collections import OrderedDict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from time import monotonic
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from edutrack.closed_access import require_closed_access
from edutrack.database import get_db
from edutrack.models import User

password_hasher = PasswordHash.recommended()
# Equaliza o trabalho de hash para e-mails inexistentes, sem usar uma senha de conta real.
DUMMY_HASH = password_hasher.hash("senha-descartavel-sem-conta-vinculada")
bearer = HTTPBearer(auto_error=False)
ISSUER = "edutrack-api"
AUDIENCE = "edutrack-client"


class RateLimiter:
    """Limite em memória para uma instância local. Produção multiworker exige Redis/gateway."""

    def __init__(self):
        self.entries = OrderedDict()
        self.lock = Lock()

    def check(self, key: str, limit: int, window: int):
        now = monotonic()
        with self.lock:
            # Expiração e limite de chaves impedem crescimento ilimitado de memória.
            for old_key in list(self.entries):
                if self.entries[old_key][1] <= now:
                    del self.entries[old_key]
            if key not in self.entries and len(self.entries) >= 10000:
                raise HTTPException(429, "Muitas solicitações. Tente mais tarde.")
            attempts, _ = self.entries.get(key, (deque(), now + window))
            while attempts and attempts[0] <= now - window:
                attempts.popleft()
            if len(attempts) >= limit:
                raise HTTPException(
                    429, "Limite de tentativas atingido.", headers={"Retry-After": str(window)}
                )
            attempts.append(now)
            self.entries[key] = (attempts, now + window)


def limit_auth(request: Request):
    # Não confiar em X-Forwarded-For sem um proxy explicitamente autorizado.
    host = request.client.host if request.client else "local"
    request.app.state.limiter.check("auth:" + host, 15, 300)


def password_stamp(secret: str, password_hash: str) -> str:
    """Revoga sessões após troca de senha sem expor o hash no JWT."""
    return hmac.new(secret.encode(), password_hash.encode(), hashlib.sha256).hexdigest()


def issue_token(request: Request, user: User):
    now = datetime.now(timezone.utc)
    minutes = request.app.state.settings.token_minutes
    claims = {
        "sub": str(user.id),
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "jti": str(uuid4()),
        "pwd": password_stamp(request.app.state.jwt_secret, user.senha_hash),
    }
    return jwt.encode(claims, request.app.state.jwt_secret, algorithm="HS256")


def current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    denied = HTTPException(
        401, "Sessão inválida ou expirada.", headers={"WWW-Authenticate": "Bearer"}
    )
    if not credentials:
        raise denied
    try:
        claims = jwt.decode(
            credentials.credentials,
            request.app.state.jwt_secret,
            algorithms=["HS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["sub", "iat", "exp", "iss", "aud", "jti"]},
        )
        user_id = UUID(claims["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise denied from None
    user = db.get(User, user_id)
    if user is None:
        raise denied
    if not hmac.compare_digest(str(claims.get("pwd", "")), password_stamp(request.app.state.jwt_secret, user.senha_hash)):
        raise denied
    # Importação local evita dependência circular com as rotas de verificação.
    from edutrack.email_verification import require_verified

    require_closed_access(request, db, user)
    require_verified(request, db, user)
    # Impede que uma aba antiga grave na conta que entrou em outra aba.
    expected = request.headers.get("X-EduTrack-User")
    if expected and expected != str(user.id):
        raise HTTPException(409, "A conta ativa mudou. Recarregue a página antes de continuar.")
    return user
