from collections.abc import Generator

from fastapi import HTTPException, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from edutrack.config import Settings


def make_engine(settings: Settings):
    url = settings.sqlalchemy_url()
    options = {"pool_pre_ping": True, "hide_parameters": True}
    if str(url).startswith("mssql"):
        options.update(pool_size=5, max_overflow=5, pool_timeout=10, connect_args={"timeout": 5})
    return create_engine(url, **options)


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


def get_db(request: Request) -> Generator[Session, None, None]:
    # A sessão é sempre encerrada. Cada operação de escrita confirma sua própria transação.
    with request.app.state.session_factory() as session:
        yield session


def require_writes(request: Request):
    if not request.app.state.settings.db_writes_enabled:
        raise HTTPException(
            503, "Gravação desativada: confirme a autorização do banco antes de habilitar."
        )
