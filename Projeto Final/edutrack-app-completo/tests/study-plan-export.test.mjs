import test from 'node:test';
import assert from 'node:assert/strict';
import { studyPlanText } from '../app/lib/study-plan-export.ts';
const plan = { origem: 'regras', resumo: 'Estudar SQL', alertas: ['Revise os prazos'], somente_proposta: true, tarefas_nao_planejadas: ['private-task'], blocos: [{ data: '2026-11-16', tarefa_id: 'secret-task-id', disciplina_id: 'secret-discipline-id', curso_id: 'secret-course-id', titulo: 'Normalização', minutos: 25, orientacao: 'Revisar exemplos.' }] };
test('exporta proposta legível com datas brasileiras, alertas e limite', () => {
  const text = studyPlanText(plan);
  assert.match(text, /16\/11\/2026 \| 25 min \| Normalização/);
  assert.match(text, /planejador por regras/);
  assert.match(text, /Não modifica tarefas/);
  assert.match(text, /Revise os prazos/);
  assert.match(text, /1 tarefa\(s\)/);
  assert.doesNotMatch(text, /secret-|private-task/);
});
test('aceita plano vazio sem inventar blocos nem alertas', () => {
  const text = studyPlanText({ ...plan, blocos: [], alertas: [], tarefas_nao_planejadas: [], origem: 'ia' });
  assert.match(text, /Origem: IA/);
  assert.doesNotMatch(text, /ALERTAS|25 min|não couberam/);
});
