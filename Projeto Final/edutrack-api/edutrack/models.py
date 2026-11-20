"""Mapeamento das tabelas existentes; importar este módulo não executa DDL."""

from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from edutrack.sql_expressions import SessionMinutes


def utc_now() -> datetime:
    # datetime2 não guarda fuso. A convenção do banco é UTC.
    return datetime.now(timezone.utc).replace(tzinfo=None)


SQL_DATE = DateTime().with_variant(DATETIME2(precision=3), "mssql")


class Base(DeclarativeBase):
    pass


class Identity:
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)


class Audit:
    criado_em: Mapped[datetime] = mapped_column(SQL_DATE, default=utc_now)
    atualizado_em: Mapped[datetime] = mapped_column(SQL_DATE, default=utc_now, onupdate=utc_now)


class User(Identity, Audit, Base):
    __tablename__ = "usuarios"
    __table_args__ = (CheckConstraint("role IN ('student', 'admin')", name="CK_usuarios_role"),)
    nome: Mapped[str] = mapped_column(Unicode(150))
    email: Mapped[str] = mapped_column(Unicode(255), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="student", server_default="student")


class AdminInvitation(Base):
    """Autorização local de uso único, ativada somente com e-mail confirmado."""

    __tablename__ = "convites_administrador"
    __table_args__ = (
        CheckConstraint("expira_em > criado_em", name="CK_convites_admin_prazo"),
        CheckConstraint("(usado_em IS NULL AND usuario_id IS NULL) OR (usado_em IS NOT NULL AND usuario_id IS NOT NULL)", name="CK_convites_admin_consumo"),
    )
    email: Mapped[str] = mapped_column(Unicode(255), primary_key=True)
    criado_em: Mapped[datetime] = mapped_column(SQL_DATE, default=utc_now)
    expira_em: Mapped[datetime] = mapped_column(SQL_DATE)
    usado_em: Mapped[datetime | None] = mapped_column(SQL_DATE)
    usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey("usuarios.id"))


class EmailVerification(Base):
    """Um desafio por conta; apenas HMAC do código e metadados de proteção."""

    __tablename__ = "verificacoes_email"
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    codigo_hash: Mapped[str | None] = mapped_column(String(64))
    expira_em: Mapped[datetime | None] = mapped_column(SQL_DATE)
    confirmado_em: Mapped[datetime | None] = mapped_column(SQL_DATE)
    enviado_em: Mapped[datetime | None] = mapped_column(SQL_DATE)
    janela_em: Mapped[datetime | None] = mapped_column(SQL_DATE)
    envios: Mapped[int] = mapped_column(Integer, default=0)
    tentativas: Mapped[int] = mapped_column(Integer, default=0)
    versao: Mapped[int] = mapped_column(Integer, default=0)


class PasswordReset(Identity, Base):
    """Desafios descartáveis; o token enviado por e-mail nunca é armazenado em texto."""

    __tablename__ = "recuperacoes_senha"
    __table_args__ = (CheckConstraint("expira_em > criado_em", name="CK_recuperacoes_senha_prazo"),)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    criado_em: Mapped[datetime] = mapped_column(SQL_DATE, default=utc_now)
    expira_em: Mapped[datetime] = mapped_column(SQL_DATE)
    usado_em: Mapped[datetime | None] = mapped_column(SQL_DATE)


class Course(Identity, Audit, Base):
    __tablename__ = "cursos"
    __table_args__ = (
        UniqueConstraint("id", "usuario_id"),
        CheckConstraint("data_inicio IS NULL OR data_fim IS NULL OR data_fim >= data_inicio"),
    )
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(Unicode(150))
    instituicao: Mapped[str | None] = mapped_column(Unicode(200))
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)


class Discipline(Identity, Audit, Base):
    __tablename__ = "disciplinas"
    __table_args__ = (
        UniqueConstraint("id", "usuario_id"),
        ForeignKeyConstraint(["curso_id", "usuario_id"], ["cursos.id", "cursos.usuario_id"]),
        CheckConstraint("carga_horaria IS NULL OR carga_horaria >= 0"),
    )
    curso_id: Mapped[UUID] = mapped_column(Uuid)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(Unicode(150))
    professor: Mapped[str | None] = mapped_column(Unicode(150))
    carga_horaria: Mapped[int | None] = mapped_column(Integer)


class Task(Identity, Audit, Base):
    __tablename__ = "tarefas_academicas"
    __table_args__ = (
        ForeignKeyConstraint(
            ["disciplina_id", "usuario_id"], ["disciplinas.id", "disciplinas.usuario_id"]
        ),
        CheckConstraint("status IN ('pendente', 'em_andamento', 'concluida', 'cancelada')"),
        CheckConstraint("status <> 'concluida' OR concluido_em IS NOT NULL"),
        CheckConstraint("minutos_estimados IS NULL OR minutos_estimados >= 0"),
    )
    disciplina_id: Mapped[UUID] = mapped_column(Uuid)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    titulo: Mapped[str] = mapped_column(Unicode(200))
    descricao: Mapped[str | None] = mapped_column(UnicodeText)
    data_prevista: Mapped[datetime | None] = mapped_column(SQL_DATE)
    status: Mapped[str] = mapped_column(String(20), default="pendente")
    minutos_estimados: Mapped[int | None] = mapped_column(Integer)
    concluido_em: Mapped[datetime | None] = mapped_column(SQL_DATE)


class TimeEntry(Identity, Base):
    __tablename__ = "registros_tempo_tarefa"
    tarefa_id: Mapped[UUID] = mapped_column(ForeignKey("tarefas_academicas.id"))
    iniciado_em: Mapped[datetime] = mapped_column(SQL_DATE)
    finalizado_em: Mapped[datetime | None] = mapped_column(SQL_DATE)
    duracao_minutos: Mapped[int | None] = mapped_column(
        Integer, Computed(SessionMinutes(), persisted=True)
    )
    criado_em: Mapped[datetime] = mapped_column(SQL_DATE, default=utc_now)


class WeeklyReport(Identity, Base):
    __tablename__ = "relatorios_semanais"
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    periodo_inicio: Mapped[date] = mapped_column(Date)
    periodo_fim: Mapped[date] = mapped_column(Date)
    url_arquivo: Mapped[str | None] = mapped_column(Unicode(2048))
    gerado_em: Mapped[datetime] = mapped_column(SQL_DATE, default=utc_now)
