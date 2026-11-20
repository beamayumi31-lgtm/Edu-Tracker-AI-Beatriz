from datetime import timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from edutrack.closed_access import DENIED, require_closed_access
from edutrack.database import get_db, require_writes
from edutrack.email_verification import require_verified
from edutrack.models import Course, Discipline, Task, TimeEntry, User, utc_now
from edutrack.progress import calculate_progress
from edutrack.repository import commit, owned, page
from edutrack.schemas import (
    CourseInput,
    CourseOut,
    DisciplineInput,
    DisciplineOut,
    Login,
    Page,
    ProfileInput,
    Registration,
    TaskInput,
    TaskOut,
    TaskStatus,
    TimeEntryInput,
    TimeEntryOut,
    TokenOut,
    UserOut,
)
from edutrack.security import DUMMY_HASH, current_user, issue_token, limit_auth, password_hasher

router = APIRouter(prefix="/api")
Db = Annotated[Session, Depends(get_db)]
Student = Annotated[User, Depends(current_user)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0, le=100000)]
write = [Depends(require_writes)]


@router.post(
    "/auth/register",
    response_model=UserOut,
    status_code=201,
    tags=["Autenticação"],
    dependencies=[Depends(limit_auth), *write],
)
def register(body: Registration, request: Request, db: Db):
    settings = request.app.state.settings
    if settings.closed_adult_access:
        raise HTTPException(403, DENIED)
    if settings.email_verification_enabled and not settings.email_configured:
        raise HTTPException(503, "Cadastro indisponível até a configuração do envio de e-mails.")
    user = User(
        nome=body.nome,
        email=str(body.email),
        senha_hash=password_hasher.hash(body.senha.get_secret_value()),
    )
    db.add(user)
    commit(db, "Não foi possível cadastrar. Se já possui conta, faça login.")
    return user


@router.post(
    "/auth/login",
    response_model=TokenOut,
    tags=["Autenticação"],
    dependencies=[Depends(limit_auth)],
)
def login(body: Login, request: Request, db: Db):
    user = db.scalar(select(User).where(User.email == str(body.email).lower()))
    valid = password_hasher.verify(
        body.senha.get_secret_value(), user.senha_hash if user else DUMMY_HASH
    )
    if not user or not valid:
        raise HTTPException(
            401, "E-mail ou senha inválidos.", headers={"WWW-Authenticate": "Bearer"}
        )
    require_closed_access(request, db, user)
    require_verified(request, db, user)
    return {
        "access_token": issue_token(request, user),
        "expires_in": request.app.state.settings.token_minutes * 60,
        "user": user,
    }


@router.get("/me", response_model=UserOut, tags=["Autenticação"])
def me(student: Student):
    return student


@router.put("/me", response_model=UserOut, tags=["Autenticação"], dependencies=write)
def update_profile(body: ProfileInput, db: Db, student: Student):
    student.nome = body.nome
    commit(db)
    return student


@router.get("/courses", response_model=Page[CourseOut], tags=["Cursos"])
def courses(db: Db, student: Student, limit: Limit = 50, offset: Offset = 0):
    return page(db, Course, student.id, CourseOut, limit, offset)


@router.post(
    "/courses", response_model=CourseOut, status_code=201, tags=["Cursos"], dependencies=write
)
def create_course(body: CourseInput, db: Db, student: Student):
    course = Course(**body.model_dump(), usuario_id=student.id)
    db.add(course)
    commit(db)
    return course


@router.get("/courses/{item_id}", response_model=CourseOut, tags=["Cursos"])
def get_course(item_id: UUID, db: Db, student: Student):
    return owned(db, Course, item_id, student.id)


@router.put("/courses/{item_id}", response_model=CourseOut, tags=["Cursos"], dependencies=write)
def update_course(item_id: UUID, body: CourseInput, db: Db, student: Student):
    course = owned(db, Course, item_id, student.id)
    for key, value in body.model_dump().items():
        setattr(course, key, value)
    commit(db)
    return course


@router.delete("/courses/{item_id}", status_code=204, tags=["Cursos"], dependencies=write)
def delete_course(item_id: UUID, db: Db, student: Student):
    course = owned(db, Course, item_id, student.id)
    if db.scalar(select(Discipline.id).where(Discipline.curso_id == item_id).limit(1)):
        raise HTTPException(
            409, "O curso possui disciplinas. Remova ou transfira os vínculos antes de excluir."
        )
    db.delete(course)
    commit(db)
    return Response(status_code=204)


@router.get("/disciplines", response_model=Page[DisciplineOut], tags=["Disciplinas"])
def disciplines(
    db: Db, student: Student, limit: Limit = 50, offset: Offset = 0, curso_id: UUID | None = None
):
    filters = [Discipline.curso_id == curso_id] if curso_id else []
    return page(db, Discipline, student.id, DisciplineOut, limit, offset, *filters)


@router.post(
    "/disciplines",
    response_model=DisciplineOut,
    status_code=201,
    tags=["Disciplinas"],
    dependencies=write,
)
def create_discipline(body: DisciplineInput, db: Db, student: Student):
    owned(db, Course, body.curso_id, student.id)
    discipline = Discipline(**body.model_dump(), usuario_id=student.id)
    db.add(discipline)
    commit(db)
    return discipline


@router.get("/disciplines/{item_id}", response_model=DisciplineOut, tags=["Disciplinas"])
def get_discipline(item_id: UUID, db: Db, student: Student):
    return owned(db, Discipline, item_id, student.id)


@router.put(
    "/disciplines/{item_id}", response_model=DisciplineOut, tags=["Disciplinas"], dependencies=write
)
def update_discipline(item_id: UUID, body: DisciplineInput, db: Db, student: Student):
    discipline = owned(db, Discipline, item_id, student.id)
    owned(db, Course, body.curso_id, student.id)
    for key, value in body.model_dump().items():
        setattr(discipline, key, value)
    commit(db)
    return discipline


@router.delete("/disciplines/{item_id}", status_code=204, tags=["Disciplinas"], dependencies=write)
def delete_discipline(item_id: UUID, db: Db, student: Student):
    discipline = owned(db, Discipline, item_id, student.id)
    if db.scalar(select(Task.id).where(Task.disciplina_id == item_id).limit(1)):
        raise HTTPException(
            409, "A disciplina possui tarefas. Remova ou transfira os vínculos antes de excluir."
        )
    db.delete(discipline)
    commit(db)
    return Response(status_code=204)


def task_values(body: TaskInput, existing: Task | None = None):
    values = body.model_dump()
    if body.data_prevista:
        values["data_prevista"] = body.data_prevista.astimezone(timezone.utc).replace(tzinfo=None)
    values["concluido_em"] = (
        (existing.concluido_em if existing and existing.concluido_em else utc_now())
        if body.status == "concluida"
        else None
    )
    return values


@router.get("/tasks", response_model=Page[TaskOut], tags=["Tarefas"])
def tasks(
    db: Db,
    student: Student,
    limit: Limit = 50,
    offset: Offset = 0,
    disciplina_id: UUID | None = None,
    status: TaskStatus | None = None,
):
    filters = []
    if disciplina_id:
        filters.append(Task.disciplina_id == disciplina_id)
    if status:
        filters.append(Task.status == status)
    return page(db, Task, student.id, TaskOut, limit, offset, *filters)


@router.post(
    "/tasks", response_model=TaskOut, status_code=201, tags=["Tarefas"], dependencies=write
)
def create_task(body: TaskInput, db: Db, student: Student):
    owned(db, Discipline, body.disciplina_id, student.id)
    task = Task(**task_values(body), usuario_id=student.id)
    db.add(task)
    commit(db)
    return task


@router.get("/tasks/{item_id}", response_model=TaskOut, tags=["Tarefas"])
def get_task(item_id: UUID, db: Db, student: Student):
    return owned(db, Task, item_id, student.id)


@router.put("/tasks/{item_id}", response_model=TaskOut, tags=["Tarefas"], dependencies=write)
def update_task(item_id: UUID, body: TaskInput, db: Db, student: Student):
    task = owned(db, Task, item_id, student.id)
    owned(db, Discipline, body.disciplina_id, student.id)
    for key, value in task_values(body, task).items():
        setattr(task, key, value)
    commit(db)
    return task


@router.delete("/tasks/{item_id}", status_code=204, tags=["Tarefas"], dependencies=write)
def delete_task(item_id: UUID, db: Db, student: Student):
    task = owned(db, Task, item_id, student.id)
    if db.scalar(select(TimeEntry.id).where(TimeEntry.tarefa_id == item_id).limit(1)):
        raise HTTPException(
            409, "Esta tarefa tem histórico de estudo. Cancele a tarefa para preservar o histórico."
        )
    db.delete(task)
    commit(db)
    return Response(status_code=204)


@router.post(
    "/study-sessions",
    response_model=TimeEntryOut,
    status_code=201,
    tags=["Estudos"],
    dependencies=write,
)
def add_session(
    body: TimeEntryInput,
    db: Db,
    student: Student,
    idempotency_key: Annotated[UUID | None, Header()] = None,
):
    owned(db, Task, body.tarefa_id, student.id)
    values = dict(
        tarefa_id=body.tarefa_id,
        iniciado_em=body.iniciado_em.astimezone(timezone.utc).replace(tzinfo=None),
        finalizado_em=body.finalizado_em.astimezone(timezone.utc).replace(tzinfo=None),
    )

    def replay():
        existing = db.get(TimeEntry, idempotency_key) if idempotency_key else None
        if existing is None:
            return None
        # O ID é apenas uma chave de repetição, nunca autorização de acesso.
        task = db.get(Task, existing.tarefa_id)
        if not task or task.usuario_id != student.id or any(
            getattr(existing, key) != value for key, value in values.items()
        ):
            raise HTTPException(409, "Identificador de sessão já utilizado.")
        return existing

    if existing := replay():
        return existing
    entry = TimeEntry(**values, **({"id": idempotency_key} if idempotency_key else {}))
    # duracao_minutos é uma coluna calculada persistida no SQL Server, não gravável.
    db.add(entry)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if existing := replay():
            return existing
        raise HTTPException(409, "A sessão conflita com registros existentes.") from None
    return entry


@router.get("/study-sessions", response_model=Page[TimeEntryOut], tags=["Estudos"])
def sessions(db: Db, student: Student, limit: Limit = 50, offset: Offset = 0):
    query = (
        select(TimeEntry)
        .join(Task, Task.id == TimeEntry.tarefa_id)
        .where(Task.usuario_id == student.id)
    )
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(
        query.order_by(TimeEntry.iniciado_em.desc(), TimeEntry.id).offset(offset).limit(limit)
    )
    return {
        "items": [TimeEntryOut.model_validate(row) for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/dashboard", tags=["Estudos"])
def dashboard(db: Db, student: Student):
    statuses = dict(
        db.execute(
            select(Task.status, func.count())
            .where(Task.usuario_id == student.id)
            .group_by(Task.status)
        ).all()
    )
    total_tasks = sum(statuses.values())
    minutes = db.scalar(
        select(func.coalesce(func.sum(TimeEntry.duracao_minutos), 0))
        .join(Task, Task.id == TimeEntry.tarefa_id)
        .where(Task.usuario_id == student.id)
    )
    return {
        "cursos": db.scalar(
            select(func.count()).select_from(Course).where(Course.usuario_id == student.id)
        ),
        "disciplinas": db.scalar(
            select(func.count()).select_from(Discipline).where(Discipline.usuario_id == student.id)
        ),
        "tarefas_por_status": statuses,
        "total_tarefas": total_tasks,
        "minutos_estudados": minutes,
        "progresso_percentual": calculate_progress(
            statuses.get("concluida", 0), total_tasks - statuses.get("cancelada", 0)
        )["percentage"],
    }
