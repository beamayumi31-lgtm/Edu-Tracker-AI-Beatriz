import type { AcademicData, ApiCourse, ApiDiscipline, ApiSession, ApiTask, Course, Discipline, Profile, ApiUser, StudyTask } from './academic-types';

export class ApiError extends Error {
  status: number;
  code?: string;
  constructor(message: string, status: number, code?: string) { super(message); this.status = status; this.code = code; }
}

let activeUser: string | null = null;
export function setApiUser(id: string | null) { activeUser = id; }

export async function progressReportPdf(): Promise<Blob> {
  const requestUser = activeUser;
  const link = await api<{ download_url: string }>('reports/generate');
  if (link.download_url !== '/api/reports/progress.pdf') throw new Error('Caminho do relatório inválido.');
  const response = await fetch('/api/backend/reports/progress.pdf', {
    cache: 'no-store', credentials: 'same-origin',
    headers: requestUser ? { 'X-EduTrack-User': requestUser } : {},
  });
  if (requestUser !== activeUser) throw new Error('A conta mudou. Gere o relatório novamente.');
  if (!response.ok) {
    if (response.status === 401) window.dispatchEvent(new Event('edutrack-session-expired'));
    const error = await response.json().catch(() => null) as { detail?: unknown } | null;
    throw new Error(typeof error?.detail === 'string' ? error.detail : 'Não foi possível gerar o PDF.');
  }
  if (!response.headers.get('content-type')?.includes('application/pdf')) throw new Error('Resposta do relatório inválida.');
  return response.blob();
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const requestUser = activeUser;
  const response = await fetch('/api/backend/' + path, {
    ...options, cache: 'no-store', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...(activeUser && !(path === 'me' && !options.method) && !path.startsWith('auth/') ? { 'X-EduTrack-User': activeUser } : {}), ...options.headers },
  });
  if (response.status === 204) return undefined as T;
  const result = await response.json().catch(() => null) as { detail?: string | { code?: string; message?: string } | { loc?: string[]; msg?: string }[] } | null;
  if (!response.ok) {
    const problem = result?.detail && typeof result.detail === 'object' && !Array.isArray(result.detail) ? result.detail : null;
    const message = typeof result?.detail === 'string' ? result.detail
      : Array.isArray(result?.detail) ? result.detail.map((item: { loc?: string[]; msg?: string }) => `${item.loc?.filter((part) => part !== 'body').join('.') || 'Campo'}: ${item.msg || 'Valor inválido'}`).join(' · ')
        : problem?.message || 'Não foi possível concluir a operação.';
    if ((response.status === 401 || problem?.code === 'EMAIL_VERIFICATION_REQUIRED') && !path.startsWith('auth/') && requestUser === activeUser && typeof window !== 'undefined') window.dispatchEvent(new Event('edutrack-session-expired'));
    throw new ApiError(message, response.status, problem?.code);
  }
  return result as T;
}

async function listAll<T>(path: string): Promise<T[]> {
  const items: T[] = [];
  for (let offset = 0; offset <= 100000; offset += 100) {
    const page = await api<{ items: T[]; total: number }>(path + '?limit=100&offset=' + offset);
    items.push(...page.items);
    if (items.length >= page.total) return items;
    if (!page.items.length) throw new Error('A lista mudou durante a consulta. Atualize os dados.');
  }
  throw new Error('Quantidade de registros acima do limite de carregamento.');
}
export async function loadAcademicData(): Promise<AcademicData> {
  const [courses, disciplines, tasks, sessions] = await Promise.all([
    listAll<ApiCourse>('courses'), listAll<ApiDiscipline>('disciplines'), listAll<ApiTask>('tasks'), listAll<ApiSession>('study-sessions'),
  ]);
  return { courses, disciplines, tasks, sessions };
}

const labels = { pendente: 'Pendente', em_andamento: 'Em andamento', concluida: 'Concluída', cancelada: 'Cancelada' };
const colors = ['violet', 'cyan', 'emerald', 'amber', 'rose'];
function progress(tasks: ApiTask[]) {
  const eligible = tasks.filter((item) => item.status !== 'cancelada');
  return eligible.length ? Math.round(eligible.filter((item) => item.status === 'concluida').length * 100 / eligible.length) : 0;
}
export function localDateInput(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}
export function academicView(data: AcademicData, user: ApiUser) {
  const disciplines: Discipline[] = data.disciplines.map((item, index) => ({
    id: item.id, title: item.nome, courseId: item.curso_id, teacher: item.professor || '',
    semester: item.carga_horaria === null ? '' : `${item.carga_horaria}h de carga horária`,
    goal: '', status: 'Em andamento', progress: progress(data.tasks.filter((task) => task.disciplina_id === item.id)), color: colors[index % colors.length],
  }));
  const courses: Course[] = data.courses.map((item, index) => {
    const ids = new Set(data.disciplines.filter((d) => d.curso_id === item.id).map((d) => d.id));
    return { id: item.id, title: item.nome, source: item.instituicao || '', type: 'Curso',
      period: [item.data_inicio, item.data_fim].filter(Boolean).join(' — '), goal: '', status: 'Em andamento',
      progress: progress(data.tasks.filter((task) => ids.has(task.disciplina_id))), color: colors[index % colors.length] };
  });
  const tasks: StudyTask[] = data.tasks.map((item) => {
    const discipline = data.disciplines.find((d) => d.id === item.disciplina_id);
    const due = item.data_prevista ? new Date(item.data_prevista) : null;
    return { id: item.id, title: item.titulo, courseId: discipline?.curso_id || '', disciplineId: item.disciplina_id,
      discipline: discipline?.nome || '', due: due ? localDateInput(due) : '',
      time: due ? `${String(due.getHours()).padStart(2, '0')}:${String(due.getMinutes()).padStart(2, '0')}` : '',
      priority: 'Média', status: labels[item.status], duration: item.minutos_estimados === null ? '' : `${item.minutos_estimados} min`, notes: item.descricao || '', category: 'Atividade' };
  });
  const profile: Profile = { name: user.nome, area: '', institution: '', preferences: '', weeklyGoal: '', focusTechnique: '', reminders: '' };
  const sessions = data.sessions.filter((item) => item.finalizado_em && item.duracao_minutos > 0)
    .map((item) => ({ id: item.id, taskId: item.tarefa_id, minutes: item.duracao_minutos, completedAt: item.finalizado_em }));
  return { courses, disciplines, tasks, profile, sessions };
}

export function taskPayload(task: ApiTask, status = task.status) {
  return { titulo: task.titulo, disciplina_id: task.disciplina_id, descricao: task.descricao,
    data_prevista: task.data_prevista, status, minutos_estimados: task.minutos_estimados };
}
