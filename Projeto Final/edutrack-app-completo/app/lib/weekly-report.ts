import { localDay, studySummary, type StudySession } from './study-game.ts';

/** A semana é de segunda a domingo, no fuso do estudante, sem juntar semanas diferentes. */
export function weeklyReport(sessions: StudySession[], offset = 0, now = new Date()) {
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  start.setDate(start.getDate() - (start.getDay() + 6) % 7 + Math.min(0, Math.trunc(offset)) * 7);
  const end = new Date(start);
  end.setDate(end.getDate() + 7);
  const completed = studySummary(sessions, now).completed.filter((session) => {
    const date = new Date(session.completedAt);
    return date >= start && date < end;
  });
  const days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'].map((label, index) => {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    const key = localDay(date);
    const entries = completed.filter((session) => localDay(new Date(session.completedAt)) === key);
    return { key, label, minutes: entries.reduce((sum, session) => sum + session.minutes, 0), sessions: entries.length };
  });
  return { start, end, days, completed, minutes: completed.reduce((sum, session) => sum + session.minutes, 0), activeDays: days.filter((day) => day.sessions > 0).length };
}

export function reportCsv(report: ReturnType<typeof weeklyReport>) {
  // Conteúdo gerado somente a partir de datas e números: nenhum texto de usuário vira fórmula.
  return '\uFEFFData;Dia;Minutos;Sessoes\r\n' + report.days.map((day) => `${day.key};${day.label};${day.minutes};${day.sessions}`).join('\r\n');
}
