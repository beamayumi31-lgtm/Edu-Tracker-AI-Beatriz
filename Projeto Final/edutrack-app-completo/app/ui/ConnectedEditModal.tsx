'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Trash2, X } from 'lucide-react';
import { localDateInput } from '../lib/academic-api';
import type { AcademicData, ApiUser, EditKind } from '../lib/academic-types';

export type Editor = { kind: EditKind; id?: string; courseId?: string; disciplineId?: string };
const labels = { course: 'curso', discipline: 'disciplina', task: 'tarefa', profile: 'perfil' };

export default function ConnectedEditModal({ editor, data, user, onSave, onDelete, onClose }: {
  editor: Editor; data: AcademicData; user: ApiUser;
  onSave: (payload: Record<string, unknown>) => Promise<void>; onDelete: () => Promise<void>; onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [confirmDelete, setConfirmDelete] = useState(false);
  const course = data.courses.find((item) => item.id === editor.id);
  const discipline = data.disciplines.find((item) => item.id === editor.id);
  const task = data.tasks.find((item) => item.id === editor.id);
  const due = task?.data_prevista ? new Date(task.data_prevista) : null;
  const taskDiscipline = data.disciplines.find((item) => item.id === task?.disciplina_id);
  const [courseId, setCourseId] = useState(taskDiscipline?.curso_id || discipline?.curso_id || editor.courseId || data.courses[0]?.id || '');
  const [disciplineId, setDisciplineId] = useState(task?.disciplina_id || editor.disciplineId || data.disciplines.find((item) => item.curso_id === courseId)?.id || '');
  useEffect(() => { dialog.current?.showModal(); }, []);
  async function act(operation: () => Promise<void>) {
    if (busy) return;
    setBusy(true); setError('');
    try { await operation(); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Não foi possível salvar.'); }
    finally { setBusy(false); }
  }
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const str = (name: string) => String(form.get(name) || '').trim();
    const optional = (name: string) => str(name) || null;
    const number = (name: string) => str(name) === '' ? null : Number(str(name));
    let payload: Record<string, unknown>;
    if (editor.kind === 'course') payload = { nome: str('nome'), instituicao: optional('instituicao'), data_inicio: optional('data_inicio'), data_fim: optional('data_fim') };
    else if (editor.kind === 'discipline') payload = { nome: str('nome'), curso_id: courseId, professor: optional('professor'), carga_horaria: number('carga_horaria') };
    else if (editor.kind === 'task') {
      if (str('time') && !str('date')) { setError('Informe a data do prazo ou limpe o horário.'); return; }
      payload = { titulo: str('titulo'), disciplina_id: disciplineId, descricao: optional('descricao'), status: str('status'), minutos_estimados: number('minutos_estimados'),
        data_prevista: str('date') ? new Date(str('date') + 'T' + (str('time') || '23:59') + ':00').toISOString() : null };
    } else payload = { nome: str('nome') };
    void act(() => onSave(payload));
  }
  return <dialog ref={dialog} className="connected-dialog" aria-labelledby="editor-title" onCancel={(event) => { event.preventDefault(); if (!busy) onClose(); }}>
    <header><div><span className="eyebrow">Salvo na sua conta</span><h2 id="editor-title">{editor.id || editor.kind === 'profile' ? 'Editar' : 'Adicionar'} {labels[editor.kind]}</h2></div><button className="icon-button" aria-label="Fechar edição" disabled={busy} onClick={onClose}><X /></button></header>
    <form onSubmit={submit}>
      <fieldset disabled={busy} className="connected-fields">
        {editor.kind === 'course' && <>
          <label>Nome do curso<input name="nome" required maxLength={150} defaultValue={course?.nome} /></label>
          <label>Instituição ou plataforma<input name="instituicao" maxLength={200} defaultValue={course?.instituicao || ''} /></label>
          <div className="connected-grid"><label>Data de início<input name="data_inicio" type="date" defaultValue={course?.data_inicio || ''} /></label><label>Data de término<input name="data_fim" type="date" defaultValue={course?.data_fim || ''} /></label></div>
          <small>O progresso é calculado a partir das tarefas concluídas. Tipo e meta semanal aguardam suporte na API.</small>
        </>}
        {(editor.kind === 'discipline' || editor.kind === 'task') && <label>Curso<select required value={courseId} onChange={(event) => { setCourseId(event.target.value); setDisciplineId(data.disciplines.find((item) => item.curso_id === event.target.value)?.id || ''); }}><option value="">Selecione um curso</option>{data.courses.map((item) => <option key={item.id} value={item.id}>{item.nome}</option>)}</select></label>}
        {editor.kind === 'discipline' && <>
          <label>Nome da disciplina<input name="nome" required maxLength={150} defaultValue={discipline?.nome} /></label>
          <label>Professor(a)<input name="professor" maxLength={150} defaultValue={discipline?.professor || ''} /></label>
          <label>Carga horária (horas)<input name="carga_horaria" type="number" min={0} max={10000} step={1} defaultValue={discipline?.carga_horaria ?? ''} /></label>
        </>}
        {editor.kind === 'task' && <>
          <label>Disciplina<select required value={disciplineId} onChange={(event) => setDisciplineId(event.target.value)}><option value="">Selecione uma disciplina</option>{data.disciplines.filter((item) => item.curso_id === courseId).map((item) => <option key={item.id} value={item.id}>{item.nome}</option>)}</select></label>
          {!data.disciplines.some((item) => item.curso_id === courseId) && <p className="form-error">Cadastre uma disciplina neste curso antes de adicionar tarefas.</p>}
          <label>Título da tarefa<input name="titulo" required maxLength={200} defaultValue={task?.titulo} /></label>
          <label>Descrição<textarea name="descricao" maxLength={10000} rows={4} defaultValue={task?.descricao || ''} /></label>
          <div className="connected-grid"><label>Data de entrega<input name="date" type="date" defaultValue={due ? localDateInput(due) : ''} /></label><label>Horário local<input name="time" type="time" defaultValue={due ? String(due.getHours()).padStart(2, '0') + ':' + String(due.getMinutes()).padStart(2, '0') : ''} /></label></div>
          <div className="connected-grid"><label>Status<select name="status" defaultValue={task?.status || 'pendente'}><option value="pendente">Pendente</option><option value="em_andamento">Em andamento</option><option value="concluida">Concluída</option><option value="cancelada">Cancelada</option></select></label><label>Estimativa (minutos)<input name="minutos_estimados" type="number" min={0} max={100000} step={1} defaultValue={task?.minutos_estimados ?? ''} /></label></div>
        </>}
        {editor.kind === 'profile' && <><label>Nome completo<input name="nome" required maxLength={150} defaultValue={user.nome} /></label><p>{user.email}</p><small>Alteração de e-mail, senha e campos adicionais do perfil ainda não estão disponíveis.</small></>}
      </fieldset>
      {error && <p className="form-error" role="alert">{error}</p>}
      {confirmDelete && <section className="delete-warning"><strong>Excluir {labels[editor.kind]} definitivamente?</strong><p>Apenas este registro será excluído. Se houver vínculos ou histórico de estudo, a API bloqueará a exclusão para preservá-los.</p><div><button type="button" className="secondary-button" disabled={busy} onClick={() => setConfirmDelete(false)}>Manter registro</button><button type="button" className="danger-button" disabled={busy} onClick={() => void act(onDelete)}>Confirmar exclusão</button></div></section>}
      <footer>{editor.id && editor.kind !== 'profile' && <button className="danger-button" type="button" disabled={busy} onClick={() => setConfirmDelete(true)}><Trash2 size={16} /> Excluir {labels[editor.kind]}</button>}<button type="button" className="secondary-button" disabled={busy} onClick={onClose}>Cancelar</button><button className="primary-button" disabled={busy || (editor.kind === 'task' && !disciplineId)}>{busy ? 'Salvando…' : 'Salvar alterações'}</button></footer>
    </form>
  </dialog>;
}

