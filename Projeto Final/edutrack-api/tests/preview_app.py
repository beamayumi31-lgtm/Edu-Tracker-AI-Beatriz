"""Prévia visual descartável: somente loopback, SQLite temporário e dados fictícios."""
import os
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from sqlalchemy import create_engine, event

from edutrack.config import Settings
from edutrack.main import create_app
from edutrack.models import Base, Course, Discipline, Task, TimeEntry, User, utc_now
from edutrack.security import password_hasher


def build_preview(database_path: Path, *, populate: bool = True):
    if os.environ.get("EDUTRACK_QA_PREVIEW") != "1":
        raise RuntimeError("Prévia de QA exige ativação explícita e não deve ser implantada.")
    # Conexões próprias suportam as quatro leituras simultâneas feitas pelo dashboard.
    # O diretório temporário é removido ao encerrar; não é o banco SQL Server de alunos.
    engine = create_engine("sqlite:///" + database_path.as_posix(), connect_args={"check_same_thread": False})
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    settings = Settings(_env_file=None, environment="test", db_writes_enabled=True,
                        jwt_secret="segredo-ficticio-exclusivo-da-previa-descartavel",
                        OPENAI_API_KEY=None, OPENAI_MODEL=None, SENDGRID_API_KEY=None,
                        GEMINI_API_KEY=None, GEMINI_MODEL=None, ai_provider="gemini", classroom_enabled=False,
                        email_from=None, email_verification_enabled=False, password_reset_enabled=False)
    app = create_app(settings, engine)
    with app.state.session_factory() as db:
        user = User(id=uuid4(), nome="Demonstração local", email="avaliacao@example.com",
                    senha_hash=password_hasher.hash("Demonstracao-local-2026"), role="student")
        db.add(user)
        db.flush()
        if not populate:
            db.commit()
            return app
        course = Course(id=uuid4(), usuario_id=user.id, nome="Ciência da Computação — demonstração", instituicao="Ambiente de testes")
        db.add(course)
        db.flush()
        discipline = Discipline(id=uuid4(), usuario_id=user.id, curso_id=course.id, nome="Banco de Dados", professor="Professor de demonstração", carga_horaria=80)
        db.add(discipline)
        db.flush()
        now = utc_now()
        tasks = []
        for index, title in enumerate(["Revisar normalização", "Desenhar modelo relacional", "Praticar consultas SQL"]):
            task = Task(id=uuid4(), usuario_id=user.id, disciplina_id=discipline.id, titulo=title,
                        descricao="Registro fictício para conferência visual. Não pertence a um aluno real.",
                        status="concluida" if index == 0 else "pendente", concluido_em=now if index == 0 else None,
                        data_prevista=now + timedelta(days=index + 1), minutos_estimados=45)
            db.add(task)
            tasks.append(task)
        db.flush()
        for index, days in enumerate([0, 1, 2, 7, 9]):
            end = now - timedelta(days=days, minutes=2)
            db.add(TimeEntry(id=uuid4(), tarefa_id=tasks[0].id, iniciado_em=end - timedelta(minutes=25 + index * 5), finalizado_em=end))
        db.commit()
    return app


if __name__ == "__main__":
    import uvicorn
    with TemporaryDirectory(prefix="edutrack-qa-") as directory:
        uvicorn.run(build_preview(Path(directory) / "preview.db"), host="127.0.0.1", port=8014, access_log=False, proxy_headers=False)
