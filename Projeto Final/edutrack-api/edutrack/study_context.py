"""Contexto acadêmico sempre obtido no servidor a partir do usuário autenticado."""

from fastapi import HTTPException
from sqlalchemy import inspect, select

from edutrack.models import Course, Discipline, Task

CONTEXT_LIMIT = 200


def study_context(db, user_id, *, exclude_classroom=False):
    def rows(model, *conditions):
        return list(
            db.scalars(
                select(model)
                .where(model.usuario_id == user_id, *conditions)
                .order_by(model.id)
                .limit(CONTEXT_LIMIT + 1)
            )
        )

    courses = rows(Course)
    disciplines = rows(Discipline)
    tasks = rows(Task, Task.status.in_(["pendente", "em_andamento"]))
    limit_reached = any(len(items) > CONTEXT_LIMIT for items in (courses, disciplines, tasks))
    if exclude_classroom:
        from edutrack.integration_models import ClassroomDisciplineLink, ClassroomTaskLink

        schema = inspect(db.connection())
        present = [schema.has_table(model.__tablename__) for model in (ClassroomDisciplineLink, ClassroomTaskLink)]
        if any(present) and not all(present):
            raise HTTPException(503, "Migração das integrações incompleta. Use o planejador local.")
        imported_disciplines = set(db.scalars(select(ClassroomDisciplineLink.disciplina_id).where(ClassroomDisciplineLink.usuario_id == user_id))) if all(present) else set()
        imported_tasks = set(db.scalars(select(ClassroomTaskLink.tarefa_id).where(ClassroomTaskLink.usuario_id == user_id))) if all(present) else set()
        disciplines = [d for d in disciplines if d.id not in imported_disciplines]
        tasks = [t for t in tasks if t.id not in imported_tasks and t.disciplina_id not in imported_disciplines]
    # A chave de titularidade nunca vem do navegador nem de argumentos sugeridos pela IA.
    return {
        "cursos": [{"id": str(c.id), "nome": c.nome} for c in courses[:CONTEXT_LIMIT]],
        "disciplinas": [
            {"id": str(d.id), "curso_id": str(d.curso_id), "nome": d.nome}
            for d in disciplines[:CONTEXT_LIMIT]
        ],
        "tarefas": [
            {
                "id": str(t.id),
                "disciplina_id": str(t.disciplina_id),
                "titulo": t.titulo,
                "descricao": (t.descricao or "")[:300],
                "status": t.status,
                "data_prevista": t.data_prevista.isoformat() + "Z" if t.data_prevista else None,
                "minutos_estimados": t.minutos_estimados,
            }
            for t in tasks[:CONTEXT_LIMIT]
        ],
        "limite_atingido": limit_reached,
        "aviso_privacidade": "Somente contexto acadêmico da conta autenticada; sem e-mail, CPF ou senha." + (" Dados importados do Classroom foram excluídos. Use o planejador local para incluí-los." if exclude_classroom else ""),
    }
