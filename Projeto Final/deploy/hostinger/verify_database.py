"""Verificação somente de leitura, sem imprimir usuários ou credenciais."""
import json

from edutrack.config import Settings
from edutrack.models import Base
from sqlalchemy import create_engine, text

settings = Settings()
assert settings.environment == 'production'
engine = create_engine(settings.sqlalchemy_url(), hide_parameters=True)
with engine.connect() as connection:
    tables = {table.name: connection.execute(text(f'SELECT COUNT_BIG(*) FROM [{table.name}]')).scalar_one()
              for table in Base.metadata.sorted_tables}
    result = {'edition': connection.execute(text("SELECT SERVERPROPERTY('Edition')")).scalar_one(),
              'sysadmin': connection.execute(text("SELECT IS_SRVROLEMEMBER('sysadmin')")).scalar_one(),
              'create_table': connection.execute(text("SELECT HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'CREATE TABLE')")).scalar_one(),
              'contagens': tables}
    assert result['sysadmin'] == 0 and result['create_table'] == 0
    print(json.dumps(result, ensure_ascii=False))
engine.dispose()
