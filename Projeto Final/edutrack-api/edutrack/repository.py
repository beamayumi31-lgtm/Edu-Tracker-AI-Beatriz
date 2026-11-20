from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError


def owned(db, model, item_id, user_id):
    item = db.scalar(select(model).where(model.id == item_id, model.usuario_id == user_id))
    if item is None:
        # Não distinguir IDs inexistentes de IDs pertencentes a outra conta.
        raise HTTPException(404, "Registro não encontrado.")
    return item


def commit(db, message="A operação conflita com registros existentes."):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, message) from None


def page(db, model, user_id, schema, limit, offset, *filters):
    criteria = (model.usuario_id == user_id, *filters)
    total = db.scalar(select(func.count()).select_from(model).where(*criteria))
    rows = db.scalars(
        select(model)
        .where(*criteria)
        .order_by(model.criado_em.desc(), model.id)
        .offset(offset)
        .limit(limit)
    )
    return {
        "items": [schema.model_validate(row) for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
