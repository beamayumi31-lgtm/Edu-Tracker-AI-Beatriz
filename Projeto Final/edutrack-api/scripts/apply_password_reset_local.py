"""Aplicação explícita da migração 003; usar somente após autorização do responsável."""
import argparse
import os
import re
from pathlib import Path

from dotenv import set_key
from sqlalchemy import inspect, text

from edutrack.config import Settings
from edutrack.database import make_engine
from edutrack.run import load_local_secrets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executar", action="store_true")
    args = parser.parse_args()
    if not args.executar:
        raise SystemExit("Somente após autorização: execute com --executar. Nenhuma alteração realizada.")
    load_local_secrets()
    settings = Settings()
    if settings.environment != "development" or settings.sql_server.lower() != r"localhost\sqlexpress" or settings.sql_database != "EduTrackIA" or settings.database_url:
        raise SystemExit("Operação permitida somente em localhost\\SQLEXPRESS / EduTrackIA, desenvolvimento.")
    private_dir = os.environ.get("LOCALAPPDATA")
    if not private_dir:
        raise SystemExit("Ambiente Windows local obrigatório.")
    settings.trust_server_certificate = True
    engine = make_engine(settings)
    source = Path(__file__).resolve().parents[1] / "migrations" / "003_recuperacao_senha.sql"
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        if connection.scalar(text("SELECT DB_NAME()")) != "EduTrackIA":
            raise SystemExit("Banco inesperado; interrompido.")
        tables = inspect(connection).get_table_names()
        before = {name: connection.scalar(text("SELECT COUNT_BIG(*) FROM dbo.[" + name.replace("]", "]]") + "]")) for name in tables}
        try:
            for batch in re.split(r"(?im)^\s*GO\s*$", source.read_text(encoding="utf-8")):
                if batch.strip():
                    connection.exec_driver_sql(batch)
        except Exception:
            connection.exec_driver_sql("IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;")
            raise
        after = {name: connection.scalar(text("SELECT COUNT_BIG(*) FROM dbo.[" + name.replace("]", "]]") + "]")) for name in tables}
        if before != after:
            raise SystemExit("Quantidades alteradas durante a operação; revisar antes de ativar.")
        assert inspect(connection).has_table("recuperacoes_senha")
    engine.dispose()
    target = Path(private_dir) / "EduTrack" / "backend.env"
    target.parent.mkdir(exist_ok=True, parents=True)
    set_key(str(target), "EDUTRACK_PASSWORD_RESET_ENABLED", "true")
    set_key(str(target), "EDUTRACK_FRONTEND_URL", "http://localhost:3002")
    print("Migração 003 aplicada. Quantidades de registros das tabelas anteriores preservadas.")
    print("Recuperação ativada no ambiente privado local. Nenhuma senha ou conta foi alterada.")


if __name__ == "__main__":
    main()
