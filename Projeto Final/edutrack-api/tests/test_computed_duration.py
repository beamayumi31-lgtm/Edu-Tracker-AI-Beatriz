from datetime import datetime, timedelta, timezone
from uuid import uuid4

from conftest import academic_data
from sqlalchemy import insert
from sqlalchemy.dialects import mssql, sqlite
from sqlalchemy.schema import CreateTable

from edutrack.models import TimeEntry


def test_time_entry_marks_duration_as_generated():
    column = TimeEntry.__table__.c.duracao_minutos
    assert column.computed is not None
    assert column.computed.persisted is True
    # Compilação apenas: nenhum CREATE TABLE é executado no SQL Server.
    sql_server_ddl = str(CreateTable(TimeEntry.__table__).compile(dialect=mssql.dialect()))
    sqlite_ddl = str(CreateTable(TimeEntry.__table__).compile(dialect=sqlite.dialect()))
    assert "DATEDIFF(minute, iniciado_em, finalizado_em)" in sql_server_ddl
    assert "PERSISTED" in sql_server_ddl
    assert "GENERATED ALWAYS AS" in sqlite_ddl and "STORED" in sqlite_ddl


def test_sql_server_insert_reads_but_does_not_write_computed_duration():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    statement = (
        insert(TimeEntry)
        .values(
            id=uuid4(),
            tarefa_id=uuid4(),
            iniciado_em=now - timedelta(minutes=25),
            finalizado_em=now,
        )
        .return_defaults()
    )
    compiled = str(statement.compile(dialect=mssql.dialect()))
    columns = compiled.split("OUTPUT")[0]
    assert "duracao_minutos" not in columns
    assert "inserted.duracao_minutos" in compiled


def test_session_uses_database_minute_boundaries(client, auth):
    _, _, task = academic_data(client, auth)
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    start = yesterday.replace(hour=10, minute=0, second=50, microsecond=0)
    end = yesterday.replace(hour=10, minute=2, second=0, microsecond=0)
    response = client.post(
        "/api/study-sessions",
        headers=auth,
        json={
            "tarefa_id": task["id"],
            "iniciado_em": start.isoformat(),
            "finalizado_em": end.isoformat(),
        },
    )
    assert response.status_code == 201
    # SQL Server conta duas viradas de minuto, não floor(70 segundos / 60).
    assert response.json()["duracao_minutos"] == 2
    assert (
        client.get("/api/study-sessions", headers=auth).json()["items"][0]["duracao_minutos"] == 2
    )
