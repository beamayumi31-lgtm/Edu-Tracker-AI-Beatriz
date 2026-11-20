import assert from 'node:assert/strict';
import { test } from 'node:test';
import { studySummary, remainingSeconds, completedFocusSession, restoreFocusRun } from '../app/lib/study-game.ts';

const now = new Date(2026, 8, 22, 18);
const session = (day, id = String(day), minutes = 25) => ({ id, minutes, completedAt: new Date(2026, 8, day, 12).toISOString() });

test('ofensiva conta dias únicos, mantém ontem e reinicia após um dia perdido', () => {
  assert.equal(studySummary([], now).streak, 0);
  const result = studySummary([session(20), session(21), session(22), session(22, 'outra')], now);
  assert.equal(result.streak, 3);
  assert.equal(result.best, 3);
  assert.equal(result.todayMinutes, 50);
  assert.equal(result.week.length, 7);
  assert.equal(result.week.filter((day) => day.today).length, 1);
  assert.equal(studySummary([session(20), session(21)], now).streak, 2);
  assert.equal(studySummary([session(18), session(19), session(20)], now).streak, 0);
  assert.equal(studySummary([session(18), session(19), session(20)], now).best, 3);
});
test('ignora duplicatas, dados inválidos, duração zero e datas futuras', () => {
  const result = studySummary([session(22), session(22), session(23), session(21, 'zero', 0), { id: 'bad', minutes: 10, completedAt: 'inválido' }], now);
  assert.equal(result.completed.length, 1);
  assert.equal(result.totalMinutes, 25);
});
test('calendário lida com virada de mês e ano no horário local', () => {
  const sessions = [30, 31].map((day) => ({ id: String(day), minutes: 15, completedAt: new Date(2025, 11, day, 12).toISOString() }));
  sessions.push({ id: 'janeiro', minutes: 25, completedAt: new Date(2026, 0, 1, 12).toISOString() });
  assert.equal(studySummary(sessions, new Date(2026, 0, 1, 18)).streak, 3);
});
test('relógio usa prazo absoluto e só foco concluído rende uma sessão', () => {
  const run = { id: 'unique', mode: 'focus', minutes: 25, remaining: 1500, endsAt: 1500000 };
  assert.equal(remainingSeconds(run, 1499500), 1);
  assert.equal(remainingSeconds(run, 1600000), 0);
  assert.equal(completedFocusSession(run, 1499500), null);
  assert.equal(completedFocusSession({ ...run, mode: 'break' }, 1600000), null);
  assert.equal(completedFocusSession({ ...run, endsAt: null }, 1600000), null);
  assert.deepEqual(completedFocusSession(run, 1600000), { id: 'unique', minutes: 25, taskId: undefined, completedAt: new Date(1500000).toISOString() });
  assert.equal(remainingSeconds({ ...run, endsAt: null, remaining: 240 }, 9999999), 240);
  assert.equal(restoreFocusRun(run).id, 'unique');
  assert.equal(restoreFocusRun({ ...run, minutes: -1 }), null);
});
