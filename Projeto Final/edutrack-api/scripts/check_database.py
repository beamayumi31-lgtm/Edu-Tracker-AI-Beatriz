"""Verifica conexão, colunas e consultas ORM sem criar tabelas ou gravar registros."""

import argparse

from sqlalchemy import inspect, select

from edutrack.config import Settings
from edutrack.database import make_engine
from edutrack.models import Base


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-sql-certificate", action="store_true")
    args = parser.parse_args()
    settings = Settings()
    if args.local_sql_certificate:
        if settings.environment == "production":
            raise SystemExit("A exceção de certificado não é permitida em produção.")
        settings.trust_server_certificate = True
    engine = make_engine(settings)
    try:
        inspector = inspect(engine)
        with engine.connect() as connection:
            for table in Base.metadata.sorted_tables:
                if table.name == "recuperacoes_senha" and not inspector.has_table(table.name):
                    if settings.password_reset_enabled:
                        raise SystemExit("Aplique a migração 003 antes de ativar recuperação de senha.")
                    print("PENDENTE: recuperacoes_senha (recurso desativado; migração não aplicada)")
                    continue
                if table.name == "verificacoes_email" and not inspector.has_table(table.name):
                    if settings.email_verification_enabled:
                        raise SystemExit("Aplique a migração de verificações de e-mail antes de ativar o recurso.")
                    print("PENDENTE: verificacoes_email (recurso desativado; migração não aplicada)")
                    continue
                columns = {column["name"]: column for column in inspector.get_columns(table.name)}
                missing = set(table.columns.keys()) - set(columns)
                if missing:
                    raise SystemExit(
                        f"Colunas ausentes em {table.name}: {', '.join(sorted(missing))}"
                    )
                for column in table.columns:
                    if (column.computed is not None) != ("computed" in columns[column.name]):
                        raise SystemExit(
                            f"Mapeamento de coluna calculada divergente: {table.name}.{column.name}"
                        )
                # TOP 0 valida a consulta e não lê dados pessoais.
                connection.execute(select(table).limit(0))
                print(f"OK: {table.name} ({len(table.columns)} colunas mapeadas)")
        print("Conexão e consultas verificadas. Nenhum registro ou tabela foi alterado.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
