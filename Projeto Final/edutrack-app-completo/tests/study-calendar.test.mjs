import assert from 'node:assert/strict';
import { test } from 'node:test';
import { localDay, studyCalendar, studyCalendarTarget } from '../app/lib/study-game.ts';
import { academicView } from '../app/lib/academic-api.ts';

const now = new Date(2026, 9, 20, 18);
const session = (id, date, minutes = 25) => ({ id, minutes, completedAt: date.toISOString() });

test('calendário vazio mostra o período real e não inventa estudo', () => {
  const result = studyCalendar([], 12, now);
  assert.equal(result.firstKey, '2025-10-21');
  assert.equal(result.lastKey, '2026-10-20');
  assert.equal(result.days.length, 365);
  assert.equal(result.activeDays, 0);
  assert.equal(result.totalMinutes, 0);
  assert.equal(result.totalSessions, 0);
  assert.equal(result.streak, 0);
  assert.ok(result.days.every((day) => day.level === 0 && day.sessions === 0));
  assert.equal(result.days.filter((day) => day.today).length, 1);
  assert.equal(result.days.at(-1).today, true);
});

test('soma sessões do mesmo dia e aplica os cinco níveis de cor', () => {
  const sessions = [1, 24, 25, 49, 50, 99, 100, 240].map((minutes, index) =>
    session(`sessao-${index}`, new Date(2026, 9, 10 + index, 12), minutes));
  sessions.push(session('segunda-no-dia', new Date(2026, 9, 18, 10), 25));
  sessions.push(session('terceira-no-dia', new Date(2026, 9, 18, 14), 75));
  const result = studyCalendar(sessions, 3, now);
  assert.deepEqual(result.days.filter((day) => day.minutes).map((day) => day.level), [1, 1, 2, 2, 3, 3, 4, 4, 4]);
  assert.equal(result.days.find((day) => day.key === '2026-10-18').sessions, 2);
  assert.equal(result.days.find((day) => day.key === '2026-10-18').minutes, 100);
  assert.equal(result.activeDays, 9);
  assert.equal(result.totalSessions, 10);
  assert.equal(result.totalMinutes, 688);
});

test('ignora duplicatas, datas futuras, valores inválidos e dias fora do filtro', () => {
  const valid = session('valida', new Date(2026, 9, 20, 12));
  const invalid = [0, -1, NaN, Infinity].map((minutes, index) => ({ ...valid, id: `invalida-${index}`, minutes }));
  const result = studyCalendar([
    valid, valid, ...invalid,
    { id: 'data-invalida', minutes: 25, completedAt: 'sem-data' },
    session('futura', new Date(2026, 9, 20, 19)),
    session('fora', new Date(2026, 6, 20, 12)),
    session('limite', new Date(2026, 6, 21, 12), 15),
  ], 3, now);
  assert.equal(result.totalMinutes, 40);
  assert.equal(result.activeDays, 2);
  assert.equal(result.totalSessions, 2);
});

test('cada coluna começa na segunda e espaços fora do período não são dias clicáveis', () => {
  const result = studyCalendar([], 12, now);
  assert.equal(result.weeks[0][0], null);
  assert.equal(result.weeks.at(-1)[2], null);
  for (const week of result.weeks) {
    assert.equal(week.length, 7);
    week.forEach((day, index) => {
      if (day) assert.equal((new Date(day.key + 'T12:00:00').getDay() + 6) % 7, index);
    });
  }
  assert.equal(new Set(result.days.map((day) => day.key)).size, result.days.length);
});

test('filtros preservam o dia local e o calendário em anos bissextos e finais de mês', () => {
  const cases = [
    [new Date(2024, 1, 29, 18), 12, '2023-03-01', 366],
    [new Date(2025, 1, 28, 18), 12, '2024-02-29', 366],
    [new Date(2026, 4, 31, 18), 3, '2026-03-01', 92],
    [new Date(2026, 0, 1, 18), 3, '2025-10-02', 92],
  ];
  for (const [date, months, firstKey, length] of cases) {
    const result = studyCalendar([], months, date);
    assert.equal(result.firstKey, firstKey);
    assert.equal(result.days.length, length);
    assert.equal(result.lastKey, localDay(date));
  }
  for (const months of [3, 6, 12]) {
    const result = studyCalendar([], months, now);
    for (let index = 1; index < result.days.length; index += 1) {
      const previous = new Date(result.days[index - 1].key + 'T12:00:00');
      previous.setDate(previous.getDate() + 1);
      assert.equal(result.days[index].key, localDay(previous));
    }
  }
});

test('sessão pertence ao dia local da conclusão, inclusive perto da meia-noite', () => {
  const date = new Date(2026, 9, 20, 0, 5);
  const result = studyCalendar([session('madrugada', date)], 3, now);
  assert.equal(result.days.find((day) => day.minutes).key, localDay(date));
});

test('resumo do período não muda a ofensiva atual quando o filtro muda', () => {
  const sessions = [19, 20].map((day) => session(String(day), new Date(2026, 9, day, 12)));
  sessions.push(session('antiga', new Date(2026, 0, 1, 12), 60));
  assert.equal(studyCalendar(sessions, 3, now).streak, 2);
  assert.equal(studyCalendar(sessions, 12, now).streak, 2);
  assert.equal(studyCalendar(sessions, 3, now).totalMinutes, 50);
  assert.equal(studyCalendar(sessions, 12, now).totalMinutes, 110);
});

test('setas, Home e End navegam com limites e sem prender outras teclas', () => {
  assert.equal(studyCalendarTarget('ArrowUp', 12, 365), 11);
  assert.equal(studyCalendarTarget('ArrowDown', 12, 365), 13);
  assert.equal(studyCalendarTarget('ArrowLeft', 12, 365), 5);
  assert.equal(studyCalendarTarget('ArrowRight', 12, 365), 19);
  assert.equal(studyCalendarTarget('ArrowLeft', 3, 365), 0);
  assert.equal(studyCalendarTarget('ArrowRight', 364, 365), 364);
  assert.equal(studyCalendarTarget('Home', 300, 365), 0);
  assert.equal(studyCalendarTarget('End', 0, 365), 364);
  assert.equal(studyCalendarTarget('Tab', 20, 365), null);
  assert.equal(studyCalendarTarget('Enter', 20, 365), null);
});

test('integra sessões da API sem alterar cursos, disciplinas, tarefas ou perfil existentes', () => {
  const user = { id: 'aluno-teste', nome: 'Aluno de teste', email: 'aluno@example.invalid', role: 'student', criado_em: '2026-01-01T12:00:00Z' };
  const data = {
    courses: [{ id: 'curso-teste', nome: 'Curso existente', instituicao: 'Instituição de teste', data_inicio: '2026-01-01', data_fim: null }],
    disciplines: [{ id: 'disciplina-teste', curso_id: 'curso-teste', nome: 'Disciplina existente', professor: 'Professor de teste', carga_horaria: 40 }],
    tasks: ['pendente', 'concluida'].map((status, index) => ({ id: `tarefa-${index}`, disciplina_id: 'disciplina-teste', titulo: `Tarefa existente ${index}`, descricao: 'Descrição preservada', data_prevista: null, status, minutos_estimados: 25, concluido_em: null })),
    sessions: [19, 20].map((day) => ({ id: `sessao-${day}`, tarefa_id: 'tarefa-0', iniciado_em: new Date(2026, 9, day, 12).toISOString(), finalizado_em: new Date(2026, 9, day, 12, 25).toISOString(), duracao_minutos: 25 })),
  };
  const originalData = structuredClone(data);
  const originalUser = structuredClone(user);
  const view = academicView(data, user);
  const originalView = structuredClone(view);
  const calendar = studyCalendar(view.sessions, 12, now);
  assert.equal(calendar.totalMinutes, 50);
  assert.equal(calendar.totalSessions, 2);
  assert.equal(calendar.activeDays, 2);
  assert.equal(calendar.streak, 2);
  assert.equal(view.courses[0].progress, 50);
  assert.equal(view.courses[0].title, 'Curso existente');
  assert.equal(view.disciplines[0].title, 'Disciplina existente');
  assert.equal(view.tasks[0].notes, 'Descrição preservada');
  assert.equal(view.profile.name, user.nome);
  assert.deepEqual(view, originalView);
  assert.deepEqual(data, originalData);
  assert.deepEqual(user, originalUser);
});

test('conta sem sessões permanece vazia depois de calcular histórico de outra conta', () => {
  const first = studyCalendar([session('somente-primeira-conta', new Date(2026, 9, 20, 12))], 12, now);
  const empty = academicView({ courses: [], disciplines: [], tasks: [], sessions: [] },
    { id: 'segunda-conta', nome: 'Outra conta', email: 'outra@example.invalid', role: 'student', criado_em: '2026-01-01T12:00:00Z' });
  const second = studyCalendar(empty.sessions, 12, now);
  assert.equal(first.totalMinutes, 25);
  assert.equal(second.totalMinutes, 0);
  assert.equal(second.activeDays, 0);
  assert.equal(second.streak, 0);
});
