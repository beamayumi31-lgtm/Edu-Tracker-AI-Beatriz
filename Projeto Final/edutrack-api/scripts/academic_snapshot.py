"""Explicit, transaction-scoped academic snapshot/clear/restore. No CLI or connections.
Caller must use a transaction, persist the snapshot privately, rehearse restoration,
and rollback on ANY exception. No function commits. Never exports account secrets.
"""
import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, insert, select

from edutrack.integration_models import ClassroomContent, ClassroomDisciplineLink, ClassroomTaskLink
from edutrack.models import Base, Course, Discipline, Task, TimeEntry

TABLES = tuple(model.__table__ for model in (
    Course, Discipline, Task, ClassroomDisciplineLink, ClassroomTaskLink,
    ClassroomContent, TimeEntry,
))


def _encode(value):
    if isinstance(value, (UUID, datetime, date, Decimal, bytes)):
        return {'$type': type(value).__name__, 'value': value.hex() if isinstance(value, bytes) else str(value)}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError('Unsupported snapshot value')


def _decode(value):
    if not isinstance(value, dict):
        return value
    constructors = {'UUID': UUID, 'datetime': datetime.fromisoformat, 'date': date.fromisoformat, 'Decimal': Decimal, 'bytes': bytes.fromhex}
    return constructors[value['$type']](value['value'])


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def _scope(table, owner):
    if table.name == TimeEntry.__tablename__:
        return table.c.tarefa_id.in_(select(Task.id).where(Task.usuario_id == owner))
    return table.c.usuario_id == owner


def _rows(conn, table, predicate=None):
    statement = select(table)
    if predicate is not None:
        statement = statement.where(predicate)
    rows = [{key: _encode(value) for key, value in row.items()} for row in conn.execute(statement).mappings()]
    return sorted(rows, key=canonical)


def snapshot(conn, owner):
    owner = UUID(str(owner))
    payload = {'version': 1, 'owner': str(owner), 'tables': {t.name: _rows(conn, t, _scope(t, owner)) for t in TABLES}}
    return {**payload, 'sha256': digest(payload)}


def validate_snapshot(data):
    payload = {key: value for key, value in data.items() if key != 'sha256'}
    if set(payload) != {'version', 'owner', 'tables'} or payload['version'] != 1 or digest(payload) != data.get('sha256'):
        raise ValueError('Invalid snapshot hash or format')
    owner = UUID(data['owner'])
    if set(data['tables']) != {t.name for t in TABLES}:
        raise ValueError('Invalid snapshot tables')
    task_ids = {_decode(r['id']) for r in data['tables'][Task.__tablename__]}
    for table in TABLES:
        for row in data['tables'][table.name]:
            if set(row) != {c.name for c in table.columns}:
                raise ValueError('Snapshot column mismatch')
            decoded = {k: _decode(v) for k, v in row.items()}
            if table.name == TimeEntry.__tablename__:
                if decoded['tarefa_id'] not in task_ids:
                    raise ValueError('Foreign task in snapshot')
            elif decoded['usuario_id'] != owner:
                raise ValueError('Foreign owner in snapshot')
    return owner


def protected_fingerprints(conn, owner):
    """Hash every non-target row, including entire account/Google tables; no raw export."""
    owner = UUID(str(owner))
    targets = {t.name for t in TABLES}
    return {table.name: digest(_rows(conn, table, ~_scope(table, owner) if table.name in targets else None))
            for table in Base.metadata.sorted_tables}


def clear(conn, data):
    """Must run in caller-owned transaction. Hash-check stale snapshot before any delete."""
    owner = validate_snapshot(data)
    if not conn.in_transaction():
        raise ValueError('Explicit caller transaction required')
    if snapshot(conn, owner) != data:
        raise ValueError('Snapshot stale; abort and create a new private snapshot')
    protected = protected_fingerprints(conn, owner)
    # Refuse cross-owner links that SET NULL could otherwise silently alter.
    for model, target, column in ((ClassroomDisciplineLink, Discipline, 'disciplina_id'), (ClassroomTaskLink, Task, 'tarefa_id')):
        if conn.execute(select(model.id).where(model.usuario_id != owner, getattr(model, column).in_(select(target.id).where(target.usuario_id == owner)))).first():
            raise ValueError('Cross-owner reference; manual investigation required')
    for table in reversed(TABLES):
        conn.execute(delete(table).where(_scope(table, owner)))
    if protected_fingerprints(conn, owner) != protected:
        raise RuntimeError('Protected rows changed; ROLLBACK required')
    if any(snapshot(conn, owner)['tables'].values()):
        raise RuntimeError('Incomplete clear; ROLLBACK required')


def restore(conn, data):
    owner = validate_snapshot(data)
    if not conn.in_transaction():
        raise ValueError('Explicit caller transaction required')
    if any(snapshot(conn, owner)['tables'].values()):
        raise ValueError('Restore requires empty owner academic data')
    protected = protected_fingerprints(conn, owner)
    for table in TABLES:
        for row in data['tables'][table.name]:
            values = {c.name: _decode(row[c.name]) for c in table.columns if c.computed is None}
            conn.execute(insert(table).values(**values))
    if snapshot(conn, owner) != data or protected_fingerprints(conn, owner) != protected:
        raise RuntimeError('Restoration mismatch; ROLLBACK required')
