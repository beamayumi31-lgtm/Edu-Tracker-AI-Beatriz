"""Busca e relatórios autenticados, sem gravar dados acadêmicos ou arquivos públicos."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from edutrack.academic_search import discipline_search
from edutrack.database import get_db
from edutrack.models import Discipline, Task, User, utc_now
from edutrack.progress_report import build_progress_pdf
from edutrack.schemas import DisciplineOut, Page
from edutrack.security import current_user

router = APIRouter(prefix="/api", tags=["Busca e relatórios"])
Db = Annotated[Session, Depends(get_db)]
Student = Annotated[User, Depends(current_user)]
MAX_REPORT_DISCIPLINES = 500


@router.get("/search/disciplines", response_model=Page[DisciplineOut])
def search_disciplines(db: Db, student: Student,
                       q: Annotated[str, Query(max_length=150)] = "",
                       overdue: bool = False,
                       limit: Annotated[int, Query(ge=1, le=100)] = 50,
                       offset: Annotated[int, Query(ge=0, le=100000)] = 0):
    """Nome parcial OU tarefa atrasada. Sem filtros, lista as disciplinas da conta."""
    query = discipline_search(student.id, q, overdue, utc_now())
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(query.order_by(Discipline.nome, Discipline.id).offset(offset).limit(limit))
    return {"items": [DisciplineOut.model_validate(row) for row in rows],
            "total": total, "limit": limit, "offset": offset}


@router.get("/reports/generate")
def report_link(student: Student):
    """Retorna caminho fixo de download; o download também exige autenticação."""
    return {"download_url": "/api/reports/progress.pdf", "filename": "edutrack-progresso.pdf",
            "requires_authentication": True, "scope": "all_time"}


@router.get("/reports/progress.pdf", response_class=Response,
            responses={200: {"content": {"application/pdf": {}}}})
def progress_pdf(request: Request, db: Db, student: Student):
    request.app.state.limiter.check("progress-pdf:" + str(student.id), 10, 60)
    query = (select(Discipline.id, Discipline.nome,
                    func.count(Task.id).label("total"),
                    func.coalesce(func.sum(case((Task.status == "concluida", 1), else_=0)), 0).label("completed"))
             .outerjoin(Task, and_(Task.disciplina_id == Discipline.id,
                                   Task.usuario_id == student.id, Task.status != "cancelada"))
             .where(Discipline.usuario_id == student.id)
             .group_by(Discipline.id, Discipline.nome)
             .order_by(Discipline.nome, Discipline.id)
             .limit(MAX_REPORT_DISCIPLINES + 1))
    rows = db.execute(query).all()
    if len(rows) > MAX_REPORT_DISCIPLINES:
        raise HTTPException(422, "O PDF suporta até 500 disciplinas por conta; nenhum relatório parcial foi gerado.")
    data = [{"name": row.nome, "total": row.total, "completed": row.completed} for row in rows]
    return Response(build_progress_pdf(data, utc_now()), media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="edutrack-progresso.pdf"',
                             "Cache-Control": "no-store"})
