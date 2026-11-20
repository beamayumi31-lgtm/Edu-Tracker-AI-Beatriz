'use client';
import PasswordRecovery from './PasswordRecovery';

import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { ArrowRight, Clock3 } from 'lucide-react';
import { api, academicView, loadAcademicData, taskPayload, setApiUser } from '../lib/academic-api';
import type { AcademicData, ApiUser, ApiCourse, ApiDiscipline, ApiTask } from '../lib/academic-types';
import { completedFocusSession, restoreFocusRun, type FocusRun } from '../lib/study-game';
import { useStudyRouter } from './useStudyRouter';
import { useFocusClock } from './useFocusClock';
import ConnectedAuth from './ConnectedAuth';
import * as Views from './EduTrackViews';
import type { Editor } from './ConnectedEditModal';

export type { Course, Discipline, StudyTask, Profile, EditKind } from '../lib/academic-types';
const TutorialModal = lazy(() => import('./TutorialModal'));
const EditorModal = lazy(() => import('./ConnectedEditModal'));
const FocusGarden = lazy(() => import('./FocusGarden'));
const StudyStreak = lazy(() => import('./StudyStreak'));
const EduAI = lazy(() => import('./ConnectedEduAI'));
const Integrations = lazy(() => import('./ConnectedIntegrations'));
const AdminPage = lazy(() => import('./ConnectedAdmin'));
const emptyData: AcademicData = { courses: [], disciplines: [], tasks: [], sessions: [] };
const errorText = (cause: unknown) => cause instanceof Error ? cause.message : 'Não foi possível concluir a operação.';
const resources = { course: 'courses', discipline: 'disciplines', task: 'tasks', profile: 'me' } as const;

function Loading() { return <p className="connection-loading" role="status">Conectando ao seu espaço de estudos…</p>; }

function ConnectedApp({ user, onUser, logout }: { user: ApiUser; onUser: (user: ApiUser) => void; logout: () => Promise<void> }) {
  const pathname = usePathname();
  const router = useStudyRouter();
  const [data, setData] = useState<AcademicData>(emptyData);
  const [loaded, setLoaded] = useState(false);
  const [loadError, setLoadError] = useState('');
  const [toast, setToast] = useState('');
  const [editor, setEditor] = useState<Editor | null>(null);
  const [mobile, setMobile] = useState(false);
  const [sidebarHidden, setSidebarHidden] = useState(false);
  const [tutorial, setTutorial] = useState(false);
  const [focusRun, setFocusRun] = useState<FocusRun | null>(null);
  const [focusReady, setFocusReady] = useState(false);
  const [pendingFocus, setPendingFocus] = useState<FocusRun | null>(null);
  const [savingFocus, setSavingFocus] = useState(false);
  const mutationLock = useRef(false);
  const focusLock = useRef(false);
  const focusKey = 'edutrack-api-focus-v1:' + user.id;
  const view = useMemo(() => academicView(data, user), [data, user]);
  const { courses, disciplines, tasks, profile, sessions } = view;
  const navigate = (path: string) => router.push(path);

  const refresh = useCallback(() => loadAcademicData()
    .then((result) => { setData(result); setLoaded(true); setLoadError(''); })
    .catch((cause) => { setLoadError(errorText(cause)); }), []);
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    try {
      // Hidratação única de uma fonte externa após SSR; o estado inicial do servidor não lê storage.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSidebarHidden(localStorage.getItem('edutrack-sidebar-hidden') === 'true');
      const saved = JSON.parse(localStorage.getItem(focusKey) || '{}');
      setFocusRun(restoreFocusRun(saved.run));
      setPendingFocus(restoreFocusRun(saved.pending));
    } catch { /* Preferências inválidas não substituem os registros do servidor. */ }
    setFocusReady(true);
  }, [focusKey]);
  useEffect(() => {
    if (!focusReady) return;
    try { localStorage.setItem(focusKey, JSON.stringify({ run: focusRun, pending: pendingFocus })); }
    // A falha real da persistência externa precisa ser comunicada ao aluno.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    catch { setToast('O rascunho do cronômetro não pôde ser salvo. Não feche esta aba durante a sessão.'); }
  }, [focusRun, pendingFocus, focusReady, focusKey]);
  useEffect(() => { if (!toast) return; const timer = setTimeout(() => setToast(''), 9000); return () => clearTimeout(timer); }, [toast]);

  // Atualiza a tela com o registro confirmado, sem converter falha de recarga em falso erro de gravação.
  async function save(payload: Record<string, unknown>) {
    if (!editor) return;
    if (editor.kind === 'profile') {
      onUser(await api<ApiUser>('me', { method: 'PUT', body: JSON.stringify(payload) }));
    } else {
      const key = resources[editor.kind];
      const result = await api<ApiCourse | ApiDiscipline | ApiTask>(key + (editor.id ? '/' + editor.id : ''), { method: editor.id ? 'PUT' : 'POST', body: JSON.stringify(payload) });
      setData((current) => ({ ...current, [key]: editor.id ? current[key].map((item) => item.id === result.id ? result : item) : [...current[key], result] }));
    }
    setEditor(null); setToast('Alterações salvas no SQL Server.');
  }
  async function remove() {
    if (!editor?.id || editor.kind === 'profile') return;
    const key = resources[editor.kind];
    await api(key + '/' + editor.id, { method: 'DELETE' });
    setData((current) => ({ ...current, [key]: current[key].filter((item) => item.id !== editor.id) }));
    setEditor(null); setToast('Registro excluído. Esta ação não pode ser desfeita pelo site.');
    navigate(key === 'courses' ? '/cursos' : key === 'disciplines' ? '/disciplinas' : '/tarefas');
  }
  async function toggleTask(id: string) {
    const task = data.tasks.find((item) => item.id === id);
    if (!task || mutationLock.current) return;
    mutationLock.current = true;
    try {
      const updated = await api<ApiTask>('tasks/' + id, { method: 'PUT', body: JSON.stringify(taskPayload(task, task.status === 'concluida' ? 'pendente' : 'concluida')) });
      setData((current) => ({ ...current, tasks: current.tasks.map((item) => item.id === id ? updated : item) }));
    } catch (cause) { setToast(errorText(cause)); } finally { mutationLock.current = false; }
  }
  async function addSuggestedCourse(suggestion: Views.SuggestedCourse) {
    if (mutationLock.current) return;
    if (courses.some((item) => item.title === suggestion.title && item.source === suggestion.source)) { setToast('Este curso já está no seu painel.'); return; }
    mutationLock.current = true;
    try {
      const result = await api<ApiCourse>('courses', { method: 'POST', body: JSON.stringify({ nome: suggestion.title, instituicao: suggestion.source }) });
      setData((current) => ({ ...current, courses: [...current.courses, result] }));
      setToast('Curso salvo. Conteúdo e matrícula na plataforma não são incluídos.');
    } catch (cause) { setToast(errorText(cause)); } finally { mutationLock.current = false; }
  }
  const persistFocus = useCallback(async (run: FocusRun) => {
    if (focusLock.current || !run.taskId || !run.endsAt) return;
    focusLock.current = true; setSavingFocus(true);
    try {
      const entry = await api<AcademicData['sessions'][number]>('study-sessions', {
        method: 'POST', headers: { 'Idempotency-Key': run.id.replace(/^focus-/, '') },
        body: JSON.stringify({ tarefa_id: run.taskId, iniciado_em: new Date(run.endsAt - run.minutes * 60000).toISOString(), finalizado_em: new Date(run.endsAt).toISOString() }),
      });
      setData((current) => ({ ...current, sessions: current.sessions.some((item) => item.id === entry.id) ? current.sessions : [...current.sessions, entry] }));
      setPendingFocus(null);
      setToast('Árvore conquistada! Sessão salva no SQL Server.');
    } catch (cause) { setToast('Sessão ainda não salva. ' + errorText(cause)); }
    finally { focusLock.current = false; setSavingFocus(false); }
  }, []);
  const finishFocus = useCallback((run: FocusRun) => {
    setFocusRun(null);
    if (completedFocusSession(run) && run.taskId) {
      // Guardar o pedido antes de enviá-lo permite repetir a mesma gravação sem duplicar.
      try { localStorage.setItem(focusKey, JSON.stringify({ run: null, pending: run })); } catch { /* A tentativa permanece visível na sessão atual. */ }
      setPendingFocus(run); void persistFocus(run);
    } else setToast('Pausa concluída. Pronto para um novo foco?');
  }, [focusKey, persistFocus]);
  const seconds = useFocusClock(focusRun, focusReady && loaded && !pendingFocus, finishFocus);
  function toggleSidebar() {
    setSidebarHidden((current) => { try { localStorage.setItem('edutrack-sidebar-hidden', String(!current)); } catch { /* Preferência opcional. */ } return !current; });
  }

  let content: ReactNode;
  if (!loaded) content = <><Loading />{loadError && <section className="connection-notice" role="alert">{loadError}<button className="secondary-button" onClick={() => void refresh()}>Tentar novamente</button></section>}</>;
  else if (pathname === '/cursos') content = <Views.CoursesPage courses={courses} edit={(id) => setEditor({ kind: 'course', id })} add={() => setEditor({ kind: 'course' })} navigate={navigate} />;
  else if (pathname.startsWith('/cursos/')) {
    const course = courses.find((item) => pathname === '/cursos/' + item.id);
    content = course ? <Views.CourseDetails course={course} disciplines={disciplines.filter((item) => item.courseId === course.id)} edit={() => setEditor({ kind: 'course', id: course.id })} goBack={() => navigate('/cursos')} /> : <p>Curso não encontrado nesta conta.</p>;
  } else if (pathname === '/disciplinas') content = <Views.DisciplinesPage disciplines={disciplines} courses={courses} tasks={tasks} edit={(id) => setEditor({ kind: 'discipline', id })} add={() => setEditor({ kind: 'discipline' })} goToCourses={() => navigate('/cursos')} navigate={navigate} />;
  else if (pathname.startsWith('/disciplinas/')) {
    const discipline = disciplines.find((item) => pathname === '/disciplinas/' + item.id);
    content = discipline ? <Views.DisciplineDetails discipline={discipline} course={courses.find((item) => item.id === discipline.courseId)} tasks={tasks} edit={() => setEditor({ kind: 'discipline', id: discipline.id })} addTask={() => setEditor({ kind: 'task', courseId: discipline.courseId, disciplineId: discipline.id })} editTask={(id) => setEditor({ kind: 'task', id })} toggle={(id) => void toggleTask(id)} goBack={() => navigate('/disciplinas')} /> : <p>Disciplina não encontrada nesta conta.</p>;
  } else if (pathname === '/tarefas') content = <Views.TasksPage tasks={tasks} disciplines={disciplines} courses={courses} edit={(id) => setEditor({ kind: 'task', id })} add={() => setEditor({ kind: 'task' })} toggle={(id) => void toggleTask(id)} goToCourses={() => navigate('/cursos')} />;
  else if (pathname === '/cronometro') content = <FocusGarden tasks={tasks} sessions={sessions} run={focusRun} seconds={seconds} setRun={setFocusRun} navigate={navigate} ready={focusReady && !pendingFocus} requireTask />;
  else if (pathname === '/ofensiva') content = <StudyStreak sessions={sessions} navigate={navigate} />;
  else if (pathname === '/relatorios') content = <Views.ReportsPage disciplines={disciplines} sessions={sessions} />;
  else if (pathname === '/edu-ia') content = <EduAI />;
  else if (pathname === '/integracoes') content = <Integrations courses={data.courses} onImported={refresh} />;
  else if (pathname === '/descobrir') content = <Views.DiscoverPage courses={courses} addCourse={(suggestion) => void addSuggestedCourse(suggestion)} />;
  else if (pathname === '/perfil') content = <Views.ProfilePage profile={profile} courses={courses} sessions={sessions} edit={() => setEditor({ kind: 'profile' })} />;
  else if (pathname === '/gerenciamento') content = <AdminPage key={user.role} role={user.role} navigate={navigate} />;
  else if (pathname === '/upgrade') content = <section className="surface connected-plan"><h1>EduTrack Pro</h1><p>Recurso futuro. Não há contratação, cobrança ou alteração de plano nesta versão.</p></section>;
  else content = <Views.Dashboard tasks={tasks} courses={courses} sessions={sessions} profile={profile} navigate={navigate} />;
  return <main className={'app-shell ' + (sidebarHidden ? 'sidebar-hidden' : '')}>
    <Views.AppSidebar pathname={pathname} profile={profile} plan="Gratuito" role={user.role} onLogout={() => void logout().catch((cause) => setToast(errorText(cause)))} />
    <section className="app-content"><Views.Topbar profile={profile} openMenu={() => setMobile(true)} sidebarHidden={sidebarHidden} toggleSidebar={toggleSidebar} openTutorial={() => setTutorial(true)} />
      {focusRun && pathname !== '/cronometro' && <button className="focus-running-bar" onClick={() => navigate('/cronometro')}><Clock3 size={17} /><span>Sessão {focusRun.endsAt ? 'em andamento' : 'pausada'} · {Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, '0')}</span><strong>Voltar ao foco <ArrowRight size={16} /></strong></button>}
      {pendingFocus && <div className="connection-notice" role="status">Sua sessão terminou e aguarda confirmação no servidor. Ela só contará nas conquistas após ser salva.<button className="secondary-button" disabled={savingFocus} onClick={() => void persistFocus(pendingFocus)}>{savingFocus ? 'Salvando sessão…' : 'Tentar salvar sessão'}</button></div>}
      <div className="content-wrap"><Suspense fallback={<Loading />}>{content}</Suspense></div>
    </section>
    {mobile && <div className="mobile-popover" onMouseDown={() => setMobile(false)}><div onMouseDown={(event) => event.stopPropagation()}><Views.AppSidebar pathname={pathname} profile={profile} plan="Gratuito" role={user.role} close={() => setMobile(false)} onLogout={() => void logout().catch((cause) => setToast(errorText(cause)))} /></div></div>}
    <Views.MobileBottomNav pathname={pathname} />
    {editor && <Suspense fallback={<Loading />}><EditorModal key={editor.kind + editor.id} editor={editor} data={data} user={user} onSave={save} onDelete={remove} onClose={() => setEditor(null)} /></Suspense>}
    {tutorial && <Suspense fallback={<Loading />}><TutorialModal onClose={() => setTutorial(false)} /></Suspense>}
    {toast && <div className="toast" role="status">{toast}</div>}
  </main>;
}

export default function EduTrackApp() {
  const pathname = usePathname();
  const router = useStudyRouter();
  const [user, setUser] = useState<ApiUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState('');
  const requestVersion = useRef(0);
  const isAuth = ['/login', '/cadastro', '/recuperar-senha'].includes(pathname);
  function acceptUser(value: ApiUser | null) { setApiUser(value?.id || null); setUser(value); }
  useEffect(() => {
    const version = ++requestVersion.current;
    api<ApiUser>('me').then((result) => { if (version === requestVersion.current) { setApiUser(result.id); setUser(result); } })
      .catch((cause) => { if (version === requestVersion.current && cause.status !== 401) setError(errorText(cause)); })
      .finally(() => { if (version === requestVersion.current) setChecking(false); });
    const expired = () => { ++requestVersion.current; setApiUser(null); setUser(null); setChecking(false); };
    const checkTab = () => {
      if (document.visibilityState !== 'visible') return;
      const current = ++requestVersion.current;
      api<ApiUser>('me')
        .then((result) => { if (current === requestVersion.current) { setApiUser(result.id); setUser(result); setError(''); } })
        .catch((cause) => { if (current === requestVersion.current && cause.status !== 401) setError(errorText(cause)); })
        .finally(() => { if (current === requestVersion.current) setChecking(false); });
    };
    window.addEventListener('edutrack-session-expired', expired);
    window.addEventListener('focus', checkTab);
    document.addEventListener('visibilitychange', checkTab);
    // O ref é um contador de requisições, não um elemento DOM: invalidar o valor mais recente é intencional.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    return () => { ++requestVersion.current; window.removeEventListener('edutrack-session-expired', expired); window.removeEventListener('focus', checkTab); document.removeEventListener('visibilitychange', checkTab); };
  }, []);
  useEffect(() => { if (!checking && !user && !isAuth && !error) router.replace('/login'); }, [checking, user, isAuth, error, router]);
  async function logout() {
    await api('auth/logout', { method: 'POST', body: '{}' });
    ++requestVersion.current; acceptUser(null); router.replace('/login');
  }
  if (checking) return <Loading />;
  if (pathname === '/recuperar-senha') return <PasswordRecovery />;
  if (isAuth) return <ConnectedAuth key={pathname} register={pathname === '/cadastro'} onLogin={(result) => { ++requestVersion.current; acceptUser(result); setError(''); }} />;
  if (!user) return error ? <main className="connection-loading"><h1>Não foi possível conectar</h1><p role="alert">{error}</p><button className="secondary-button" onClick={() => window.location.reload()}>Tentar novamente</button></main> : <Loading />;
  return <ConnectedApp key={user.id} user={user} onUser={acceptUser} logout={logout} />;
}
