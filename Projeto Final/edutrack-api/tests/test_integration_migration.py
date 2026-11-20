from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateTable

from edutrack.integration_models import (
    ClassroomDisciplineLink,
    ClassroomTaskLink,
    GoogleConnection,
    GoogleOAuthAttempt,
)


def test_sql_server_ddl_compiles_with_unique_keys_and_nullable_history():
    tables = [GoogleConnection, GoogleOAuthAttempt, ClassroomDisciplineLink, ClassroomTaskLink]
    ddl = "\n".join(str(CreateTable(model.__table__).compile(dialect=mssql.dialect())) for model in tables)
    assert "VARCHAR(max)" in ddl and "DATETIME2(3)" in ddl
    assert ddl.count("ON DELETE SET NULL") == 2
    assert "UNIQUE (usuario_id, google_sub, turma_id, atividade_id)" in ddl
    assert "DROP" not in ddl and "ALTER TABLE usuarios" not in ddl
