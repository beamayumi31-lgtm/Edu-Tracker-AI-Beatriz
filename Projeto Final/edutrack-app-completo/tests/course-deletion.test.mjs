import assert from 'node:assert/strict';
import { test } from 'node:test';
import { deleteCourseFromState } from '../app/lib/course-deletion.ts';

const example = () => ({
  courses: [{ id: 'a', title: 'Curso A' }, { id: 'b', title: 'Curso B' }],
  disciplines: [{ id: 'da', courseId: 'a' }, { id: 'db', courseId: 'b' }],
  tasks: [
    { id: 'ta', courseId: 'a', disciplineId: 'da' },
    { id: 'livre', courseId: 'a' },
    { id: 'tb', courseId: 'b', disciplineId: 'db' },
  ],
  sessions: [{ id: 'sa', taskId: 'ta', minutes: 25 }, { id: 'sb', taskId: 'tb', minutes: 45 }, { id: 'foco', minutes: 15 }],
});

test('exclui só o curso escolhido, suas disciplinas e tarefas, sem modificar a entrada', () => {
  const state = example();
  const before = structuredClone(state);
  const result = deleteCourseFromState(state, 'a');
  assert.deepEqual(result.courses, [state.courses[1]]);
  assert.deepEqual(result.disciplines, [state.disciplines[1]]);
  assert.deepEqual(result.tasks, [state.tasks[2]]);
  assert.deepEqual(state, before);
});

test('preserva minutos e sessões, desvinculando apenas as tarefas excluídas', () => {
  const result = deleteCourseFromState(example(), 'a');
  assert.deepEqual(result.sessions.map(({ id, minutes }) => ({ id, minutes })), [
    { id: 'sa', minutes: 25 }, { id: 'sb', minutes: 45 }, { id: 'foco', minutes: 15 },
  ]);
  assert.equal(result.sessions[0].taskId, undefined);
  assert.equal(result.sessions[1].taskId, 'tb');
  const restored = JSON.parse(JSON.stringify(result));
  assert.equal(restored.courses.some((course) => course.id === 'a'), false);
  assert.equal('taskId' in restored.sessions[0], false);
});

test('evita tarefas órfãs quando o vínculo com a disciplina é o único correto', () => {
  const state = example();
  state.tasks.push({ id: 'legada', courseId: '', disciplineId: 'da' });
  assert.deepEqual(deleteCourseFromState(state, 'a').tasks.map((task) => task.id), ['tb']);
});

test('curso inexistente não muda o estado; o último curso pode ser excluído', () => {
  const state = example();
  assert.equal(deleteCourseFromState(state, 'inexistente'), state);
  const result = deleteCourseFromState(deleteCourseFromState(state, 'a'), 'b');
  assert.deepEqual(result.courses, []);
  assert.deepEqual(result.disciplines, []);
  assert.deepEqual(result.tasks, []);
  assert.equal(result.sessions.length, 3);
});
