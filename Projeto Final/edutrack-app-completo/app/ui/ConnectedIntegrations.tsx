'use client';

import { useEffect, useRef, useState } from 'react';
import { useStudyRouter } from './useStudyRouter';
import Link from './StudyLink';
import { ArrowRight, BookOpen, Check, Download, Link2, LoaderCircle, RefreshCw, ShieldCheck, Unplug } from 'lucide-react';
import { api } from '../lib/academic-api';
import type { ApiCourse } from '../lib/academic-types';

type Status = { configured: boolean; connected: boolean; email: string | null; conexao_versao: string | null; completo_configurado: boolean; completo_autorizado: boolean };
type ClassroomCourse = { id: string; nome: string; secao: string };
type Activity = { id: string; titulo: string; descricao: string; data_prevista: string | null; ja_importada: boolean };
type Mode = 'completo' | 'todas_atividades' | 'selecionadas';
type ErrorScope = 'status' | 'connection' | 'courses' | 'preview' | 'import';
type Preview = { atividades: Activity[]; conexao_versao: string; conteudos: { tipo: string; anexos: unknown[] }[]; curso_importado_id: string | null; disciplina_importada_id: string | null; disciplina_excluida: boolean };
const message = (error: unknown) => error instanceof Error ? error.message : 'Não foi possível concluir. Tente novamente.';

export default function ConnectedIntegrations({ courses, onImported }: { courses: ApiCourse[]; onImported: () => Promise<unknown> }) {
  const router = useStudyRouter();
  const [status, setStatus] = useState<Status | null>(null);
  const [remote, setRemote] = useState<ClassroomCourse[]>([]);
  const [searched, setSearched] = useState(false);
  const [searchNote, setSearchNote] = useState('');
  const [target, setTarget] = useState(courses[0]?.id || '__new__');
  const [courseName, setCourseName] = useState('');
  const [mode, setMode] = useState<Mode>('completo');
  const [summary, setSummary] = useState({ materiais: 0, avisos: 0, anexos: 0 });
  const [removedDiscipline, setRemovedDiscipline] = useState(false);
  const [importedDiscipline, setImportedDiscipline] = useState('');
  const [linkedCourse, setLinkedCourse] = useState('');
  const [existingDiscipline, setExistingDiscipline] = useState('');
  const [selectedClass, setSelectedClass] = useState('');
  const [activities, setActivities] = useState<Activity[] | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [errorScope, setErrorScope] = useState<ErrorScope>('status');
  const [feedback, setFeedback] = useState('');
  const [confirmDisconnect, setConfirmDisconnect] = useState(false);
  // Impede dois cliques no intervalo anterior à atualização visual do React.
  const operationLock = useRef(false);
  const destinationRef = useRef<HTMLElement>(null);
  const targetCourseId = courses.find((course) => course.id === target)?.id || '';
  const newCourse = target === '__new__';
  const destinationValid = newCourse ? !!courseName.trim() : !!targetCourseId;
  const fullReady = !!status?.completo_configurado && !!status?.completo_autorizado;
  const selectedCourse = remote.find((course) => course.id === selectedClass);
  const importBlocker = busy || (!selectedClass ? 'Escolha uma turma abaixo para ver o conteúdo.'
    : mode === 'completo' && !fullReady ? 'Atualize a autorização Google para importar os conteúdos da turma.'
      : !activities ? 'A prévia precisa ser carregada antes de importar.'
        : removedDiscipline ? 'Esta disciplina foi excluída no EduTrack. A importação não recria registros apagados.'
          : !destinationValid ? 'Informe o nome do novo curso ou escolha um curso existente.' : '');

  useEffect(() => {
    let active = true;
    api<Status>('integrations/google/status').then((s) => { if (active) setStatus(s); }).catch((e) => { if (active) setError(message(e)); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (selectedClass) destinationRef.current?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
  }, [selectedClass]);

  async function act(label: string, scope: ErrorScope, action: () => Promise<void>) {
    if (operationLock.current) return;
    operationLock.current = true;
    setBusy(label); setErrorScope(scope); setError(''); setFeedback(''); setImportedDiscipline('');
    try { await action(); } catch (e) { setError(message(e)); } finally { operationLock.current = false; setBusy(''); }
  }
  function connect() {
    void act('Conectando…', 'connection', async () => {
      const result = await api<{ authorization_url: string }>('integrations/google/start', { method: 'POST', body: '{}' });
      const url = new URL(result.authorization_url);
      if (url.origin !== 'https://accounts.google.com' || url.pathname !== '/o/oauth2/v2/auth') throw new Error('Endereço de autorização inválido.');
      window.location.assign(url.href);
    });
  }
  function clearPreview() {
    setActivities(null); setSelected([]); setRemovedDiscipline(false);
    setLinkedCourse(''); setExistingDiscipline(''); setSummary({ materiais: 0, avisos: 0, anexos: 0 });
  }
  async function fetchPreview(id: string, nextMode: Mode, preserveSelection = false) {
    setErrorScope('preview');
    const result = await api<Preview>('integrations/google/preview', { method: 'POST', body: JSON.stringify({ turma_id: id, completo: nextMode === 'completo' }) });
    setActivities(result.atividades); setStatus((s) => s ? { ...s, conexao_versao: result.conexao_versao } : s);
    setSummary({ materiais: result.conteudos.filter((c) => c.tipo === 'material').length, avisos: result.conteudos.filter((c) => c.tipo === 'aviso').length, anexos: result.conteudos.reduce((sum, c) => sum + c.anexos.length, 0) });
    setRemovedDiscipline(result.disciplina_excluida);
    setLinkedCourse(result.curso_importado_id || ''); setExistingDiscipline(result.disciplina_importada_id || '');
    if (result.curso_importado_id) setTarget(result.curso_importado_id);
    if (preserveSelection) setSelected((items) => items.filter((id) => result.atividades.some((a) => a.id === id && !a.ja_importada)));
  }
  function loadClasses() {
    void act('Buscando turmas…', 'courses', async () => {
      const result = await api<{ turmas: ClassroomCourse[]; conexao_versao: string }>('integrations/google/courses');
      setRemote(result.turmas); setSearched(true); setSearchNote('');
      setStatus((s) => s ? { ...s, conexao_versao: result.conexao_versao } : s);
      if (selectedClass && result.turmas.some((course) => course.id === selectedClass)) {
        // Atualizar a busca mantém a turma, o curso de destino e as escolhas válidas.
        if (mode !== 'completo' || fullReady) {
          setActivities(null); setBusy('Atualizando a prévia da turma selecionada…');
          await fetchPreview(selectedClass, mode, true);
        }
      } else {
        if (selectedClass) setSearchNote('A turma anterior não está mais disponível nesta conta. Escolha outra turma.');
        setSelectedClass(''); clearPreview();
      }
    });
  }
  function preview(id: string, nextMode = mode) {
    if (operationLock.current) return;
    setMode(nextMode); setSelectedClass(id); clearPreview();
    setError(''); setFeedback(''); setImportedDiscipline('');
    if (!id || (nextMode === 'completo' && !fullReady)) return;
    void act('Carregando prévia…', 'preview', () => fetchPreview(id, nextMode));
  }
  function importItems() {
    if (importBlocker || operationLock.current) return;
    void act('Consultando o Classroom e importando. Aguarde a confirmação…', 'import', async () => {
      const result = await api<{ disciplinas_criadas: number; tarefas_criadas: number; itens_preservados: number; conteudos_criados: number; conteudos_atualizados: number; curso_id: string; disciplinas_ids: string[] }>('integrations/google/import', {
        method: 'POST', body: JSON.stringify({ ...(newCourse ? { novo_curso: { nome: courseName.trim() } } : { curso_id: targetCourseId }), conexao_versao: status?.conexao_versao, turmas: [{ turma_id: selectedClass, modo: mode, atividades: mode === 'selecionadas' ? selected : [] }] }),
      });
      setActivities((items) => items?.map((a) => mode !== 'selecionadas' || selected.includes(a.id) ? { ...a, ja_importada: true } : a) || null); setSelected([]);
      setTarget(result.curso_id); setLinkedCourse(result.curso_id); setImportedDiscipline(result.disciplinas_ids[0] || ''); setExistingDiscipline(result.disciplinas_ids[0] || '');
      setFeedback(`Importação concluída: ${result.disciplinas_criadas} disciplina(s), ${result.tarefas_criadas} tarefa(s) nova(s), ${result.conteudos_criados} conteúdo(s) adicionado(s) e ${result.conteudos_atualizados} atualizado(s). ${result.itens_preservados} registro(s) pessoal(is) preservado(s).`);
      try { await onImported(); } catch { setError('A importação foi concluída. Atualize a página para recarregar seus estudos.'); }
    });
  }
  function disconnect() {
    void act('Desconectando…', 'connection', async () => {
      const result = await api<{ mensagem: string }>('integrations/google/connection', { method: 'DELETE' });
      setStatus((s) => s ? { ...s, connected: false, email: null, conexao_versao: null } : s);
      setRemote([]); setSearched(false); setSearchNote(''); setSelectedClass(''); clearPreview(); setConfirmDisconnect(false); setFeedback(result.mensagem);
    });
  }
  const available = activities?.filter((a) => !a.ja_importada) || [];
  return <div className="integrations-page">
    <header className="page-heading"><div><span className="eyebrow">Seus estudos, conectados</span><h1>Integrações</h1><p>Traga suas atividades para perto do seu plano de estudos.</p></div></header>
    <section className="surface integration-hero">
      <div className="integration-symbol"><BookOpen size={30} /></div>
      <div><span className="eyebrow">Google Classroom</span><h2>Sua turma, organizada de uma vez.</h2><p>Importe atividades, materiais, avisos e links de anexos para estudar no mesmo lugar.</p>
        <span className="integration-badge"><ShieldCheck size={15} /> Acesso somente para leitura</span>
      </div>
      <div className="integration-account">
        {status?.connected ? <><span className="integration-badge"><Check size={15} /> Conta conectada</span><strong>{status.email}</strong><button className="secondary-button" disabled={!!busy} onClick={() => setConfirmDisconnect(true)}><Unplug size={16} /> Desconectar</button></> : <><button className="primary-button" disabled={!status?.configured || !!busy} onClick={connect}><Link2 size={18} /> Conectar Google Classroom</button><small>{status === null ? 'Verificando disponibilidade…' : status.configured ? 'Você escolhe a conta na próxima etapa.' : 'Aguardando configuração do administrador.'}</small></>}
      </div>
    </section>
    {!status?.configured && status && <section className="connection-notice"><div><strong>Integração preparada para ativação</strong><p>O administrador precisa cadastrar o aplicativo no Google Cloud, configurar as credenciais no servidor e ativar a integração. Nenhuma chave é solicitada aos alunos.</p></div></section>}
    {error && (!status?.connected || errorScope === 'connection' || errorScope === 'status') && <div className="form-error" role="alert">{error}{errorScope === 'connection' && <button className="secondary-button" disabled={!!busy} onClick={connect}>Reconectar conta</button>}{!status && <button className="secondary-button" onClick={() => void act('Verificando…', 'status', async () => setStatus(await api<Status>('integrations/google/status')))}>Tentar novamente</button>}</div>}
    {feedback && !status?.connected && <div className="connection-notice" role="status">{feedback}</div>}
    {confirmDisconnect && <section className="surface integration-confirm"><h2>Desconectar o Classroom?</h2><p>O EduTrack removerá a conexão e tentará revogar a permissão no Google. Suas disciplinas, tarefas e edições já importadas serão mantidas.</p><div className="integration-actions"><button className="secondary-button" disabled={!!busy} onClick={() => setConfirmDisconnect(false)}>Cancelar</button><button className="primary-button" disabled={!!busy} onClick={disconnect}>Confirmar desconexão</button></div></section>}
    <ol className="integration-steps"><li><b>1</b><div><strong>Conecte sua conta</strong><small>Autorize a leitura no Google.</small></div></li><li><b>2</b><div><strong>Escolha uma turma</strong><small>Confira o conteúdo e o curso de destino.</small></div></li><li><b>3</b><div><strong>Importe de uma vez</strong><small>Atividades e conteúdos já organizados.</small></div></li></ol>
    {status?.connected && <section className="surface integration-import">
      <header><div><span className="eyebrow">Passo 1 · Google Classroom</span><h2>Encontre sua turma</h2><p>Busque as turmas da conta conectada e clique na que deseja importar.</p></div><button type="button" className="primary-button" disabled={!!busy} onClick={loadClasses}><RefreshCw size={16} /> {searched ? 'Atualizar turmas' : 'Buscar turmas'}</button></header>
      {busy && <p role="status" className="connection-notice integration-loading"><LoaderCircle size={18} aria-hidden="true" />{busy}</p>}
      {error && errorScope === 'courses' && <div className="form-error integration-error" role="alert"><p>{error}</p><button type="button" className="secondary-button" disabled={!!busy} onClick={loadClasses}>Tentar buscar novamente</button></div>}
      {!searched && !busy && <div className="integration-empty"><BookOpen size={26} aria-hidden="true" /><div><strong>Suas turmas aparecerão aqui</strong><p>Clique em Buscar turmas. Você não precisa preencher um curso antes da busca.</p></div></div>}
      {searched && <section className="integration-results" aria-label="Turmas encontradas no Classroom">
        <p className="integration-search-summary" role="status">{remote.length ? `${remote.length} turma(s) encontrada(s). Clique em uma turma abaixo para ver a prévia.` : 'Nenhuma turma ativa encontrada nesta conta Google. Confira a conta conectada acima.'}</p>
        {searchNote && <p className="connection-notice">{searchNote}</p>}
        <div className="classroom-course-grid">{remote.map((course) => <button type="button" key={course.id} className="classroom-course-choice" disabled={!!busy} aria-pressed={selectedClass === course.id} onClick={() => preview(course.id)}>
          <span className="classroom-course-icon"><BookOpen size={20} aria-hidden="true" /></span><span><strong>{course.nome}</strong>{course.secao && <small>{course.secao}</small>}<span className="classroom-course-action">{selectedClass === course.id ? 'Turma selecionada' : 'Ver prévia'} {selectedClass === course.id ? <Check size={15} /> : <ArrowRight size={15} />}</span></span>
        </button>)}</div>
      </section>}
      {selectedClass && <section ref={destinationRef} className="integration-destination" aria-label="Destino da turma selecionada"><span className="eyebrow">Passo 2 · EduTrack</span><h3>{selectedCourse?.nome || 'Turma selecionada'}</h3><p>Esta turma será uma disciplina dentro do curso escolhido abaixo.</p>
      <fieldset className="connected-fields" disabled={!!busy}><div className="connected-grid">
        <label>O que importar<select value={mode} onChange={(e) => preview(selectedClass, e.target.value as Mode)}><option value="completo">Turma completa: atividades, materiais e avisos</option><option value="todas_atividades">Somente todas as atividades</option><option value="selecionadas">Escolher atividades manualmente</option></select></label>
        <label>Curso de destino<select value={target} disabled={!!linkedCourse} onChange={(e) => setTarget(e.target.value)}><option value="__new__">Criar um curso nesta importação</option>{courses.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}</select></label>
        {newCourse && <label>Nome do novo curso<input value={courseName} maxLength={150} onChange={(e) => setCourseName(e.target.value)} placeholder="Ex.: Ciência da Computação" /></label>}
      </div></fieldset>
      {linkedCourse && <p className="integration-linked">Esta turma já está vinculada ao curso {courses.find((course) => course.id === linkedCourse)?.nome || 'original'}. Reimportar preserva suas edições e evita duplicações.{existingDiscipline && <button type="button" className="text-button" disabled={!!busy} onClick={() => router.push('/disciplinas/' + existingDiscipline)}>Abrir disciplina existente <ArrowRight size={14} /></button>}</p>}
      {mode === 'completo' && !fullReady && <div className="connection-notice"><div><strong>{status.completo_configurado ? 'Autorize também os conteúdos da turma' : 'Importação completa em preparação'}</strong><p>{status.completo_configurado ? 'Sua conexão atual lê atividades. Atualize a autorização para incluir materiais, avisos e tópicos. Seus estudos serão preservados.' : 'O administrador precisa ativar a importação completa. Você já pode consultar e importar todas as atividades usando a opção acima.'}</p>{status.completo_configurado && <button className="secondary-button" disabled={!!busy} onClick={connect}>Atualizar autorização Google</button>}</div></div>}
      <div className="integration-import-action"><div><strong>Passo 3 · Confirme a importação</strong><p id="classroom-import-help">{importBlocker || (mode === 'selecionadas' ? `${selected.length} atividade(s) nova(s) selecionada(s). As já importadas serão preservadas.` : 'Tudo pronto. Os conteúdos disponíveis serão consultados novamente ao importar.')}</p></div><button type="button" className="primary-button" aria-describedby="classroom-import-help" disabled={!!importBlocker} onClick={importItems}><Download size={17} />{mode === 'completo' ? 'Importar turma completa' : mode === 'todas_atividades' ? 'Importar todas as atividades' : selected.length ? `Importar disciplina e ${selected.length} atividade(s)` : 'Importar apenas a disciplina'}</button></div>
      {error && ['preview', 'import'].includes(errorScope) && <div className="form-error integration-error" role="alert"><p>{error}</p>{errorScope === 'preview' && <button type="button" className="secondary-button" disabled={!!busy} onClick={() => preview(selectedClass)}>Tentar carregar a prévia</button>}</div>}
      {feedback && <div className="connection-notice integration-success" role="status"><p>{feedback}</p>{importedDiscipline && <button type="button" className="primary-button" disabled={!!busy} onClick={() => router.push('/disciplinas/' + importedDiscipline)}>Abrir disciplina importada <ArrowRight size={16} /></button>}</div>}
        {activities && <div className="integration-preview"><div className="integration-preview-heading"><strong>{activities.length} atividade(s) publicada(s)</strong>{mode === 'selecionadas' && <button className="secondary-button" disabled={!!busy || !available.length} onClick={() => setSelected(selected.length === available.length ? [] : available.map((a) => a.id))}>{selected.length === available.length && available.length ? 'Desmarcar todas' : 'Selecionar novas'}</button>}</div>
          {mode === 'completo' && <div className="integration-content-summary"><span><b>{summary.materiais}</b> materiais</span><span><b>{summary.avisos}</b> avisos</span><span><b>{summary.anexos}</b> links de anexos</span></div>}
          {mode !== 'selecionadas' && <p>Todas as atividades disponíveis serão consultadas novamente ao importar. Você não precisa marcar uma por uma.</p>}
          {activities.length ? <ul>{activities.map((a) => <li key={a.id}><label>{mode === 'selecionadas' ? <input type="checkbox" disabled={!!busy || a.ja_importada} checked={a.ja_importada || selected.includes(a.id)} onChange={(e) => setSelected((items) => e.target.checked ? [...items, a.id] : items.filter((id) => id !== a.id))} /> : <Check size={18} aria-label="Incluída automaticamente" />}<span><strong>{a.titulo}</strong><small>{a.ja_importada ? 'Já importada · edição local preservada' : a.data_prevista ? 'Prazo: ' + new Date(a.data_prevista).toLocaleString('pt-BR') : 'Sem prazo definido'}</small></span></label>{a.descricao && <details><summary>Ver descrição</summary><p className="preserve-lines">{a.descricao}</p></details>}</li>)}</ul> : <p>Esta turma não tem atividades publicadas. Os demais conteúdos disponíveis continuam incluídos no modo completo.</p>}
          {removedDiscipline && <p role="alert" className="form-error">Esta disciplina foi excluída no EduTrack. A importação não recria registros apagados automaticamente.</p>}
          <footer><div><p>Atividades aparecem em Tarefas; materiais, avisos e anexos ficam em Conteúdo da turma. Arquivos abrem no serviço original.</p><p>Esta importação é pontual. Para buscar novas publicações, importe novamente. Suas edições e conclusões de tarefas são preservadas, sem duplicar registros.</p></div></footer>
        </div>}
      </section>}
    </section>}
    <aside className="surface integration-privacy"><ShieldCheck size={24} /><div><h2>Você mantém o controle</h2><p>Importamos apenas publicações acessíveis à sua conta: atividades, descrições, prazos, materiais, avisos, tópicos e links de anexos. Notas, entregas, comentários, lista de alunos e arquivos privados fora dessas publicações não são consultados. O Google inclui notas na permissão de atividades, mas não as utilizamos. Não alteramos o Classroom nem baixamos seus arquivos. Esses dados não são enviados automaticamente à IA generativa.</p><p>Algumas instituições exigem liberação do administrador Google. Você também pode revogar o acesso nas <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer">permissões da sua conta Google</a>. <Link href="/privacidade">Entenda como usamos seus dados.</Link></p></div></aside>
  </div>;
}
