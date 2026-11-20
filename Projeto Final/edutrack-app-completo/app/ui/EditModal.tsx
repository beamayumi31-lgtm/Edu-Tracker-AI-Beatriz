'use client';

import { Trash2, X } from 'lucide-react';
import { type FormEvent, useMemo, useRef, useState } from 'react';
import type { Course, Discipline, StudyTask, Profile, EditKind } from './EduTrackApp';

export default function EditModal({ kind, item, courses, disciplines, initialCourseId, initialDisciplineId, onClose, onSave, onDelete, deleteImpact }: {
  kind: EditKind; item?: Course | Discipline | StudyTask | Profile; courses: Course[]; disciplines: Discipline[];
  initialCourseId?: string; initialDisciplineId?: string; onClose: () => void; onSave: (data: Record<string, string>) => void;
  onDelete?: () => void; deleteImpact?: { disciplines: number; tasks: number };
}) {
  const initial = useMemo<Record<string, string>>(() => {
    if (kind === 'course') {
      const value = item as Course | undefined;
      return { title: value?.title || '', source: value?.source || '', type: value?.type || 'Universidade', period: value?.period || '', goal: value?.goal || '', status: value?.status || 'Em andamento', progress: String(value?.progress || 0) } as Record<string, string>;
    }
    if (kind === 'discipline') {
      const value = item as Discipline | undefined;
      return { title: value?.title || '', courseId: value?.courseId || courses[0]?.id || '', teacher: value?.teacher || '', semester: value?.semester || '', goal: value?.goal || '', status: value?.status || 'Em andamento', progress: String(value?.progress || 0) } as Record<string, string>;
    }
    if (kind === 'task') {
      const value = item as StudyTask | undefined;
      const matchedDiscipline = disciplines.find((discipline) => discipline.id === value?.disciplineId || (discipline.title === value?.discipline && discipline.courseId === value?.courseId));
      return { title: value?.title || '', courseId: value?.courseId || initialCourseId || courses[0]?.id || '', disciplineId: matchedDiscipline?.id || initialDisciplineId || '', discipline: value?.discipline || '', category: value?.category || 'Atividade', due: value?.due || '', time: value?.time || '', priority: value?.priority || 'Média', status: value?.status || 'Pendente', duration: value?.duration || '', materialUrl: value?.materialUrl || '', notes: value?.notes || '' } as Record<string, string>;
    }
    const value = item as Profile | undefined;
    return { name: value?.name || '', area: value?.area || '', institution: value?.institution || '', preferences: value?.preferences || '', weeklyGoal: value?.weeklyGoal || '', focusTechnique: value?.focusTechnique || '', reminders: value?.reminders || '' } as Record<string, string>;
  }, [courses, disciplines, initialCourseId, initialDisciplineId, item, kind]);
  const [form, setForm] = useState<Record<string, string>>(initial);
  const deleteDialogRef = useRef<HTMLDialogElement>(null);
  const canDelete = kind === 'course' && Boolean(item) && Boolean(onDelete);
  const availableDisciplines = disciplines.filter((discipline) => discipline.courseId === form.courseId);
  const labels = { course: 'curso', discipline: 'disciplina', task: 'tarefa', profile: 'perfil' };
  function update(field: string, value: string) { setForm((current) => ({ ...current, [field]: value })); }
  function updateTaskCourse(value: string) { setForm((current) => ({ ...current, courseId: value, disciplineId: '' })); }
  function submit(event: FormEvent) { event.preventDefault(); onSave(form); }
  function confirmDeletion() {
    deleteDialogRef.current?.showModal();
    deleteDialogRef.current?.querySelector<HTMLButtonElement>('[data-cancel-delete]')?.focus();
  }

  return <div className="modal-backdrop" onMouseDown={onClose}><section className="edit-modal" onMouseDown={(event) => event.stopPropagation()}><header><div><span className="eyebrow">Personalizar informações</span><h2>{item ? 'Editar' : 'Adicionar'} {labels[kind]}</h2></div><button className="icon-button" onClick={onClose} aria-label="Fechar"><X /></button></header><form onSubmit={submit}>
    {kind === 'course' && <><label>Nome do curso<input required value={form.title} placeholder="Ex.: Engenharia de Software" onChange={(event) => update('title', event.target.value)} /></label><div className="form-grid"><label>Tipo<select value={form.type} onChange={(event) => update('type', event.target.value)}><option>Universidade</option><option>Plataforma online</option><option>Curso livre</option><option>Independente</option></select></label><label>Instituição ou plataforma<input required value={form.source} placeholder="Informe a origem" onChange={(event) => update('source', event.target.value)} /></label></div><div className="form-grid"><label>Período<input value={form.period} placeholder="Ex.: 2º semestre" onChange={(event) => update('period', event.target.value)} /></label><label>Meta semanal<input value={form.goal} placeholder="Ex.: 5 horas" onChange={(event) => update('goal', event.target.value)} /></label></div><div className="form-grid"><label>Status<select value={form.status} onChange={(event) => update('status', event.target.value)}><option>Em andamento</option><option>Pausado</option><option>Concluído</option></select></label><label>Progresso (%)<input type="number" min="0" max="100" value={form.progress} onChange={(event) => update('progress', event.target.value)} /></label></div></>}
    {kind === 'discipline' && <><label>Nome da disciplina<input required value={form.title} placeholder="Ex.: Banco de Dados" onChange={(event) => update('title', event.target.value)} /></label><label>Curso vinculado<select required value={form.courseId} onChange={(event) => update('courseId', event.target.value)}>{courses.map((course) => <option value={course.id} key={course.id}>{course.title}</option>)}</select></label><div className="form-grid"><label>Professor (opcional)<input value={form.teacher} placeholder="Opcional" onChange={(event) => update('teacher', event.target.value)} /></label><label>Período ou semestre<input value={form.semester} placeholder="Ex.: 3º semestre" onChange={(event) => update('semester', event.target.value)} /></label></div><div className="form-grid"><label>Meta semanal<input value={form.goal} placeholder="Ex.: 3 horas" onChange={(event) => update('goal', event.target.value)} /></label><label>Progresso (%)<input type="number" min="0" max="100" value={form.progress} onChange={(event) => update('progress', event.target.value)} /></label></div><label>Status<select value={form.status} onChange={(event) => update('status', event.target.value)}><option>Em andamento</option><option>Pausado</option><option>Concluído</option></select></label></>}
    {kind === 'task' && <><label>Título da atividade<input required value={form.title} placeholder="O que precisa ser entregue ou estudado?" onChange={(event) => update('title', event.target.value)} /></label><div className="form-grid"><label>Curso<select required value={form.courseId} onChange={(event) => updateTaskCourse(event.target.value)}>{courses.map((course) => <option value={course.id} key={course.id}>{course.title}</option>)}</select></label><label>Disciplina<select value={form.disciplineId} onChange={(event) => update('disciplineId', event.target.value)}><option value="">Sem disciplina específica</option>{availableDisciplines.map((discipline) => <option value={discipline.id} key={discipline.id}>{discipline.title}</option>)}</select></label></div><div className="form-grid"><label>Tipo de atividade<select value={form.category} onChange={(event) => update('category', event.target.value)}><option>Atividade</option><option>Trabalho</option><option>Prova</option><option>Projeto</option><option>Leitura</option><option>Revisão</option></select></label><label>Prioridade<select value={form.priority} onChange={(event) => update('priority', event.target.value)}><option>Alta</option><option>Média</option><option>Baixa</option></select></label></div><div className="form-grid"><label>Data de entrega<input type="date" value={form.due} onChange={(event) => update('due', event.target.value)} /></label><label>Horário<input type="time" value={form.time} onChange={(event) => update('time', event.target.value)} /></label></div><div className="form-grid"><label>Status<select value={form.status} onChange={(event) => update('status', event.target.value)}><option>Pendente</option><option>Em andamento</option><option>Concluída</option></select></label><label>Duração estimada<input value={form.duration} placeholder="Ex.: 45 minutos" onChange={(event) => update('duration', event.target.value)} /></label></div><label>Link do material (opcional)<input type="url" value={form.materialUrl} placeholder="https://..." onChange={(event) => update('materialUrl', event.target.value)} /></label><label>Instruções e anotações<textarea value={form.notes} placeholder="Descreva o que deve ser feito e os pontos importantes." onChange={(event) => update('notes', event.target.value)} /></label></>}
    {kind === 'profile' && <><label>Nome<input value={form.name} placeholder="Seu nome" onChange={(event) => update('name', event.target.value)} /></label><div className="form-grid"><label>Área de estudo<input value={form.area} placeholder="Sua área de estudo" onChange={(event) => update('area', event.target.value)} /></label><label>Instituição<input value={form.institution} placeholder="Sua instituição" onChange={(event) => update('institution', event.target.value)} /></label></div><div className="form-grid"><label>Meta semanal<input value={form.weeklyGoal} placeholder="Ex.: 8 horas" onChange={(event) => update('weeklyGoal', event.target.value)} /></label><label>Técnica de foco<input value={form.focusTechnique} placeholder="Ex.: Pomodoro" onChange={(event) => update('focusTechnique', event.target.value)} /></label></div><label>Lembretes<select value={form.reminders} onChange={(event) => update('reminders', event.target.value)}><option value="">Não definido</option><option>Ativados</option><option>Desativados</option></select></label><label>Preferências de estudo<textarea value={form.preferences} placeholder="Ex.: revisão semanal, intervalos curtos" onChange={(event) => update('preferences', event.target.value)} /></label></>}
    <footer className={canDelete ? 'course-edit-actions' : undefined}>
      {canDelete && <button type="button" className="course-delete-button" onClick={confirmDeletion}><Trash2 size={17} /> Excluir curso</button>}
      <button type="button" className="secondary-button" onClick={onClose}>Cancelar</button>
      <button type="submit" className="primary-button">Salvar alterações</button>
    </footer>
  </form>
    {canDelete && <dialog ref={deleteDialogRef} className="course-delete-dialog" aria-labelledby="course-delete-title" aria-describedby="course-delete-description">
      <form method="dialog">
        <span className="course-delete-icon"><Trash2 size={24} /></span>
        <h2 id="course-delete-title">Excluir este curso?</h2>
        <p id="course-delete-description">O curso <strong>{(item as Course).title}</strong> será excluído. Esta ação não pode ser desfeita.</p>
        {Boolean(deleteImpact && (deleteImpact.disciplines || deleteImpact.tasks)) && <div className="course-delete-impact">
          <strong>Também serão excluídos:</strong>
          <ul>
            {Boolean(deleteImpact?.disciplines) && <li>{deleteImpact?.disciplines} {deleteImpact?.disciplines === 1 ? 'disciplina vinculada' : 'disciplinas vinculadas'}</li>}
            {Boolean(deleteImpact?.tasks) && <li>{deleteImpact?.tasks} {deleteImpact?.tasks === 1 ? 'tarefa vinculada' : 'tarefas vinculadas'}</li>}
          </ul>
        </div>}
        <p>Seu histórico de tempo estudado será mantido.</p>
        <div className="course-delete-confirm-actions">
          <button type="submit" className="secondary-button" data-cancel-delete>Manter curso</button>
          <button type="button" className="course-delete-button solid" onClick={() => { deleteDialogRef.current?.close(); onDelete?.(); }}><Trash2 size={17} /> Sim, excluir curso</button>
        </div>
      </form>
    </dialog>}
  </section></div>;
}
