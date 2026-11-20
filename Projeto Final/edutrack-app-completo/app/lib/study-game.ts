export type StudySession = { id: string; minutes: number; completedAt: string; taskId?: string };
export type FocusRun = {
  id: string; mode: 'focus' | 'break'; minutes: number;
  remaining: number; endsAt: number | null; taskId?: string;
};

export function localDay(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

/** Datas locais evitam mudar a ofensiva antes da meia-noite do estudante. */
export function studySummary(sessions: StudySession[], now = new Date()) {
  const today = localDay(now);
  const days = new Set<string>();
  const seen = new Set<string>();
  const completed = sessions.filter((session) => {
    const date = new Date(session.completedAt);
    if (seen.has(session.id) || !Number.isFinite(date.getTime()) || date > now || !Number.isFinite(session.minutes) || session.minutes <= 0) return false;
    seen.add(session.id);
    days.add(localDay(date));
    return true;
  });
  const cursor = new Date(now);
  cursor.setHours(12, 0, 0, 0);
  if (!days.has(today)) cursor.setDate(cursor.getDate() - 1);
  let streak = 0;
  while (days.has(localDay(cursor))) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  let best = 0;
  let sequence = 0;
  let previous = '';
  for (const day of [...days].sort()) {
    const yesterday = new Date(day + 'T12:00:00');
    yesterday.setDate(yesterday.getDate() - 1);
    sequence = previous === localDay(yesterday) ? sequence + 1 : 1;
    best = Math.max(best, sequence);
    previous = day;
  }
  const week = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(now);
    date.setDate(date.getDate() - ((date.getDay() + 6) % 7) + index);
    const key = localDay(date);
    return { key, label: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'][index], day: date.getDate(), done: days.has(key), today: key === today, future: key > today };
  });
  return { streak, best, week, completed, studiedToday: days.has(today),
    totalMinutes: completed.reduce((sum, session) => sum + session.minutes, 0),
    todayMinutes: completed.filter((session) => localDay(new Date(session.completedAt)) === today).reduce((sum, session) => sum + session.minutes, 0),
    activeDays: days.size };
}

export type StudyDay = { key: string; minutes: number; sessions: number; level: number; today: boolean };

/** Calendário por dia local de conclusão. Reutiliza a validação e deduplicação da ofensiva. */
export function studyCalendar(sessions: StudySession[], months: 3 | 6 | 12 = 12, now = new Date()) {
  const summary = studySummary(sessions, now);
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12);
  const start = new Date(end.getFullYear(), end.getMonth() - months, 1, 12);
  const lastDay = new Date(start.getFullYear(), start.getMonth() + 1, 0).getDate();
  start.setDate(Math.min(end.getDate(), lastDay) + 1);
  const firstKey = localDay(start);
  const lastKey = localDay(end);
  const totals = new Map<string, { minutes: number; sessions: number }>();
  for (const session of summary.completed) {
    const key = localDay(new Date(session.completedAt));
    if (key < firstKey || key > lastKey) continue;
    const previous = totals.get(key) ?? { minutes: 0, sessions: 0 };
    totals.set(key, { minutes: previous.minutes + session.minutes, sessions: previous.sessions + 1 });
  }
  const cursor = new Date(start);
  cursor.setDate(cursor.getDate() - ((cursor.getDay() + 6) % 7));
  const weeks: (StudyDay | null)[][] = [];
  const days: StudyDay[] = [];
  while (cursor <= end) {
    const week: (StudyDay | null)[] = [];
    for (let index = 0; index < 7; index += 1) {
      const key = localDay(cursor);
      const value = totals.get(key) ?? { minutes: 0, sessions: 0 };
      const day = key < firstKey || key > lastKey ? null : {
        key, ...value, today: key === lastKey,
        level: value.minutes === 0 ? 0 : value.minutes < 25 ? 1 : value.minutes < 50 ? 2 : value.minutes < 100 ? 3 : 4,
      };
      week.push(day);
      if (day) days.push(day);
      // Incrementos de calendário, e não de 24 horas, preservam dias em mudanças de fuso.
      cursor.setDate(cursor.getDate() + 1);
    }
    weeks.push(week);
  }
  return { weeks, days, firstKey, lastKey, activeDays: totals.size,
    totalMinutes: days.reduce((sum, day) => sum + day.minutes, 0),
    totalSessions: days.reduce((sum, day) => sum + day.sessions, 0), streak: summary.streak };
}

/** Uma parada de Tab; setas percorrem dias e semanas sem centenas de paradas. */
export function studyCalendarTarget(key: string, current: number, count: number) {
  const delta: Record<string, number> = { ArrowUp: -1, ArrowDown: 1, ArrowLeft: -7, ArrowRight: 7 };
  if (key === 'Home') return 0;
  if (key === 'End') return count - 1;
  return key in delta ? Math.max(0, Math.min(count - 1, current + delta[key])) : null;
}

export function remainingSeconds(run: FocusRun, now = Date.now()) {
  return run.endsAt === null ? run.remaining : Math.max(0, Math.min(run.minutes * 60, Math.ceil((run.endsAt - now) / 1000)));
}

/** Só o término real de um bloco de foco gera sessão e árvore; pausas não geram pontos. */
export function completedFocusSession(run: FocusRun, now = Date.now()): StudySession | null {
  if (run.mode !== 'focus' || run.endsAt === null || remainingSeconds(run, now) > 0) return null;
  return { id: run.id, minutes: run.minutes, taskId: run.taskId, completedAt: new Date(run.endsAt).toISOString() };
}

export function restoreFocusRun(value: unknown): FocusRun | null {
  if (!value || typeof value !== 'object') return null;
  const run = value as FocusRun;
  if (typeof run.id !== 'string' || !['focus', 'break'].includes(run.mode) || !Number.isInteger(run.minutes) || run.minutes < 1 || run.minutes > 120 || !Number.isFinite(run.remaining) || run.remaining <= 0 || run.remaining > run.minutes * 60 || (run.endsAt !== null && (!Number.isFinite(run.endsAt) || run.endsAt <= 0)) || (run.taskId !== undefined && typeof run.taskId !== 'string')) return null;
  return run;
}
