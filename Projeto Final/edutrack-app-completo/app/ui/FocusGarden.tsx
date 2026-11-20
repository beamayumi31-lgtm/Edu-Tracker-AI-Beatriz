'use client';

import { useRef, useState, type Dispatch, type SetStateAction, type CSSProperties } from 'react';
import { ArrowLeft, ArrowRight, Check, Coffee, Flame, Leaf, Pause, Play, Sprout, TreeDeciduous, TreePine, Trophy, X } from 'lucide-react';
import { remainingSeconds, studySummary, type FocusRun, type StudySession } from '../lib/study-game';
import type { StudyTask } from './EduTrackApp';

export default function FocusGarden({ tasks, sessions, run, seconds, setRun, navigate, ready, requireTask = false }: {
  tasks: StudyTask[]; sessions: StudySession[]; run: FocusRun | null; seconds: number;
  setRun: Dispatch<SetStateAction<FocusRun | null>>; navigate: (path: string) => void; ready: boolean; requireTask?: boolean;
}) {
  const [minutes, setMinutes] = useState(25);
  const [taskId, setTaskId] = useState('');
  const [mode, setMode] = useState<'focus' | 'break'>('focus');
  const confirm = useRef<HTMLDialogElement>(null);
  const summary = studySummary(sessions);
  const activeMode = run?.mode ?? mode;
  const duration = run?.minutes ?? (mode === 'break' ? 5 : minutes);
  const remaining = run ? seconds : duration * 60;
  const progress = run ? Math.min(100, Math.max(0, (1 - remaining / (run.minutes * 60)) * 100)) : 0;
  const growing = Boolean(run?.endsAt);
  const Stage = activeMode === 'break' ? Coffee : progress < 35 ? Sprout : progress < 70 ? TreePine : TreeDeciduous;
  const stageLabel = activeMode === 'break' ? 'Tempo de respirar' : !run ? 'Uma semente, um novo começo' : progress < 35 ? 'Sua semente está brotando' : progress < 70 ? 'Criando raízes, ganhando foco' : 'Sua árvore está quase pronta!';
  const trees = summary.completed.length;
  const nextGoal = (Math.floor(trees / 5) + 1) * 5;
  const selectedTask = tasks.find((task) => task.id === (run?.taskId ?? taskId));

  function startOrToggle() {
    if (!ready) return;
    if (!run && requireTask && mode === 'focus' && !tasks.some((task) => task.id === taskId && !['Concluída', 'Cancelada'].includes(task.status))) return;
    if (run) {
      const left = remainingSeconds(run);
      if (left <= 0) return;
      setRun({ ...run, remaining: left, endsAt: run.endsAt === null ? Date.now() + left * 1000 : null });
    } else {
      setRun({ id: 'focus-' + crypto.randomUUID(), mode, minutes: duration, remaining: duration * 60, endsAt: Date.now() + duration * 60000, taskId: taskId || undefined });
    }
  }

  return <div className="study-game">
    <header className="game-heading"><div><button className="game-back" onClick={() => navigate('/dashboard')}><ArrowLeft size={16} /> Dashboard</button><span className="eyebrow">Cronômetro · Modo foco</span><h1>Sua floresta de foco</h1><p>Um bloco de estudo. Uma árvore a mais.</p></div><button className="game-streak-link" onClick={() => navigate('/ofensiva')}><Flame /><strong>{summary.streak}</strong><span>dias de ofensiva</span><ArrowRight size={17} /></button></header>
    <div className="garden-layout">
      <section className={'garden-play surface ' + (growing ? 'is-growing' : '')} aria-label="Sessão de foco">
        <div className="garden-mode" aria-label="Tipo de sessão">{(['focus', 'break'] as const).map((item) => <button key={item} disabled={Boolean(run)} aria-pressed={activeMode === item} className={activeMode === item ? 'active' : ''} onClick={() => setMode(item)}>{item === 'focus' ? <Leaf size={17} /> : <Coffee size={17} />}{item === 'focus' ? 'Plantar uma árvore' : 'Fazer uma pausa'}</button>)}</div>
        <div className="garden-stage" style={{ '--growth': progress + '%' } as CSSProperties}>
          <div className="growth-ring" role="progressbar" aria-label="Crescimento da árvore" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(progress)}><Stage aria-hidden="true" strokeWidth={1.45} /></div>
          <span className="garden-stage-label">{run && !growing ? 'Crescimento pausado' : stageLabel}</span>
          <strong className="garden-clock" role="timer" aria-label="Tempo restante">{String(Math.floor(remaining / 60)).padStart(2, '0')}<span>:</span>{String(remaining % 60).padStart(2, '0')}</strong>
          <p>{activeMode === 'focus' ? (selectedTask?.title || 'Seu momento de concentração') : 'Relaxe um pouco. Sua floresta espera por você.'}</p>
        </div>
        {activeMode === 'focus' && <><div className="garden-durations" aria-label="Duração da sessão">{[15, 25, 45, 60].map((value) => <button disabled={Boolean(run)} aria-pressed={duration === value} className={duration === value ? 'active' : ''} key={value} onClick={() => setMinutes(value)}>{value}<span> min</span></button>)}</div><label className="garden-task">O que você vai estudar?<select value={run?.taskId ?? taskId} disabled={Boolean(run)} onChange={(event) => setTaskId(event.target.value)}><option value="">{requireTask ? 'Selecione uma tarefa' : 'Foco livre'}</option>{tasks.filter((task) => !['Concluída', 'Cancelada'].includes(task.status) || task.id === run?.taskId).map((task) => <option key={task.id} value={task.id}>{task.title}</option>)}</select></label></>}
        {requireTask && activeMode === 'focus' && !run && !taskId && <p className="game-hint">Selecione uma tarefa para vincular e salvar seu tempo de estudo na conta.</p>}
        <div className="garden-actions"><button className="garden-start" disabled={!ready || Boolean(run && seconds === 0) || (!run && requireTask && activeMode === 'focus' && !taskId)} onClick={startOrToggle}>{growing ? <Pause size={20} /> : <Play size={20} />}{growing ? 'Pausar foco' : run ? 'Continuar sessão' : activeMode === 'focus' ? 'Plantar e focar' : 'Iniciar pausa'}</button>{run && <button className="garden-abandon" onClick={() => confirm.current?.showModal()}>Encerrar sessão</button>}</div>
        <p className="game-hint">{activeMode === 'focus' ? 'Complete o tempo para ganhar uma árvore. Pausar preserva seu progresso.' : 'As pausas não contam como tempo estudado nem aumentam a ofensiva.'}</p>
      </section>
      <aside className="garden-side">
        <section className="surface forest-collection"><header><div><span className="eyebrow">Cada sessão importa</span><h2>Minha floresta</h2></div><span className="forest-count"><TreeDeciduous size={19} />{trees}</span></header>
          {trees ? <><div className="forest-tiles">{summary.completed.slice(-12).map((session, index) => { const Tree = index % 2 ? TreePine : TreeDeciduous; return <div key={session.id} title={new Date(session.completedAt).toLocaleDateString('pt-BR') + ' · ' + session.minutes + ' min'}><Tree strokeWidth={1.6} /><span>{session.minutes} min</span></div>; })}</div><p>{trees > 12 ? `Mostrando as 12 árvores mais recentes de ${trees}.` : `${trees} ${trees === 1 ? 'sessão concluída, uma árvore conquistada.' : 'sessões concluídas, uma conquista de cada vez.'}`}</p></> : <div className="forest-empty"><Sprout size={42} strokeWidth={1.5} /><h3>Seu primeiro broto vem aí</h3><p>Conclua uma sessão de foco para começar sua coleção.</p></div>}
          <div className="forest-milestone"><Trophy size={20} /><div><strong>Próxima conquista: {nextGoal} árvores</strong><span>Faltam {nextGoal - trees} sessões completas.</span></div></div><progress aria-label="Progresso da próxima conquista" value={trees % 5} max={5} />
        </section>
        <section className="surface garden-today"><div><span>Estudo hoje</span><strong>{summary.todayMinutes}<small> min</small></strong></div><div><span>Tempo total</span><strong>{summary.totalMinutes}<small> min</small></strong></div></section>
        <section className="garden-note"><Check size={20} /><p>Você pode consultar suas tarefas e voltar: o cronômetro continua. Só uma sessão concluída aumenta sua ofensiva.</p></section>
      </aside>
    </div>
    <dialog ref={confirm} className="game-confirm" aria-labelledby="end-focus-title"><button className="icon-button" aria-label="Fechar confirmação" onClick={() => confirm.current?.close()}><X /></button><Sprout size={40} /><h2 id="end-focus-title">Encerrar esta sessão?</h2><p>{activeMode === 'focus' ? 'Esta árvore ainda está crescendo. Se encerrar agora, não serão registrados minutos nem uma nova árvore. Suas conquistas anteriores continuam salvas.' : 'A pausa será encerrada. Você poderá começar um novo foco quando quiser.'}</p><div><button className="secondary-button" autoFocus onClick={() => confirm.current?.close()}>Continuar sessão</button><button className="primary-button" onClick={() => { setRun(null); confirm.current?.close(); }}>Sim, encerrar</button></div></dialog>
  </div>;
}
