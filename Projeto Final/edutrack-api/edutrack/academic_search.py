"""Busca híbrida: regras Python e filtros parametrizados no banco relacional."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, or_, select

from edutrack.models import Discipline, Task


def discipline_search(user_id: UUID, name: str, overdue: bool, now: datetime):
    """Cria consulta sem N+1; EXISTS não duplica disciplinas com várias pendências."""
    query = select(Discipline).where(Discipline.usuario_id == user_id)
    criteria = []
    if term := name.strip():
        # SQL Server também interpreta '[' em LIKE. Escapar todos os curingas.
        for literal in ("/", "%", "_", "["):
            term = term.replace(literal, "/" + literal)
        criteria.append(Discipline.nome.ilike("%" + term + "%", escape="/"))
    if overdue:
        criteria.append(exists().where(
            Task.disciplina_id == Discipline.id,
            Task.usuario_id == user_id,
            Task.status.in_(("pendente", "em_andamento")),
            Task.data_prevista < now,
        ))
    return query.where(or_(*criteria)) if criteria else query
