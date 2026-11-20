import assert from 'node:assert/strict';
import { test } from 'node:test';
import { weeklyReport, reportCsv } from '../app/lib/weekly-report.ts';

const entry = (id, date, minutes) => ({ id, completedAt: date.toISOString(), minutes });
test('separa segundas de semanas diferentes e inclui limites locais', () => {
  const now = new Date(2026, 10, 8, 23, 59);
  const sessions = [entry('anterior', new Date(2026, 9, 26, 10), 90), entry('segunda', new Date(2026, 10, 2), 25), entry('domingo', new Date(2026, 10, 8, 23, 58), 15), entry('futura', new Date(2026, 10, 9), 50)];
  const current = weeklyReport(sessions, 0, now);
  assert.equal(current.minutes, 40);
  assert.equal(current.days[0].minutes, 25);
  assert.equal(current.days[6].minutes, 15);
  assert.equal(current.activeDays, 2);
  assert.equal(weeklyReport(sessions, -1, now).minutes, 90);
});
test('remove duplicatas e inválidos, preserva virada do ano e CSV consistente', () => {
  const now = new Date(2027, 0, 3, 18);
  const valid = entry('a', new Date(2026, 11, 31, 12), 30);
  const result = weeklyReport([valid, valid, { ...valid, id: 'bad', minutes: -1 }, { ...valid, id: 'date', completedAt: 'invalida' }], 0, now);
  assert.equal(result.days[0].key, '2026-12-28');
  assert.equal(result.days[6].key, '2027-01-03');
  assert.equal(result.minutes, 30);
  assert.equal(result.completed.length, 1);
  assert.match(reportCsv(result), /2026-12-31;Qui;30;1/);
  assert.equal(reportCsv(result).split('\r\n').length, 8);
});
test('semana vazia não inventa minutos ou sessões', () => {
  const result = weeklyReport([], 0, new Date(2026, 10, 3));
  assert.equal(result.minutes, 0);
  assert.ok(result.days.every(day => day.minutes === 0 && day.sessions === 0));
});
