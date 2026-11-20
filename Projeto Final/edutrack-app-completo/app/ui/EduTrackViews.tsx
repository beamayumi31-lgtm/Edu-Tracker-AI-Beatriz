'use client';

import { AlarmClock, ArrowLeft, ArrowRight, BarChart3, Bell, BookOpen, Bot, BookMarked, CalendarDays, CheckCircle2, ChevronRight, CircleAlert, ClipboardList, Clock3, Compass, Crown, Edit3, ExternalLink, FileText, Filter, CircleHelp, Flame, GraduationCap, KeyRound, LayoutDashboard, ListTodo, LogOut, Mail, Menu, PanelLeftClose, PanelLeftOpen, Phone, Plus, Search, Settings, ShieldCheck, Sparkles, Target } from 'lucide-react';

import { Brand, ThemeToggle } from './Brand';
import StudyActivity from './StudyActivity';
import WeeklyReport from './WeeklyReport';
import { useStudyRouter as useRouter } from './useStudyRouter';
import { studySummary, type StudySession } from '../lib/study-game';
import { useState, type CSSProperties, type ReactNode } from 'react';
import type { Course, Discipline, StudyTask, Profile } from '../lib/academic-types';
import ClassroomLibrary from './ClassroomLibrary';
import DisciplineSearch from './DisciplineSearch';
type AccountStatus = { role: 'student' | 'admin'; plan: 'Gratuito' | 'Interesse no Pro' };
export type SuggestedCourse = { title: string; source: string; type: string; category: string; description: string; duration: string; color: string };

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/cursos', label: 'Cursos', icon: GraduationCap },
  { path: '/descobrir', label: 'Descobrir', icon: Compass },
  { path: '/disciplinas', label: 'Disciplinas', icon: BookOpen },
  { path: '/tarefas', label: 'Tarefas', icon: CheckCircle2 },
  { path: '/cronometro', label: 'Cronômetro', icon: Clock3 },
  { path: '/ofensiva', label: 'Ofensiva', icon: Flame },
  { path: '/relatorios', label: 'Relatórios', icon: BarChart3 },
  { path: '/edu-ia', label: 'Edu IA', icon: Bot },
  { path: '/integracoes', label: 'Integrações', icon: BookMarked },
  { path: '/gerenciamento', label: 'Administração', icon: Settings, adminOnly: true },
];

const suggestedCourses: SuggestedCourse[] = [
  { title: 'Fundamentos de Python', source: 'Sugestão EduTrack', type: 'Curso livre', category: 'Tecnologia', description: 'Lógica, estruturas de dados e primeiros projetos para construir uma base sólida.', duration: '8 semanas', color: 'cyan' },
  { title: 'Banco de Dados e SQL', source: 'Sugestão EduTrack', type: 'Curso livre', category: 'Tecnologia', description: 'Modelagem relacional, consultas SQL e práticas para projetos acadêmicos.', duration: '10 semanas', color: 'violet' },
  { title: 'Inglês para a vida acadêmica', source: 'Sugestão EduTrack', type: 'Curso livre', category: 'Idiomas', description: 'Leitura, vocabulário e comunicação aplicados a estudos e apresentações.', duration: '12 semanas', color: 'emerald' },
  { title: 'Gestão do tempo e foco', source: 'Sugestão EduTrack', type: 'Curso livre', category: 'Produtividade', description: 'Planejamento semanal, prioridades e técnicas de foco adaptáveis à rotina.', duration: '4 semanas', color: 'amber' },
  { title: 'Comunicação e apresentações', source: 'Sugestão EduTrack', type: 'Curso livre', category: 'Carreira', description: 'Estruture ideias, apresente projetos e comunique resultados com clareza.', duration: '6 semanas', color: 'rose' },
  { title: 'Introdução à Inteligência Artificial', source: 'Sugestão EduTrack', type: 'Curso livre', category: 'Tecnologia', description: 'Conceitos essenciais, usos responsáveis e aplicações no aprendizado.', duration: '6 semanas', color: 'violet' },
];

function formatMinutes(total: number) {
  const hours = Math.floor(total / 60);
  const minutes = total % 60;
  if (!hours) return String(minutes) + 'min';
  return minutes ? String(hours) + 'h ' + String(minutes) + 'min' : String(hours) + 'h';
}
function localDateKey(date: Date) {
  return String(date.getFullYear()) + '-' +
    String(date.getMonth() + 1).padStart(2, '0') + '-' +
    String(date.getDate()).padStart(2, '0');
}
function taskDisciplineName(task: StudyTask, disciplines: Discipline[]) {
  return disciplines.find((discipline) => discipline.id === task.disciplineId)?.title ||
    task.discipline || 'Sem disciplina';
}
function isTaskOverdue(task: StudyTask) {
  return Boolean(task.due && !['Concluída', 'Cancelada'].includes(task.status) && task.due < localDateKey(new Date()));
}
function isTaskDueSoon(task: StudyTask) {
  if (!task.due || ['Concluída', 'Cancelada'].includes(task.status)) return false;
  const due = new Date(task.due + 'T23:59:59');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const limit = new Date(today);
  limit.setDate(limit.getDate() + 7);
  return due >= today && due <= limit;
}
function formatTaskDue(task: StudyTask) {
  if (!task.due) return 'Sem prazo';
  const today = localDateKey(new Date());
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  if (task.due === today) return 'Entrega hoje';
  if (task.due === localDateKey(tomorrow)) return 'Entrega amanhã';
  return 'Entrega em ' + new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short' })
    .format(new Date(task.due + 'T12:00:00'));
}
function safeExternalUrl(value?: string) {
  return value && /^https?:\/\//i.test(value) ? value : undefined;
}
function getStudyStreak(sessions: StudySession[]) {
  return studySummary(sessions).streak;
}
function getInitials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return 'ET';
  return (parts[0][0] + (parts.at(-1)?.[0] || '')).toUpperCase();
}

function AppSidebar({ pathname, profile, plan, role, close, onLogout }: { pathname: string; profile: Profile; plan: AccountStatus['plan']; role: AccountStatus['role']; close?: () => void; onLogout: () => void }) {
  const router = useRouter();
  function navigate(path: string) { router.push(path); close?.(); }
  const visibleNavItems = navItems.filter((item) => !item.adminOnly || role === 'admin');
  return (
    <aside className="app-sidebar">
      <Brand />
      <nav>{visibleNavItems.map(({ path, label, icon: Icon }) => <button key={path} className={pathname.startsWith(path) ? 'active' : ''} onClick={() => navigate(path)}><Icon size={19} /> {label}</button>)}</nav>
      <button className="sidebar-upgrade" onClick={() => navigate('/upgrade')}>
        <span><Crown size={17} /></span>
        <div><strong>{plan === 'Gratuito' ? 'Conheça o EduTrack Pro' : 'Interesse no Pro salvo'}</strong><small>Recursos futuros · sem cobrança</small></div>
        <ChevronRight size={16} />
      </button>
      <div className="sidebar-profile">
        <button className="sidebar-profile-link" type="button" onClick={() => navigate('/perfil')} aria-label="Abrir perfil">
          <span className="sidebar-profile-avatar">{getInitials(profile.name)}</span>
          <span className="sidebar-profile-copy"><strong>{profile.name || 'Seu perfil'}</strong><small>{profile.area || 'Personalizar informações'}</small></span>
        </button>
        <button className="sidebar-switch-account" type="button" onClick={onLogout} aria-label="Sair da conta" title="Sair da conta">
          <LogOut size={18} strokeWidth={1.8} aria-hidden="true" />
        </button>
      </div>
    </aside>
  );
}

function Topbar({
  profile, openMenu, sidebarHidden, toggleSidebar, openTutorial,
}: {
  profile: Profile; openMenu: () => void; sidebarHidden: boolean;
  toggleSidebar: () => void; openTutorial: () => void;
}) {
  const router = useRouter();
  return (
    <header className="topbar">
      <button className="mobile-menu" onClick={openMenu} aria-label="Abrir navegação"><Menu /></button>
      <button
        className="sidebar-toggle"
        onClick={toggleSidebar}
        aria-label={sidebarHidden ? 'Mostrar menu lateral' : 'Esconder menu lateral'}
        aria-expanded={!sidebarHidden}
        title={sidebarHidden ? 'Mostrar menu' : 'Esconder menu'}
      >
        {sidebarHidden ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
      </button>
      <div className="mobile-brand"><Brand compact /></div>
      <div className="top-search"><Search size={18} /><input aria-label="Buscar no EduTrack" placeholder="Buscar cursos, disciplinas e tarefas..." /></div>
      <button className="tutorial-trigger" type="button" onClick={openTutorial} aria-label="Abrir tutorial do EduTrack" title="Abrir tutorial">
        <CircleHelp size={18} /><span>Tutorial</span>
      </button>
      <ThemeToggle compact />
      <button className="icon-button" aria-label="Notificações"><Bell size={20} /></button>
      <button className="top-avatar" onClick={() => router.push('/perfil')} aria-label="Abrir perfil">{getInitials(profile.name)}</button>
    </header>
  );
}

function MobileBottomNav({ pathname }: { pathname: string }) {
  const router = useRouter();
  const items = navItems.filter((item) => ['/dashboard', '/cursos', '/tarefas', '/edu-ia'].includes(item.path));
  return <nav className="mobile-bottom-nav">{items.map(({ path, label, icon: Icon }) => <button key={path} className={pathname.startsWith(path) ? 'active' : ''} onClick={() => router.push(path)}><Icon size={19} /><span>{label === 'Dashboard' ? 'Início' : label}</span></button>)}</nav>;
}

function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return <div className="page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{action}</div>;
}

function EmptyState({ icon, title, description, action }: { icon: ReactNode; title: string; description: string; action?: ReactNode }) {
  return <div className="empty-state"><span className="empty-state-icon">{icon}</span><h3>{title}</h3><p>{description}</p>{action}</div>;
}

function Dashboard({ tasks, courses, sessions, profile, navigate }: {
  tasks: StudyTask[]; courses: Course[]; sessions: StudySession[];
  profile: Profile; navigate: (path: string) => void;
}) {
  const pendingTasks = tasks.filter((task) => !['Concluída', 'Cancelada'].includes(task.status));
  const averageProgress = courses.length
    ? Math.round(courses.reduce((sum, course) => sum + course.progress, 0) / courses.length)
    : 0;
  const studiedMinutes = sessions.reduce((sum, session) => sum + session.minutes, 0);
  const streak = getStudyStreak(sessions);
  const nextTask = pendingTasks[0];
  return (
    <>
      <section className="dashboard-welcome">
        <div>
          <span className="hero-kicker"><Sparkles size={15} /> Seu espaço acadêmico</span>
          <h1>{profile.name ? 'Bem-vindo, ' + profile.name.split(' ')[0] + '.' : 'Bem-vindo ao EduTrack.'}</h1>
          <p>Um pouco a cada dia. Acompanhe o ritmo dos seus estudos.</p>
        </div>
          <div className="dashboard-welcome-actions">
            <button className="primary-button" onClick={() => navigate(courses.length ? '/cronometro' : '/cursos')}>
              {courses.length ? 'Iniciar sessão de foco' : 'Adicionar primeiro curso'} <ArrowRight size={17} />
            </button>
            <button className="secondary-button" onClick={() => navigate('/edu-ia')}><Sparkles size={16} /> Edu IA</button>
          </div>
      </section>
      <StudyActivity sessions={sessions} navigate={navigate} />
      <section className="metric-grid">
        <article className="metric-card"><span className="metric-icon violet"><Target /></span><div><span>Progresso geral</span><strong>{averageProgress}%</strong><small>{courses.length ? String(courses.length) + (courses.length === 1 ? ' curso cadastrado' : ' cursos cadastrados') : 'adicione um curso'}</small></div></article>
        <article className="metric-card"><span className="metric-icon amber"><CalendarDays /></span><div><span>Tarefas pendentes</span><strong>{pendingTasks.length}</strong><small>{tasks.length ? String(tasks.filter((task) => task.status === 'Concluída').length) + ' concluídas' : 'nenhuma tarefa criada'}</small></div></article>
        <button type="button" className="metric-card metric-action metric-focus" onClick={() => navigate('/cronometro')} aria-label={'Tempo de estudo: ' + formatMinutes(studiedMinutes) + '. Abrir floresta de foco'}><span className="metric-icon emerald"><Clock3 /></span><div><span>Tempo de estudo</span><strong>{formatMinutes(studiedMinutes)}</strong><small>Cultivar minha floresta <ArrowRight size={13} /></small></div></button>
        <button type="button" className="metric-card metric-action metric-streak" onClick={() => navigate('/ofensiva')} aria-label={'Ofensiva de estudos: ' + streak + ' dias. Ver minha ofensiva'}><span className="metric-icon amber"><Flame /></span><div><span>Ofensiva de estudos</span><strong>{streak} {streak === 1 ? 'dia' : 'dias'}</strong><small>Ver minha ofensiva <ArrowRight size={13} /></small></div></button>
      </section>
      <section className="dashboard-grid">
        <article className="surface tasks-surface">
          <div className="section-heading"><div><span>Prioridades</span><h2>Próximas tarefas</h2></div><button onClick={() => navigate('/tarefas')}>Ver todas <ChevronRight size={16} /></button></div>
          {pendingTasks.length
            ? <div className="task-list">{pendingTasks.slice(0, 4).map((task) => <div className="task-row" key={task.id}><span className="task-check" /><div><strong>{task.title}</strong><span>{task.discipline || 'Sem disciplina'}</span></div><time className={task.priority === 'Alta' ? 'urgent' : ''}>{task.due || 'Sem data'}{task.time ? ', ' + task.time : ''}</time></div>)}</div>
            : <EmptyState icon={<CheckCircle2 />} title="Tudo começa com uma tarefa" description="Cadastre uma entrega, revisão ou atividade para acompanhar por aqui." action={<button className="secondary-button compact" onClick={() => navigate('/tarefas')}>Criar tarefa</button>} />}
        </article>
        <article className="surface focus-surface">
          <span className="focus-label"><Sparkles size={16} /> Próximo passo</span>
          <h2>{nextTask ? nextTask.title : 'Crie um bloco de foco.'}</h2>
          <p>{nextTask ? (nextTask.discipline || 'Tarefa livre') + ' · ' + (nextTask.duration || 'Defina o tempo no cronômetro') : 'Escolha 15, 25, 45 ou 60 minutos e concentre-se em uma coisa por vez.'}</p>
          <button className="primary-button" onClick={() => navigate('/cronometro')}>Abrir cronômetro <ArrowRight size={17} /></button>
        </article>
      </section>
      <section className="surface course-surface">
        <div className="section-heading"><div><span>Aprendizado</span><h2>Seus cursos</h2></div><button onClick={() => navigate('/cursos')}>Gerenciar cursos <ChevronRight size={16} /></button></div>
        {courses.length
          ? <div className="course-grid">{courses.slice(0, 3).map((course) => <CourseMiniCard key={course.id} course={course} onClick={() => navigate('/cursos/' + course.id)} />)}</div>
          : <EmptyState icon={<GraduationCap />} title="Nenhum curso cadastrado" description="Adicione sua faculdade, uma formação online ou um estudo independente." action={<button className="primary-button compact" onClick={() => navigate('/cursos')}>Adicionar curso</button>} />}
      </section>
    </>
  );
}

function CourseMiniCard({ course, onClick, edit }: { course: Course; onClick?: () => void; edit?: () => void }) {
  return <article className="course-card clickable-card" onClick={onClick}><div className="card-top"><span className={'course-symbol ' + course.color}><GraduationCap size={21} /></span>{edit && <button className="edit-button" onClick={(event) => { event.stopPropagation(); edit(); }} aria-label={'Editar ' + course.title}><Edit3 size={16} /></button>}</div><small>{course.source || course.type}</small><h3>{course.title}</h3><div className="progress-copy"><span>Progresso</span><strong>{course.progress}%</strong></div><div className="progress-track"><span className={course.color} style={{ width: String(course.progress) + '%' }} /></div></article>;
}

function CoursesPage({ courses, edit, add, navigate }: { courses: Course[]; edit: (id: string) => void; add: () => void; navigate: (path: string) => void }) {
  return <><PageHeading eyebrow="Aprendizado" title="Meus cursos" description="Faculdade, plataformas e cursos independentes organizados no mesmo espaço." action={<button className="primary-button" onClick={add}><Plus size={17} /> Novo curso</button>} /><section className="catalog-grid">{courses.map((course) => <CourseMiniCard key={course.id} course={course} edit={() => edit(course.id)} onClick={() => navigate('/cursos/' + course.id)} />)}<button className="add-card" onClick={add}><Plus /><strong>{courses.length ? 'Adicionar outro curso' : 'Adicionar seu primeiro curso'}</strong><span>Universidade, plataforma ou estudo independente</span></button></section></>;
}

function CourseDetails({ course, disciplines, edit, goBack }: { course: Course; disciplines: Discipline[]; edit: () => void; goBack: () => void }) {
  const style = { '--course-progress': String(course.progress) + '%' } as CSSProperties;
  return <><button className="back-button" onClick={goBack}><ArrowLeft size={17} /> Voltar para cursos</button><section className="course-hero surface"><div><span className="eyebrow">{course.source || course.type}{course.period ? ' · ' + course.period : ''}</span><h1>{course.title}</h1><p>Acompanhe disciplinas, tarefas e evolução dentro deste curso.</p></div><div className="course-hero-actions"><div className="hero-progress" style={style}><strong>{course.progress}%</strong><span>progresso geral</span></div><button className="secondary-button" onClick={edit}><Edit3 size={16} /> Editar curso</button></div></section><section className="content-section"><div className="section-heading"><div><span>Estrutura</span><h2>Disciplinas vinculadas</h2></div></div>{disciplines.length ? <div className="discipline-grid">{disciplines.map((item) => <DisciplineCard key={item.id} item={item} />)}</div> : <EmptyState icon={<BookOpen />} title="Nenhuma disciplina vinculada" description="Crie disciplinas e vincule-as a este curso para organizar melhor o conteúdo." />}</section></>;
}

function DisciplineCard({ item, tasks = [], edit, open }: {
  item: Discipline; tasks?: StudyTask[]; edit?: () => void; open?: () => void;
}) {
  const disciplineTasks = tasks.filter((task) => task.disciplineId === item.id || (!task.disciplineId && task.discipline === item.title));
  const pendingTasks = disciplineTasks.filter((task) => !['Concluída', 'Cancelada'].includes(task.status));
  const nextTask = [...pendingTasks].sort((a, b) => (a.due || '9999').localeCompare(b.due || '9999'))[0];
  return (
    <article className="discipline-card classroom-discipline-card">
      <div className={'discipline-cover ' + item.color}>
        <span><BookOpen size={21} /></span>
        {edit && <button className="edit-button" onClick={edit} aria-label={'Editar ' + item.title}><Edit3 size={16} /></button>}
      </div>
      <div className="discipline-card-body">
        <small>{item.semester || 'Período não informado'}</small>
        <h3>{item.title}</h3>
        <p>{item.teacher || 'Professor não informado'}</p>
        <div className="discipline-classroom-meta">
          <span><ClipboardList size={14} /> {pendingTasks.length} {pendingTasks.length === 1 ? 'atividade pendente' : 'atividades pendentes'}</span>
          <span><Target size={14} /> {item.goal || 'Meta não definida'}</span>
        </div>
        <div className="discipline-next-task">
          <span>{nextTask ? formatTaskDue(nextTask) : 'Agenda livre'}</span>
          <strong>{nextTask?.title || 'Nenhuma atividade pendente'}</strong>
        </div>
        <div className="progress-copy"><span>Progresso</span><strong>{item.progress}%</strong></div>
        <div className="progress-track"><span className={item.color} style={{ width: String(item.progress) + '%' }} /></div>
      </div>
      {open && <button className="discipline-open" onClick={open}>Abrir disciplina <ChevronRight size={16} /></button>}
    </article>
  );
}

function DisciplinesPage({ disciplines, courses, tasks, edit, add, goToCourses, navigate }: {
  disciplines: Discipline[]; courses: Course[]; tasks: StudyTask[]; edit: (id: string) => void;
  add: () => void; goToCourses: () => void; navigate: (path: string) => void;
}) {
  const pending = tasks.filter((task) => !['Concluída', 'Cancelada'].includes(task.status));
  const dueSoon = pending.filter(isTaskDueSoon);
  return (
    <>
      <PageHeading eyebrow="Minhas turmas" title="Disciplinas" description="Acesse cada matéria, acompanhe avisos e encontre rapidamente suas próximas atividades." action={<button className="primary-button" onClick={courses.length ? add : goToCourses}><Plus size={17} /> {courses.length ? 'Nova disciplina' : 'Adicionar curso primeiro'}</button>} />
      <DisciplineSearch navigate={navigate} />
      {disciplines.length ? <>
        <section className="classroom-summary surface">
          <div><span className="summary-icon violet"><BookOpen /></span><p><strong>{disciplines.length}</strong><small>disciplinas ativas</small></p></div>
          <div><span className="summary-icon amber"><ClipboardList /></span><p><strong>{pending.length}</strong><small>atividades a fazer</small></p></div>
          <div><span className="summary-icon cyan"><CalendarDays /></span><p><strong>{dueSoon.length}</strong><small>entregas em 7 dias</small></p></div>
          <button onClick={() => navigate('/tarefas')}>Ver agenda de tarefas <ArrowRight size={16} /></button>
        </section>
        <section className="discipline-grid page-grid classroom-discipline-grid">
          {disciplines.map((item) => <DisciplineCard key={item.id} item={item} tasks={tasks} edit={() => edit(item.id)} open={() => navigate('/disciplinas/' + item.id)} />)}
        </section>
      </> : <section className="standalone-empty surface"><EmptyState icon={<BookOpen />} title="Nenhuma disciplina cadastrada" description={courses.length ? 'Adicione as disciplinas do seu curso e acompanhe cada evolução.' : 'Cadastre primeiro um curso para poder vincular suas disciplinas.'} action={<button className="secondary-button" onClick={courses.length ? add : goToCourses}>{courses.length ? 'Criar disciplina' : 'Ir para cursos'}</button>} /></section>}
    </>
  );
}

function DisciplineDetails({ discipline, course, tasks, edit, addTask, editTask, toggle, goBack }: {
  discipline: Discipline; course?: Course; tasks: StudyTask[]; edit: () => void; addTask: () => void;
  editTask: (id: string) => void; toggle: (id: string) => void; goBack: () => void;
}) {
  const disciplineTasks = tasks.filter((task) => task.disciplineId === discipline.id || (!task.disciplineId && task.discipline === discipline.title));
  const pending = disciplineTasks.filter((task) => !['Concluída', 'Cancelada'].includes(task.status));
  const orderedTasks = [...disciplineTasks].sort((a, b) => (a.status === 'Concluída' ? 1 : 0) - (b.status === 'Concluída' ? 1 : 0) || (a.due || '9999').localeCompare(b.due || '9999'));
  return (
    <>
      <button className="back-button" onClick={goBack}><ArrowLeft size={17} /> Voltar para disciplinas</button>
      <section className={'classroom-class-hero ' + discipline.color}>
        <div><span>{course?.title || 'Curso não informado'}{discipline.semester ? ' · ' + discipline.semester : ''}</span><h1>{discipline.title}</h1><p>{discipline.teacher || 'Professor não informado'}</p></div>
        <button className="class-hero-edit" onClick={edit}><Edit3 size={16} /> Editar disciplina</button>
      </section>
      <section className="classroom-class-layout">
        <aside className="surface class-overview">
          <span className="eyebrow">Visão geral</span>
          <h2>Seu progresso</h2>
          <div className="class-progress-number"><strong>{discipline.progress}%</strong><span>concluído</span></div>
          <div className="progress-track"><span className={discipline.color} style={{ width: discipline.progress + '%' }} /></div>
          <dl><div><dt>Atividades pendentes</dt><dd>{pending.length}</dd></div><div><dt>Meta semanal</dt><dd>{discipline.goal || 'Não definida'}</dd></div><div><dt>Status</dt><dd>{discipline.status}</dd></div></dl>
        </aside>
        <div className="classroom-stream">
          <article className="surface stream-composer"><span><ClipboardList /></span><div><strong>Organize uma nova atividade</strong><p>Adicione prazo, prioridade, material e instruções para estudar.</p></div><button className="primary-button compact" onClick={addTask}><Plus size={16} /> Criar atividade</button></article>
          <div className="section-heading stream-heading"><div><span>Mural da disciplina</span><h2>Atividades</h2></div><strong>{pending.length} a fazer</strong></div>
          {orderedTasks.length ? <div className="class-activity-feed">{orderedTasks.map((task) => (
            <article className={'class-activity-item surface ' + (task.status === 'Concluída' ? 'done' : '')} key={task.id}>
              <span className="activity-type-icon"><FileText /></span>
              <div><div className="activity-line"><span>{task.category || 'Atividade'}</span>{isTaskOverdue(task) && <em>Atrasada</em>}</div><h3>{task.title}</h3><p>{task.notes || 'Sem instruções adicionais.'}</p><div className="task-details"><span><CalendarDays size={14} /> {formatTaskDue(task)}{task.time ? ', ' + task.time : ''}</span><span><AlarmClock size={14} /> {task.duration || 'Tempo livre'}</span></div></div>
              <div className="activity-actions"><button className="task-status-button" onClick={() => toggle(task.id)}>{task.status === 'Concluída' ? 'Reabrir' : 'Concluir'}</button><button className="edit-button" onClick={() => editTask(task.id)} aria-label={'Editar ' + task.title}><Edit3 size={16} /></button></div>
            </article>
          ))}</div> : <section className="surface class-empty"><EmptyState icon={<ClipboardList />} title="Nenhuma atividade nesta disciplina" description="Crie a primeira atividade para montar seu mural de estudos." action={<button className="secondary-button" onClick={addTask}>Criar atividade</button>} /></section>}
          <ClassroomLibrary key={discipline.id} disciplineId={discipline.id} />
        </div>
      </section>
    </>
  );
}

function TasksPage({ tasks, disciplines, courses, edit, add, toggle, goToCourses }: {
  tasks: StudyTask[]; disciplines: Discipline[]; courses: Course[]; edit: (id: string) => void;
  add: () => void; toggle: (id: string) => void; goToCourses: () => void;
}) {
  const [filter, setFilter] = useState<'A fazer' | 'Concluídas' | 'Todas'>('A fazer');
  const [disciplineFilter, setDisciplineFilter] = useState('');
  const pending = tasks.filter((task) => !['Concluída', 'Cancelada'].includes(task.status));
  const overdue = pending.filter(isTaskOverdue);
  const dueSoon = pending.filter(isTaskDueSoon);
  const selectedDiscipline = disciplines.find((discipline) => discipline.id === disciplineFilter);
  const visibleTasks = tasks
    .filter((task) => filter === 'Todas' || (filter === 'Concluídas' ? task.status === 'Concluída' : !['Concluída', 'Cancelada'].includes(task.status)))
    .filter((task) => !disciplineFilter || task.disciplineId === disciplineFilter || (!task.disciplineId && task.discipline === selectedDiscipline?.title))
    .sort((a, b) => (isTaskOverdue(a) ? -1 : 0) - (isTaskOverdue(b) ? -1 : 0) || (a.due || '9999').localeCompare(b.due || '9999'));
  return (
    <>
      <PageHeading eyebrow="Central de atividades" title="Tarefas" description="Acompanhe tudo o que foi atribuído, os próximos prazos e o que você já concluiu." action={<button className="primary-button" onClick={courses.length ? add : goToCourses}><Plus size={17} /> {courses.length ? 'Nova atividade' : 'Adicionar curso primeiro'}</button>} />
      <section className="task-summary-grid">
        <article className="surface"><span className="summary-icon violet"><ListTodo /></span><div><strong>{pending.length}</strong><p>A fazer</p></div></article>
        <article className="surface"><span className="summary-icon amber"><CalendarDays /></span><div><strong>{dueSoon.length}</strong><p>Próximos 7 dias</p></div></article>
        <article className="surface"><span className="summary-icon rose"><CircleAlert /></span><div><strong>{overdue.length}</strong><p>Atrasadas</p></div></article>
      </section>
      <section className="filter-bar surface classroom-filter-bar">
        <div className="filter-tabs">{(['A fazer', 'Concluídas', 'Todas'] as const).map((item) => <button key={item} className={filter === item ? 'active' : ''} onClick={() => setFilter(item)}>{item}</button>)}</div>
        <label><Filter size={15} /><select value={disciplineFilter} onChange={(event) => setDisciplineFilter(event.target.value)} aria-label="Filtrar por disciplina"><option value="">Todas as disciplinas</option>{disciplines.map((discipline) => <option key={discipline.id} value={discipline.id}>{discipline.title}</option>)}</select></label>
        <span className="filter-count">{visibleTasks.length} {visibleTasks.length === 1 ? 'atividade' : 'atividades'}</span>
      </section>
      {visibleTasks.length ? <section className="classroom-task-list">{visibleTasks.map((task) => {
        const course = courses.find((item) => item.id === task.courseId);
        const materialUrl = safeExternalUrl(task.materialUrl);
        return <article className={'classroom-task-card surface ' + (task.status === 'Concluída' ? 'done' : '')} key={task.id}>
          <span className="activity-type-icon"><FileText /></span>
          <div className="classroom-task-copy"><div className="activity-line"><span>{task.category || 'Atividade'}</span>{isTaskOverdue(task) && <em>Atrasada</em>}{task.priority === 'Alta' && <em className="priority">Prioridade alta</em>}</div><h3>{task.title}</h3><p>{taskDisciplineName(task, disciplines)}{course ? ' · ' + course.title : ''}</p><div className="task-details"><span><CalendarDays size={14} /> {formatTaskDue(task)}{task.time ? ', ' + task.time : ''}</span><span><AlarmClock size={14} /> {task.duration || 'Tempo livre'}</span></div>{task.notes && <small>{task.notes}</small>}</div>
          <div className="classroom-task-actions">{materialUrl && <a href={materialUrl} target="_blank" rel="noreferrer">Material <ExternalLink size={14} /></a>}<button className="task-status-button" onClick={() => toggle(task.id)}>{task.status === 'Concluída' ? 'Reabrir' : 'Marcar como concluída'}</button><button className="edit-button" onClick={() => edit(task.id)} aria-label={'Editar ' + task.title}><Edit3 size={16} /></button></div>
        </article>;
      })}</section> : <section className="standalone-empty surface"><EmptyState icon={<CheckCircle2 />} title={tasks.length ? 'Nenhuma atividade neste filtro' : 'Nenhuma atividade cadastrada'} description={tasks.length ? 'Altere os filtros para consultar outras atividades.' : courses.length ? 'Crie sua primeira atividade com disciplina, prazo e instruções.' : 'Cadastre primeiro um curso para organizar suas atividades.'} action={!tasks.length && <button className="secondary-button" onClick={courses.length ? add : goToCourses}>{courses.length ? 'Criar atividade' : 'Ir para cursos'}</button>} /></section>}
    </>
  );
}


function ReportsPage({ disciplines, sessions }: { disciplines: Discipline[]; sessions: StudySession[] }) { return <WeeklyReport disciplines={disciplines} sessions={sessions} />; }

function ProfilePage({ profile, courses, sessions, edit }: {
  profile: Profile; courses: Course[]; sessions: StudySession[]; edit: () => void;
}) {
  const progress = courses.length
    ? Math.round(courses.reduce((sum, course) => sum + course.progress, 0) / courses.length)
    : 0;
  return <><PageHeading eyebrow="Conta" title="Perfil" description="Confira sua conta e atualize seu nome." action={<button className="secondary-button" onClick={edit}><Edit3 size={16} /> Editar perfil</button>} /><section className="profile-layout"><article className="surface profile-card"><div className="profile-avatar">{getInitials(profile.name)}</div><h2>{profile.name || 'Seu nome'}</h2><p>{profile.area || 'Conta conectada à API'}{profile.institution ? ' · ' + profile.institution : ''}</p><div className="profile-stats"><div><strong>{courses.length}</strong><span>cursos</span></div><div><strong>{getStudyStreak(sessions)}</strong><span>dias de ofensiva</span></div><div><strong>{progress}%</strong><span>progresso</span></div></div></article><article className="surface preferences-card"><div className="section-heading"><div><span>Preferências</span><h2>Preferências futuras</h2><p>Estes campos ainda não têm suporte de gravação na API.</p></div></div><div className="preference-row"><span><Clock3 /> Técnica de foco</span><strong>{profile.focusTechnique || 'Não definida'}</strong></div><div className="preference-row"><span><CalendarDays /> Meta semanal</span><strong>{profile.weeklyGoal || 'Não definida'}</strong></div><div className="preference-row"><span><Bell /> Lembretes</span><strong>{profile.reminders || 'Não definidos'}</strong></div>{profile.preferences && <div className="profile-note"><span>Observações</span><p>{profile.preferences}</p></div>}</article></section></>;
}

function DiscoverPage({ courses, addCourse }: { courses: Course[]; addCourse: (course: SuggestedCourse) => void }) {
  const [category, setCategory] = useState('Todos');
  const categories = ['Todos', ...Array.from(new Set(suggestedCourses.map((course) => course.category)))];
  const visibleCourses = category === 'Todos' ? suggestedCourses : suggestedCourses.filter((course) => course.category === category);
  const alreadyAdded = (suggestion: SuggestedCourse) => courses.some((course) => course.title.toLocaleLowerCase('pt-BR') === suggestion.title.toLocaleLowerCase('pt-BR') && course.source === suggestion.source);

  return (
    <>
      <PageHeading eyebrow="Explore novos caminhos" title="Descobrir cursos" description="Sugestões gerais para ampliar seus estudos. Adicione uma ideia ao painel e personalize quando quiser." />
      <section className="discovery-banner surface">
        <span className="discovery-icon"><Compass /></span>
        <div><span>Curadoria inicial</span><h2>Escolha pelo seu objetivo, não pelo impulso.</h2><p>As opções abaixo são referências demonstrativas. O EduTrack não realiza matrícula nem possui vínculo com instituições.</p></div>
        <Sparkles className="discovery-spark" />
      </section>
      <section className="category-pills" aria-label="Filtrar sugestões por categoria">
        {categories.map((item) => <button key={item} className={category === item ? 'active' : ''} onClick={() => setCategory(item)}>{item}</button>)}
      </section>
      <section className="suggestion-grid">
        {visibleCourses.map((course) => {
          const added = alreadyAdded(course);
          return <article className="suggestion-card surface" key={course.title}>
            <div className="suggestion-top"><span className={'course-symbol ' + course.color}><BookMarked size={21} /></span><small>{course.category}</small></div>
            <h2>{course.title}</h2><p>{course.description}</p>
            <div className="suggestion-meta"><span><Clock3 size={14} /> {course.duration}</span><span><GraduationCap size={14} /> {course.type}</span></div>
            <button className={added ? 'secondary-button' : 'primary-button'} disabled={added} onClick={() => addCourse(course)}>{added ? <><CheckCircle2 size={17} /> Adicionado</> : <><Plus size={17} /> Adicionar aos meus cursos</>}</button>
          </article>;
        })}
      </section>
    </>
  );
}

function ManagementPage({ role, navigate }: { role: AccountStatus['role']; navigate: (path: string) => void }) {
  if (role !== 'admin') {
    return (
      <section className="admin-restricted surface">
        <span className="admin-restricted-icon"><ShieldCheck /></span>
        <span className="eyebrow">Área protegida</span>
        <h1>Acesso exclusivo para administradores</h1>
        <p>Esta página reúne dados e configurações de todo o EduTrack. Contas de aluno não podem visualizar ou alterar essas informações.</p>
        <div className="admin-security-note"><KeyRound size={17} /><span><strong>Controle pela futura API</strong><small>O servidor verificará a permissão de administrador em todas as solicitações.</small></span></div>
        <button className="primary-button" onClick={() => navigate('/dashboard')}>Voltar ao meu painel <ArrowRight size={17} /></button>
      </section>
    );
  }

  return (
    <>
      <PageHeading eyebrow="Acesso administrativo" title="Painel administrativo" description="Gerencie contas, validações, catálogo e integrações do EduTrack." action={<span className="admin-role-badge"><ShieldCheck size={16} /> Administrador</span>} />
      <section className="admin-summary-grid">
        <article className="surface"><span className="admin-summary-icon violet"><LayoutDashboard /></span><div><small>USUÁRIOS CADASTRADOS</small><strong>—</strong><span>Aguardando API</span></div></article>
        <article className="surface"><span className="admin-summary-icon emerald"><ShieldCheck /></span><div><small>CONTAS VERIFICADAS</small><strong>—</strong><span>E-mail ou SMS</span></div></article>
        <article className="surface"><span className="admin-summary-icon cyan"><BookMarked /></span><div><small>CURSOS SUGERIDOS</small><strong>{suggestedCourses.length}</strong><span>Catálogo inicial</span></div></article>
        <article className="surface"><span className="admin-summary-icon amber"><CircleAlert /></span><div><small>PENDÊNCIAS</small><strong>—</strong><span>Aguardando API</span></div></article>
      </section>
      <section className="admin-workspace">
        <article className="surface admin-users-panel">
          <div className="section-heading"><div><span>CONTAS DO SISTEMA</span><h2>Usuários</h2></div><button disabled>Dados da API</button></div>
          <div className="admin-table-head"><span>Usuário</span><span>Perfil</span><span>Verificação</span><span>Situação</span></div>
          <EmptyState icon={<ShieldCheck />} title="Nenhum usuário recebido" description="A lista será carregada do SQL Server pela API e ficará disponível somente para administradores." />
        </article>
        <aside className="surface admin-services-panel">
          <div className="section-heading"><div><span>OPERAÇÃO</span><h2>Serviços</h2></div></div>
          <div className="admin-service-list">
            <span><Mail /><div><strong>E-mail</strong><small>Verificação e recuperação</small></div><i>Pendente</i></span>
            <span><Phone /><div><strong>SMS</strong><small>Códigos de confirmação</small></div><i>Pendente</i></span>
            <span><Bot /><div><strong>Edu IA</strong><small>Assistência aos estudos</small></div><i>Preparada</i></span>
            <span><GraduationCap /><div><strong>Flutter</strong><small>Aplicativo móvel futuro</small></div><i>Planejado</i></span>
          </div>
        </aside>
      </section>
      <section className="admin-catalog surface">
        <div><span className="eyebrow"><BookMarked size={15} /> Catálogo do EduTrack</span><h2>Cursos sugeridos aos alunos</h2><p>Administradores poderão publicar, pausar e editar as sugestões exibidas na página Descobrir.</p></div>
        <div className="admin-catalog-preview">{suggestedCourses.slice(0, 3).map((course) => <span key={course.title}><i className={course.color}><BookOpen size={16} /></i><strong>{course.title}</strong><small>{course.category}</small></span>)}</div>
      </section>
    </>
  );
}

function UpgradePage({ plan, onInterest }: { plan: AccountStatus['plan']; onInterest: () => void }) {
  return (
    <>
      <PageHeading eyebrow="Evolua quando precisar" title="Planos EduTrack" description="Uma prévia transparente da experiência de upgrade. Pagamentos ainda não estão conectados." />
      <section className="upgrade-intro surface"><span><Crown /></span><div><small>SEM COBRANÇA NESTA ETAPA</small><h2>Teste a decisão antes de implementar o pagamento.</h2><p>O botão do plano Pro registra somente seu interesse neste navegador. Nenhum dado bancário é solicitado.</p></div></section>
      <section className="plans-grid">
        <article className="plan-card surface"><span className="plan-label">ATUAL</span><h2>Gratuito</h2><p>Organização completa para começar.</p><strong>R$ 0 <small>/ sempre</small></strong><ul><li><CheckCircle2 /> Cursos, disciplinas e tarefas</li><li><CheckCircle2 /> Cronômetro e relatórios</li><li><CheckCircle2 /> Edu IA conforme disponibilidade da API</li><li><CheckCircle2 /> Temas claro e escuro</li></ul><button className="secondary-button" disabled>Plano atual</button></article>
        <article className="plan-card featured surface"><span className="plan-label"><Sparkles size={14} /> CONCEITO FUTURO</span><h2>EduTrack Pro</h2><p>Mais automação para rotinas intensas.</p><strong>Valor a definir</strong><ul><li><CheckCircle2 /> Tudo do plano Gratuito</li><li><CheckCircle2 /> Recomendações avançadas da Edu IA</li><li><CheckCircle2 /> Sincronização entre dispositivos</li><li><CheckCircle2 /> Relatórios e metas ampliados</li></ul><button className="primary-button" onClick={onInterest} disabled={plan === 'Interesse no Pro'}>{plan === 'Interesse no Pro' ? <><CheckCircle2 size={17} /> Interesse registrado</> : <>Quero saber quando lançar <ArrowRight size={17} /></>}</button><small className="no-charge-note">Sem assinatura e sem cobrança neste protótipo.</small></article>
      </section>
    </>
  );
}


export { AppSidebar, Topbar, MobileBottomNav, PageHeading, EmptyState, Dashboard, CoursesPage, CourseDetails, DisciplinesPage, DisciplineDetails, TasksPage, ReportsPage, ProfilePage, DiscoverPage, ManagementPage, UpgradePage };

