"""Cria exclusivamente o banco vazio aprovado e um login restrito de aplicação."""
import os
import re
import time
from pathlib import Path

import pyodbc

connection_string = (
    'DRIVER={ODBC Driver 18 for SQL Server};SERVER=127.0.0.1,14330;'
    'DATABASE=master;UID=sa;PWD=' + os.environ['MSSQL_SA_PASSWORD'] + ';'
    'Encrypt=yes;TrustServerCertificate=no;HostNameInCertificate=srv1834976.hstgr.cloud'
)
for attempt in range(30):
    try:
        connection = pyodbc.connect(connection_string, autocommit=True, timeout=3)
        break
    except pyodbc.Error as error:
        if attempt == 29:
            reason = str(error).replace(os.environ['MSSQL_SA_PASSWORD'], '[segredo omitido]')
            raise SystemExit('SQL indisponível com TLS validado: ' + reason) from None
        time.sleep(2)

cursor = connection.cursor()
if cursor.execute("SELECT DB_ID('EduTrackIA')").fetchval() is not None:
    raise SystemExit('Banco já existe. Interrompido para preservar dados; revisar migração separadamente.')
cursor.execute('CREATE DATABASE [EduTrackIA]')
for batch in re.split(r'^\s*GO\s*$', Path('/schema.sql').read_text(encoding='utf-8-sig'), flags=re.MULTILINE):
    if batch.strip():
        cursor.execute(batch)
        while cursor.nextset():
            pass
password = os.environ['EDUTRACK_SQL_PASSWORD'].replace("'", "''")
cursor.execute('USE [master]')
cursor.execute("CREATE LOGIN [edutrack_app] WITH PASSWORD=N'" + password + "', CHECK_POLICY=ON, CHECK_EXPIRATION=OFF, DEFAULT_DATABASE=[EduTrackIA]")
cursor.execute('USE [EduTrackIA]')
cursor.execute('CREATE USER [edutrack_app] FOR LOGIN [edutrack_app]')
tables = [row[0] for row in cursor.execute('SELECT name FROM sys.tables WHERE is_ms_shipped=0').fetchall()]
assert len(tables) == 9
for table in tables:
    cursor.execute(f'GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::dbo.[{table}] TO [edutrack_app]')
print(f'Banco novo com {len(tables)} tabelas; login dedicado sem DDL. TLS validado.')
connection.close()
