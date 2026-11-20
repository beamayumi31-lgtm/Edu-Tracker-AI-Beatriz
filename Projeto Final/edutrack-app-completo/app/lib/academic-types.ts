export type Course = {
  id: string; title: string; source: string; type: string; period: string;
  goal: string; status: string; progress: number; color: string;
};
export type Discipline = {
  id: string; title: string; courseId: string; teacher: string; semester: string;
  status: string; goal: string; progress: number; color: string;
};
export type StudyTask = {
  id: string; title: string; courseId: string; discipline: string; due: string;
  time: string; priority: string; status: string; duration: string; notes: string;
  disciplineId?: string; category?: string; materialUrl?: string;
};
export type Profile = {
  name: string; area: string; institution: string; preferences: string;
  weeklyGoal: string; focusTechnique: string; reminders: string;
};
export type EditKind = 'course' | 'discipline' | 'task' | 'profile';
export type ApiUser = { id: string; nome: string; email: string; role: 'student' | 'admin'; criado_em: string };
export type ApiCourse = { id: string; nome: string; instituicao: string | null; data_inicio: string | null; data_fim: string | null };
export type ApiDiscipline = { id: string; curso_id: string; nome: string; professor: string | null; carga_horaria: number | null };
export type ApiTask = {
  id: string; disciplina_id: string; titulo: string; descricao: string | null;
  data_prevista: string | null; status: 'pendente' | 'em_andamento' | 'concluida' | 'cancelada';
  minutos_estimados: number | null; concluido_em: string | null;
};
export type ApiSession = { id: string; tarefa_id: string; iniciado_em: string; finalizado_em: string; duracao_minutos: number };
export type AcademicData = { courses: ApiCourse[]; disciplines: ApiDiscipline[]; tasks: ApiTask[]; sessions: ApiSession[] };
export type StudyPlan = {
  origem: 'regras' | 'ia'; resumo: string; alertas: string[]; somente_proposta: boolean;
  tarefas_nao_planejadas: string[];
  blocos: { data: string; tarefa_id: string; disciplina_id: string; curso_id: string; titulo: string; minutos: number; orientacao: string }[];
};
