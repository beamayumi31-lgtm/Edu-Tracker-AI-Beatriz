import json
from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, insert

from edutrack.integration_models import (
    ClassroomContent,
    ClassroomDisciplineLink,
    ClassroomTaskLink,
    GoogleConnection,
)
from edutrack.models import Base, Course, Discipline, Task, TimeEntry, User
from scripts.academic_snapshot import clear, protected_fingerprints, restore, snapshot


@pytest.fixture
def database():
    engine = create_engine('sqlite://')
    @event.listens_for(engine, 'connect')
    def foreign_keys(dbapi, _):
        dbapi.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    owners = [uuid4(), uuid4()]
    with engine.begin() as conn:
        for i, owner in enumerate(owners):
            course, discipline, task = uuid4(), uuid4(), uuid4()
            conn.execute(insert(User).values(id=owner, nome=f'Test{i}', email=f'{i}@example.com', senha_hash='synthetic'))
            conn.execute(insert(GoogleConnection).values(usuario_id=owner, google_sub=str(i), email=f'{i}@example.com', refresh_cifrado='synthetic-cipher', versao=uuid4()))
            conn.execute(insert(Course).values(id=course, usuario_id=owner, nome='Course', data_inicio=date(2026, 1, 1)))
            conn.execute(insert(Discipline).values(id=discipline, curso_id=course, usuario_id=owner, nome='Discipline'))
            conn.execute(insert(Task).values(id=task, disciplina_id=discipline, usuario_id=owner, titulo='Task', data_prevista=datetime(2026, 1, 2, 12, 30)))
            conn.execute(insert(ClassroomDisciplineLink).values(usuario_id=owner, google_sub=str(i), turma_id='class', disciplina_id=discipline))
            conn.execute(insert(ClassroomTaskLink).values(usuario_id=owner, google_sub=str(i), turma_id='class', atividade_id='activity', tarefa_id=task))
            conn.execute(insert(ClassroomContent).values(usuario_id=owner, google_sub=str(i), turma_id='class', origem_id='content', tipo='material', disciplina_id=discipline, titulo='Content', descricao='Description', topico='Topic', anexos_json='[]'))
            start = datetime(2026, 1, 2, 12, 0)
            conn.execute(insert(TimeEntry).values(tarefa_id=task, iniciado_em=start, finalizado_em=start + timedelta(minutes=25)))
    yield engine, owners
    engine.dispose()


def test_json_roundtrip_clear_restore_exact_all_seven_tables(database):
    engine, (owner, other) = database
    with engine.begin() as conn:
        before = snapshot(conn, owner)
        saved = json.loads(json.dumps(before))
        protected = protected_fingerprints(conn, owner)
        other_before = snapshot(conn, other)
        assert len(saved['tables']) == 7
        assert 'usuarios' not in saved['tables'] and 'conexoes_google' not in saved['tables']
        assert saved['tables']['registros_tempo_tarefa'][0]['duracao_minutos'] == 25
        clear(conn, saved)
        assert not any(snapshot(conn, owner)['tables'].values())
        assert protected_fingerprints(conn, owner) == protected
        restore(conn, saved)
        assert snapshot(conn, owner) == before
        assert snapshot(conn, other) == other_before
        assert protected_fingerprints(conn, owner) == protected


def test_stale_and_corrupt_snapshot_do_not_delete(database):
    engine, (owner, _) = database
    with engine.begin() as conn:
        before = snapshot(conn, owner)
        corrupt = json.loads(json.dumps(before))
        corrupt['owner'] = str(uuid4())
        with pytest.raises(ValueError):
            clear(conn, corrupt)
        conn.execute(insert(Course).values(usuario_id=owner, nome='New data'))
        current = snapshot(conn, owner)
        with pytest.raises(ValueError, match='stale'):
            clear(conn, before)
        assert snapshot(conn, owner) == current


def test_restore_refuses_nonempty_owner(database):
    engine, (owner, _) = database
    with engine.begin() as conn:
        saved = snapshot(conn, owner)
        with pytest.raises(ValueError, match='empty'):
            restore(conn, saved)
        assert snapshot(conn, owner) == saved


def test_cross_owner_link_rejected_before_delete(database):
    engine, (owner, other) = database
    with engine.begin() as conn:
        saved = snapshot(conn, owner)
        from scripts.academic_snapshot import _decode
        task_id = _decode(saved['tables']['tarefas_academicas'][0]['id'])
        conn.execute(insert(ClassroomTaskLink).values(usuario_id=other, google_sub='other', turma_id='other-class', atividade_id='foreign-link', tarefa_id=task_id))
        protected = protected_fingerprints(conn, owner)
        with pytest.raises(ValueError, match='Cross-owner'):
            clear(conn, saved)
        assert snapshot(conn, owner) == saved
        assert protected_fingerprints(conn, owner) == protected
