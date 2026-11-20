"""Teste autorizado contra o SQL Server real, com limpeza restrita à execução.

Não é coletado pelo pytest comum. Só executa com --executar e não altera DDL,
configuração permanente, .env ou o site publicado. Não chama provedor de IA.
"""

import argparse
import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from edutrack.config import Settings
from edutrack.database import make_engine
from edutrack.main import create_app
from edutrack.models import Base, Course, Discipline, Task, TimeEntry, User, WeeklyReport

SERVER = r"localhost\SQLEXPRESS"
DATABASE = "EduTrackIA"


def fingerprint(value):
    content = json.dumps(value, default=str, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(content.encode()).hexdigest()


def snapshot(engine):
    """Compara dados e estrutura sem imprimir ou salvar conteúdo pessoal."""
    inspector = inspect(engine)
    schema = {}
    data = {}
    with engine.connect() as connection:
        for table in Base.metadata.sorted_tables:
            rows = (
                connection.execute(select(table).order_by(table.c.id).limit(10001)).mappings().all()
            )
            if len(rows) > 10000:
                raise RuntimeError("Teste interrompido: volume acima do limite de inspeção segura.")
            data[table.name] = {
                "registros": len(rows),
                "assinatura": fingerprint([dict(row) for row in rows]),
            }
            schema[table.name] = {
                "colunas": inspector.get_columns(table.name),
                "fks": inspector.get_foreign_keys(table.name),
                "pk": inspector.get_pk_constraint(table.name),
                "indices": inspector.get_indexes(table.name),
                # O dialeto MSSQL não implementa get_check_constraints neste SQLAlchemy.
                "checks": [
                    dict(row)
                    for row in connection.execute(
                        text(
                            "SELECT name, definition, is_disabled, is_not_trusted "
                            "FROM sys.check_constraints "
                            "WHERE parent_object_id = OBJECT_ID(:table_name) ORDER BY name"
                        ),
                        {"table_name": "dbo." + table.name},
                    ).mappings()
                ],
            }
    return {"dados": data, "estrutura": fingerprint(schema)}


def cleanup(engine, identities):
    """Exclui somente as contas exclusivas e seus vínculos, em uma transação."""
    with Session(engine) as db:
        users = list(db.scalars(select(User).where(User.email.in_(identities))))
        if any(user.nome != identities[user.email] for user in users):
            raise RuntimeError(
                "Limpeza bloqueada: identidade de teste não corresponde ao esperado."
            )
        ids = [user.id for user in users]
        if not ids:
            return {}
        task_ids = select(Task.id).where(Task.usuario_id.in_(ids))
        commands = [
            (TimeEntry, TimeEntry.tarefa_id.in_(task_ids)),
            (WeeklyReport, WeeklyReport.usuario_id.in_(ids)),
            (Task, Task.usuario_id.in_(ids)),
            (Discipline, Discipline.usuario_id.in_(ids)),
            (Course, Course.usuario_id.in_(ids)),
            (User, User.id.in_(ids)),
        ]
        removed = {}
        for model, condition in commands:
            result = db.execute(
                delete(model).where(condition).execution_options(synchronize_session=False)
            )
            removed[model.__tablename__] = result.rowcount
        db.commit()
        return removed


class Verification:
    def __init__(self, client):
        self.client = client
        self.passed = []

    def check(self, label, condition):
        if not condition:
            raise AssertionError(label)
        self.passed.append(label)
        print("OK:", label)

    def request(self, label, method, path, status=200, **kwargs):
        response = self.client.request(method, path, **kwargs)
        # Não imprimir corpos de resposta: login contém token e conta contém e-mail.
        self.check(
            f"{label} [HTTP {response.status_code}/{status}]", response.status_code == status
        )
        return response.json() if status != 204 else None


def exercise_api(client, engine, identities):
    verify = Verification(client)
    verify.request("API conectada ao banco", "GET", "/ready")
    verify.request("Anônimo bloqueado", "GET", "/api/courses", 401)
    accounts = []
    for email, name in identities.items():
        password = secrets.token_urlsafe(30)
        body = {"nome": name, "email": email, "senha": password, "cpf": "00000000191"}
        user = verify.request("Cadastro persistido", "POST", "/api/auth/register", 201, json=body)
        token = verify.request(
            "Login autenticado", "POST", "/api/auth/login", json={"email": email, "senha": password}
        )
        headers = {"Authorization": "Bearer " + token["access_token"]}
        accounts.append((user, headers, body))
        with Session(engine) as db:
            saved = db.get(User, UUID(user["id"]))
            verify.check(
                "Conta confirmada em conexão independente e senha Argon2id",
                saved is not None
                and saved.senha_hash.startswith("$argon2id$")
                and saved.senha_hash != password,
            )
        verify.check("Resposta não expõe hash", "senha_hash" not in user)
    (user_a, auth_a, body_a), (user_b, auth_b, _) = accounts
    verify.request("E-mail duplicado recusado", "POST", "/api/auth/register", 409, json=body_a)
    verify.request(
        "Senha inválida recusada",
        "POST",
        "/api/auth/login",
        401,
        json={"email": body_a["email"], "senha": "incorreta"},
    )
    me = verify.request("Identidade da sessão", "GET", "/api/me", headers=auth_a)
    verify.check("Sessão pertence ao aluno correto", me["id"] == user_a["id"])

    course = verify.request(
        "Criar curso com Unicode e datas",
        "POST",
        "/api/courses",
        201,
        headers=auth_a,
        json={
            "nome": "Teste — Ciência da Computação",
            "instituicao": "Instituição fictícia",
            "data_inicio": "2030-01-01",
            "data_fim": "2030-12-31",
        },
    )
    foreign_course = verify.request(
        "Criar curso da segunda conta",
        "POST",
        "/api/courses",
        201,
        headers=auth_b,
        json={"nome": "Curso fictício B"},
    )
    course_update = {
        "nome": "Teste — Curso atualizado",
        "instituicao": "Instituição revisada",
        "data_inicio": "2030-02-01",
        "data_fim": "2030-11-30",
    }
    verify.request(
        "Editar curso", "PUT", f"/api/courses/{course['id']}", headers=auth_a, json=course_update
    )
    saved = verify.request(
        "Reler curso editado", "GET", f"/api/courses/{course['id']}", headers=auth_a
    )
    verify.check(
        "Unicode e datas preservados pelo SQL Server",
        all(saved[key] == value for key, value in course_update.items()),
    )
    discipline_input = {
        "nome": "Banco de Dados",
        "curso_id": course["id"],
        "professor": "Professor fictício",
        "carga_horaria": 80,
    }
    discipline = verify.request(
        "Criar disciplina", "POST", "/api/disciplines", 201, headers=auth_a, json=discipline_input
    )
    discipline_update = {**discipline_input, "nome": "SQL Server", "carga_horaria": 100}
    verify.request(
        "Editar disciplina",
        "PUT",
        f"/api/disciplines/{discipline['id']}",
        headers=auth_a,
        json=discipline_update,
    )
    saved = verify.request(
        "Reler disciplina editada", "GET", f"/api/disciplines/{discipline['id']}", headers=auth_a
    )
    verify.check(
        "Edição de disciplina persistiu",
        saved["nome"] == "SQL Server" and saved["carga_horaria"] == 100,
    )
    task_input = {
        "titulo": "Modelo relacional fictício",
        "disciplina_id": discipline["id"],
        "descricao": "Revisar chaves e relacionamentos — ação de teste.",
        "minutos_estimados": 90,
        "data_prevista": "2030-01-03T20:00:00-03:00",
    }
    task = verify.request(
        "Criar tarefa", "POST", "/api/tasks", 201, headers=auth_a, json=task_input
    )
    task_update = {**task_input, "titulo": "Modelo relacional revisado", "status": "concluida"}
    verify.request(
        "Concluir tarefa", "PUT", f"/api/tasks/{task['id']}", headers=auth_a, json=task_update
    )
    saved = verify.request(
        "Reler tarefa concluída", "GET", f"/api/tasks/{task['id']}", headers=auth_a
    )
    verify.check(
        "Conclusão e conversão UTC persistiram",
        saved["concluido_em"] is not None and saved["data_prevista"] == "2030-01-03T23:00:00Z",
    )
    task_update["status"] = "pendente"
    verify.request(
        "Reabrir tarefa", "PUT", f"/api/tasks/{task['id']}", headers=auth_a, json=task_update
    )
    verify.check(
        "Reabertura remove data de conclusão",
        client.get(f"/api/tasks/{task['id']}", headers=auth_a).json()["concluido_em"] is None,
    )

    resources = [
        ("courses", course, course_update),
        ("disciplines", discipline, discipline_update),
        ("tasks", task, task_update),
    ]
    for resource, record, body in resources:
        listed = verify.request(
            f"Listar {resource} do aluno",
            "GET",
            f"/api/{resource}?limit=1&offset=0",
            headers=auth_a,
        )
        verify.check(f"Paginação de {resource}", listed["total"] == 1 and len(listed["items"]) == 1)
        other = verify.request(
            f"Listar {resource} da outra conta", "GET", f"/api/{resource}", headers=auth_b
        )
        verify.check(
            f"Lista de {resource} não expõe a outra conta",
            all(item["id"] != record["id"] for item in other["items"]),
        )
        for method in ("GET", "PUT", "DELETE"):
            verify.request(
                f"Bloquear {method} alheio em {resource}",
                method,
                f"/api/{resource}/{record['id']}",
                404,
                headers=auth_b,
                **({"json": body} if method == "PUT" else {}),
            )
    verify.request(
        "Bloquear criação em curso alheio",
        "POST",
        "/api/disciplines",
        404,
        headers=auth_b,
        json=discipline_input,
    )
    verify.request(
        "Bloquear criação em disciplina alheia",
        "POST",
        "/api/tasks",
        404,
        headers=auth_b,
        json=task_input,
    )
    verify.request(
        "Bloquear transferência para curso de outro aluno",
        "PUT",
        f"/api/disciplines/{discipline['id']}",
        404,
        headers=auth_a,
        json={**discipline_update, "curso_id": foreign_course["id"]},
    )
    verify.request(
        "Bloquear injeção de usuario_id",
        "POST",
        "/api/courses",
        422,
        headers=auth_a,
        json={"nome": "Tentativa", "usuario_id": user_b["id"]},
    )

    # Confirma também a barreira da FK composta no banco, fora da validação HTTP.
    rejected_id = uuid4()
    with Session(engine) as db:
        db.add(
            Discipline(
                id=rejected_id,
                nome="Vínculo inválido de teste",
                curso_id=UUID(course["id"]),
                usuario_id=UUID(user_b["id"]),
            )
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            verify.check("FK composta do SQL Server bloqueia vínculo entre alunos", True)
        else:
            raise AssertionError("SQL Server aceitou vínculo de titularidade inválido.")
    with Session(engine) as db:
        verify.check(
            "Transação inválida não deixou registro", db.get(Discipline, rejected_id) is None
        )

    end = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=1)
    session_input = {
        "tarefa_id": task["id"],
        "iniciado_em": (end - timedelta(minutes=25)).isoformat(),
        "finalizado_em": end.isoformat(),
    }
    session = verify.request(
        "Registrar sessão de estudo",
        "POST",
        "/api/study-sessions",
        201,
        headers=auth_a,
        json=session_input,
    )
    sessions = verify.request("Reler sessões", "GET", "/api/study-sessions", headers=auth_a)
    verify.check(
        "Sessão e duração persistiram",
        sessions["items"][0]["id"] == session["id"]
        and sessions["items"][0]["duracao_minutos"] == 25,
    )
    verify.request(
        "Bloquear sessão em tarefa alheia",
        "POST",
        "/api/study-sessions",
        404,
        headers=auth_b,
        json=session_input,
    )
    verify.check(
        "Histórico não vaza entre contas",
        client.get("/api/study-sessions", headers=auth_b).json()["items"] == [],
    )
    summary = verify.request("Resumo acadêmico calculado", "GET", "/api/dashboard", headers=auth_a)
    verify.check(
        "Resumo reflete o banco",
        summary["cursos"] == 1
        and summary["disciplinas"] == 1
        and summary["minutos_estudados"] == 25
        and summary["total_tarefas"] == 1,
    )
    context = verify.request("Contexto da Edu IA", "GET", "/api/edu-ia/context", headers=auth_a)
    verify.check(
        "Contexto usa atividades da conta",
        context["tarefas"][0]["id"] == task["id"]
        and "senha_hash" not in json.dumps(context)
        and body_a["email"] not in json.dumps(context),
    )
    verify.check(
        "Contexto da outra conta não inclui atividades alheias",
        client.get("/api/edu-ia/context", headers=auth_b).json()["tarefas"] == [],
    )
    plan = verify.request(
        "Gerar plano sem chamada externa",
        "POST",
        "/api/edu-ia/study-plan",
        headers=auth_a,
        json={"data_inicio": "2030-01-01", "dias": 3, "minutos_por_dia": 30},
    )
    verify.check(
        "Plano cobre 90 minutos com as tarefas corretas",
        plan["origem"] == "regras"
        and sum(block["minutos"] for block in plan["blocos"]) == 90
        and all(block["tarefa_id"] == task["id"] for block in plan["blocos"]),
    )
    for resource, record in [("courses", course), ("disciplines", discipline), ("tasks", task)]:
        verify.request(
            f"Proteger histórico/dependências em {resource}",
            "DELETE",
            f"/api/{resource}/{record['id']}",
            409,
            headers=auth_a,
        )

    # Uma segunda hierarquia sem histórico valida o DELETE real de todos os recursos.
    disposable_course = verify.request(
        "Criar curso descartável",
        "POST",
        "/api/courses",
        201,
        headers=auth_a,
        json={"nome": "Curso para exclusão de teste"},
    )
    disposable_discipline = verify.request(
        "Criar disciplina descartável",
        "POST",
        "/api/disciplines",
        201,
        headers=auth_a,
        json={"nome": "Disciplina para exclusão", "curso_id": disposable_course["id"]},
    )
    disposable_task = verify.request(
        "Criar tarefa descartável",
        "POST",
        "/api/tasks",
        201,
        headers=auth_a,
        json={"titulo": "Tarefa para exclusão", "disciplina_id": disposable_discipline["id"]},
    )
    for resource, record, model in [
        ("tasks", disposable_task, Task),
        ("disciplines", disposable_discipline, Discipline),
        ("courses", disposable_course, Course),
    ]:
        verify.request(
            f"Excluir {resource} pela API",
            "DELETE",
            f"/api/{resource}/{record['id']}",
            204,
            headers=auth_a,
        )
        verify.request(
            f"Confirmar ausência HTTP de {resource}",
            "GET",
            f"/api/{resource}/{record['id']}",
            404,
            headers=auth_a,
        )
        with Session(engine) as db:
            verify.check(
                f"Exclusão persistida no SQL Server: {resource}",
                db.get(model, UUID(record["id"])) is None,
            )
    return len(verify.passed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--executar",
        action="store_true",
        help="Autoriza somente dados fictícios desta execução e sua limpeza.",
    )
    args = parser.parse_args()
    if not args.executar:
        parser.error(
            "Nenhuma gravação realizada. Use --executar somente após autorização do responsável."
        )
    marker = uuid4().hex
    identities = {
        f"edutrack.qa.{marker}.{n}@example.com": f"Teste EduTrack {marker} {n}" for n in (1, 2)
    }
    # Valores explícitos impedem variáveis de ambiente de redirecionar o teste para outro banco.
    settings = Settings(
        _env_file=None,
        environment="test",
        sql_server=SERVER,
        sql_database=DATABASE,
        database_url=None,
        trust_server_certificate=True,
        db_writes_enabled=True,
        jwt_secret=secrets.token_urlsafe(48),
        OPENAI_API_KEY=None,
        OPENAI_MODEL=None,
        email_verification_enabled=False,
        SENDGRID_API_KEY=None,
    )
    engine = make_engine(settings)
    try:
        with engine.connect() as connection:
            actual_db = connection.scalar(text("SELECT DB_NAME()"))
            actual_server = connection.scalar(
                text("SELECT CAST(SERVERPROPERTY('ServerName') AS nvarchar(128))")
            )
            if actual_db != DATABASE or actual_server != r"DESKTOP-PBP3G2U\SQLEXPRESS":
                raise RuntimeError(
                    "Destino diferente do SQL Server local autorizado; teste cancelado."
                )
            if connection.execute(select(User.id).where(User.email.in_(identities))).first():
                raise RuntimeError("Identificador de teste já existente; nada foi alterado.")
        before = snapshot(engine)
        print("Destino confirmado:", SERVER, "/", DATABASE)
        print("Execução fictícia:", marker)
        print(
            "Registros antes:",
            {name: value["registros"] for name, value in before["dados"].items()},
        )
        try:
            with TestClient(create_app(settings, engine)) as client:
                passed = exercise_api(client, engine, identities)
        finally:
            removed = cleanup(engine, identities)
            after = snapshot(engine)
            print("Limpeza restrita aos dados fictícios:", removed)
            print(
                "Registros depois:",
                {name: value["registros"] for name, value in after["dados"].items()},
            )
            if before != after:
                raise RuntimeError(
                    "A comparação final encontrou uma diferença. Não altere outros dados; investigue antes de repetir."
                )
            print("Confirmado: dados e estrutura idênticos ao estado anterior.")
        print(f"SUCESSO: {passed} verificações aprovadas contra o SQL Server real.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
