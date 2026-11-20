"""Backup nativo com checksum e VERIFYONLY, usando TLS e credencial privada."""
import os
import re
import sys

import pyodbc

name = sys.argv[1]
if not re.fullmatch(r'EduTrackIA_\d{8}T\d{6}Z\.bak', name):
    raise SystemExit('Nome de backup inválido.')
connection = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};SERVER=127.0.0.1,14330;'
    'DATABASE=master;UID=sa;PWD=' + os.environ['MSSQL_SA_PASSWORD'] + ';'
    'Encrypt=yes;TrustServerCertificate=no;HostNameInCertificate=srv1834976.hstgr.cloud',
    autocommit=True, timeout=10,
)
cursor = connection.cursor()
path = '/var/opt/mssql/backup/' + name
for statement in [f"BACKUP DATABASE [EduTrackIA] TO DISK=N'{path}' WITH COPY_ONLY, CHECKSUM",
                  f"RESTORE VERIFYONLY FROM DISK=N'{path}' WITH CHECKSUM"]:
    cursor.execute(statement)
    while cursor.nextset():
        pass
connection.close()
print('Backup nativo e VERIFYONLY concluídos: ' + name)
