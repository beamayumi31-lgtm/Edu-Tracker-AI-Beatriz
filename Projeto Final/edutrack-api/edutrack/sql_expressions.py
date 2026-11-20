"""Expressões de colunas calculadas, sem executar alterações no banco existente."""

from sqlalchemy import Integer
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ColumnElement


class SessionMinutes(ColumnElement):
    """Espelha o DATEDIFF(minute) já existente no SQL Server."""

    inherit_cache = True
    type = Integer()


@compiles(SessionMinutes, "mssql")
def session_minutes_mssql(element, compiler, **kwargs):
    return (
        "CASE WHEN finalizado_em IS NULL THEN NULL "
        "ELSE DATEDIFF(minute, iniciado_em, finalizado_em) END"
    )


@compiles(SessionMinutes, "sqlite")
def session_minutes_sqlite(element, compiler, **kwargs):
    # Exclusivo dos testes em memória: reproduz a contagem de viradas de minuto,
    # inclusive antes de 1970, truncando os segundos antes de converter o instante.
    return (
        "CASE WHEN finalizado_em IS NULL THEN NULL ELSE "
        "(CAST(strftime('%s', strftime('%Y-%m-%d %H:%M:00', finalizado_em)) AS INTEGER) "
        "- CAST(strftime('%s', strftime('%Y-%m-%d %H:%M:00', iniciado_em)) AS INTEGER)) / 60 END"
    )
