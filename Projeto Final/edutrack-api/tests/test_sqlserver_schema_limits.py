"""Regressão: compilação de DDL não valida limites de tipos do SQL Server."""

import re
from pathlib import Path

from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateTable

from edutrack import integration_models  # noqa: F401 — registrar tabelas
from edutrack.models import Base


def test_sqlserver_unicode_columns_respect_native_size_limit():
    # Valida também o SQL manual: SQLite não detecta NVARCHAR(4096) inválido.
    scripts = [str(CreateTable(t).compile(dialect=mssql.dialect())) for t in Base.metadata.sorted_tables]
    migrations = list((Path(__file__).parents[1] / "migrations").glob("*.sql"))
    assert migrations, "As migrações devem estar presentes na execução deste teste."
    scripts += [p.read_text(encoding="utf-8-sig") for p in migrations]
    for script in scripts:
        for size in re.findall(r"\bN(?:VAR)?CHAR\s*\(\s*(\d+)\s*\)", script, flags=re.IGNORECASE):
            assert 1 <= int(size) <= 4000, f"Tamanho Unicode incompatível com SQL Server: {size}"
