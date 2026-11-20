import asyncio
import logging
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from edutrack.academic_tools_routes import router as academic_tools_router
from edutrack.admin_access import router as admin_router
from edutrack.ai_routes import router as ai_router
from edutrack.config import Settings
from edutrack.database import make_engine, make_session_factory
from edutrack.email_delivery import send_password_reset, send_verification
from edutrack.email_verification import router as email_router
from edutrack.google_classroom import GoogleClassroom
from edutrack.integration_models import (
    ClassroomContent,
    ClassroomDisciplineLink,
    ClassroomTaskLink,
    GoogleConnection,
    GoogleOAuthAttempt,
)
from edutrack.integration_routes import router as integrations_router
from edutrack.models import AdminInvitation, EmailVerification, PasswordReset, User
from edutrack.password_reset import router as reset_router
from edutrack.routes import router
from edutrack.security import RateLimiter


def create_app(settings: Settings | None = None, engine=None):
    settings = settings or Settings()
    app_engine = engine if engine is not None else make_engine(settings)

    @asynccontextmanager
    async def lifespan(app):
        # Nunca criar tabelas ou executar migrações ao iniciar.
        yield
        app_engine.dispose()

    app = FastAPI(
        title="EduTrack API",
        version="0.1.0",
        lifespan=lifespan,
        description=(
            "## Como testar\n"
            "1. Cadastre sua conta em **POST /api/auth/register** (nome, e-mail, CPF válido e senha de 10 a 128 caracteres). O CPF é validado e descartado.\n"
            "Se a confirmação de e-mail estiver ativa, use **POST /api/auth/request-verification** com e-mail e senha; depois **POST /api/auth/verify-email** com os mesmos dados e o código recebido. Códigos expiram em dez minutos e têm cinco tentativas.\n"
            "2. Faça login em **POST /api/auth/login**.\n"
            "3. Copie somente o valor de **access_token**, clique em **Authorize** e cole no campo Value. Não inclua a palavra Bearer.\n"
            "4. Teste **GET /api/me**; depois crie curso → disciplina → tarefa.\n\n"
            "**Atenção:** Try it out + Execute realiza operações reais no banco local. "
            "DELETE não possui lixeira. Exclusões com vínculos/histórico são bloqueadas.\n\n"
            "PUT substitui todos os campos editáveis. Datas devem incluir fuso; respostas são UTC. "
            "Tokens expiram após 20 minutos na configuração padrão. Refaça o login quando necessário.\n\n"
            "O planejador funciona com usar_ia=false, sem chave externa. "
            "Chat generativo exige configuração e consentimento. Nenhuma chave deve ser colada nesta documentação."
        ),
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        swagger_ui_parameters={
            "persistAuthorization": False,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "filter": True,
        },
    )
    app.state.settings = settings
    app.state.session_factory = make_session_factory(app_engine)
    app.state.jwt_secret = (
        settings.jwt_secret.get_secret_value() if settings.jwt_secret else secrets.token_urlsafe(48)
    )
    app.state.limiter = RateLimiter()
    app.state.email_sender = send_verification
    app.state.password_reset_sender = send_password_reset
    app.state.google_client_factory = GoogleClassroom
    if settings.environment != "production":
        @app.get("/swagger", include_in_schema=False)
        def swagger_alias():
            return RedirectResponse("/docs")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def response_security(request: Request, call_next):
        # O limite ASGI também cobre corpos sem Content-Length e transferências em blocos.
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # O erro padrão inclui a entrada; não devolver senhas/CPF em mensagens de validação.
        errors = [
            {"loc": item["loc"], "msg": item["msg"], "type": item["type"]} for item in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": errors})

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        logging.getLogger("edutrack").error("Falha no banco: %s", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content={"detail": "Banco temporariamente indisponível. Tente novamente."},
        )

    @app.get("/health", tags=["Sistema"])
    def health():
        return {"status": "ok", "service": "edutrack-api"}

    @app.get("/ready", tags=["Sistema"])
    def ready():
        with app_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.execute(select(User.role).limit(0))
            connection.execute(select(AdminInvitation.email).limit(0))
            if settings.email_verification_enabled or settings.closed_adult_access:
                connection.execute(select(EmailVerification).limit(0))
            if settings.password_reset_enabled:
                connection.execute(select(PasswordReset).limit(0))
            if settings.classroom_enabled:
                for model in (GoogleConnection, GoogleOAuthAttempt, ClassroomDisciplineLink, ClassroomTaskLink):
                    connection.execute(select(model).limit(0))
            if settings.classroom_full_import_enabled:
                connection.execute(select(ClassroomContent).limit(0))
        return {"status": "ok"}

    app.include_router(router)
    app.include_router(academic_tools_router)
    app.include_router(admin_router)
    app.include_router(email_router)
    app.include_router(reset_router)
    app.include_router(ai_router)
    app.include_router(integrations_router)
    app.add_middleware(BodyLimitMiddleware)
    return app


class BodyLimitMiddleware:
    """Lê no máximo 64 KiB antes do processamento para evitar corpos ilimitados."""

    def __init__(self, app, max_bytes=65536):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        body = bytearray()
        try:
            async with asyncio.timeout(15):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    chunk = message.get("body", b"")
                    if len(body) + len(chunk) > self.max_bytes:
                        response = JSONResponse(
                            status_code=413, content={"detail": "Solicitação excede 64 KiB."}
                        )
                        return await response(scope, receive, send)
                    body.extend(chunk)
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            response = JSONResponse(status_code=408, content={"detail": "Tempo de envio excedido."})
            return await response(scope, receive, send)

        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)


def app_factory():
    return create_app()
