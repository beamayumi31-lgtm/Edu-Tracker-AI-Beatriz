"""Vínculos externos isolados por titular. Importar não cria nem migra tabelas."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.mssql import NVARCHAR, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from edutrack.models import SQL_DATE, Audit, Base, Identity


class GoogleConnection(Audit, Base):
    __tablename__ = "conexoes_google"
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    google_sub: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(255))
    refresh_cifrado: Mapped[str] = mapped_column(Text().with_variant(VARCHAR(None), "mssql"))
    versao: Mapped[UUID] = mapped_column(Uuid)
    conteudo_autorizado: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")


class GoogleOAuthAttempt(Base):
    __tablename__ = "autorizacoes_google"
    state_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), unique=True)
    verifier_cifrado: Mapped[str] = mapped_column(Text().with_variant(VARCHAR(None), "mssql"))
    expira_em: Mapped[datetime] = mapped_column(SQL_DATE)
    usado_em: Mapped[datetime | None] = mapped_column(SQL_DATE)


class ClassroomDisciplineLink(Identity, Base):
    __tablename__ = "vinculos_classroom_disciplinas"
    __table_args__ = (UniqueConstraint("usuario_id", "google_sub", "turma_id", name="UQ_classroom_disciplina_origem"),)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    google_sub: Mapped[str] = mapped_column(String(128))
    turma_id: Mapped[str] = mapped_column(String(128))
    # SET NULL permite excluir registros locais sem apagar a chave de deduplicação.
    disciplina_id: Mapped[UUID | None] = mapped_column(ForeignKey("disciplinas.id", ondelete="SET NULL"))


class ClassroomTaskLink(Identity, Base):
    __tablename__ = "vinculos_classroom_tarefas"
    __table_args__ = (UniqueConstraint("usuario_id", "google_sub", "turma_id", "atividade_id", name="UQ_classroom_tarefa_origem"),)
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    google_sub: Mapped[str] = mapped_column(String(128))
    turma_id: Mapped[str] = mapped_column(String(128))
    atividade_id: Mapped[str] = mapped_column(String(128))
    tarefa_id: Mapped[UUID | None] = mapped_column(ForeignKey("tarefas_academicas.id", ondelete="SET NULL"))


class ClassroomContent(Identity, Audit, Base):
    """Cópia de leitura da publicação; os arquivos continuam no serviço de origem."""

    __tablename__ = "conteudos_classroom"
    __table_args__ = (
        UniqueConstraint("usuario_id", "google_sub", "turma_id", "tipo", "origem_id", name="UQ_classroom_conteudo_origem"),
        CheckConstraint("tipo IN ('atividade', 'material', 'aviso')", name="CK_classroom_conteudo_tipo"),
        ForeignKeyConstraint(["disciplina_id", "usuario_id"], ["disciplinas.id", "disciplinas.usuario_id"], ondelete="CASCADE"),
        Index("IX_classroom_conteudo_disciplina", "usuario_id", "disciplina_id"),
    )
    usuario_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"))
    google_sub: Mapped[str] = mapped_column(String(128))
    turma_id: Mapped[str] = mapped_column(String(128))
    origem_id: Mapped[str] = mapped_column(String(128))
    tipo: Mapped[str] = mapped_column(String(20))
    # Excluir a disciplina remove suas cópias de conteúdo, sem alterar o Google.
    disciplina_id: Mapped[UUID] = mapped_column(Uuid)
    titulo: Mapped[str] = mapped_column(Unicode(3000))
    descricao: Mapped[str] = mapped_column(UnicodeText().with_variant(NVARCHAR(None), "mssql"))
    topico: Mapped[str] = mapped_column(Unicode(200))
    # SQL Server aceita NVARCHAR(n) até 4000; a aplicação limita links a 4096.
    url: Mapped[str | None] = mapped_column(Unicode(4096).with_variant(NVARCHAR(None), "mssql"))
    anexos_json: Mapped[str] = mapped_column(UnicodeText().with_variant(NVARCHAR(None), "mssql"))
    publicado_em: Mapped[datetime | None] = mapped_column(SQL_DATE)
