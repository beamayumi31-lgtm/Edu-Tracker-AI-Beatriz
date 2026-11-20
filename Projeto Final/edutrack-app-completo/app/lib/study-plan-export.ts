import type { StudyPlan } from './academic-types';

/** Plain text export: no identifiers or spreadsheet formulas are emitted. */
export function studyPlanText(plan: StudyPlan): string {
  const dateLabel = (value: string) => /^\d{4}-\d{2}-\d{2}$/.test(value) ? value.split('-').reverse().join('/') : value;
  return [
    'EDUTRACK | PLANO DE ESTUDOS',
    plan.origem === 'ia' ? 'Origem: IA' : 'Origem: planejador por regras',
    'Proposta para revisão. Não modifica tarefas, prazos nem agenda.',
    '', plan.resumo, '',
    ...plan.blocos.map((block) => `${dateLabel(block.data)} | ${block.minutos} min | ${block.titulo}\n${block.orientacao}`),
    ...(plan.alertas.length ? ['', 'ALERTAS', ...plan.alertas.map((alert) => `- ${alert}`)] : []),
    ...(plan.tarefas_nao_planejadas.length ? ['', `${plan.tarefas_nao_planejadas.length} tarefa(s) não couberam neste período.`] : []),
  ].join('\n');
}
