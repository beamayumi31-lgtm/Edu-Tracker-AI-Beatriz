import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { GraduationCap, LayoutDashboard, BookOpen, CheckCircle2, Clock3, Flame, BarChart3, Bot } from 'lucide-react';
import { Dashboard } from '../../app/ui/EduTrackViews';
import { ThemeToggle } from '../../app/ui/Brand';
import type { StudySession } from '../../app/lib/study-game';
import '../../app/globals.css';
import '../../app/study-game.css';
import '../../app/connected.css';
import '../../app/study-activity.css';

const history: StudySession[] = Array.from({ length: 110 }, (_, index) => {
  const date = new Date();
  date.setHours(12, 0, 0, 0);
  date.setDate(date.getDate() - index - 1);
  return { id: `fixture-${index}`, minutes: [15, 25, 50, 100, 0, 45, 0][index % 7], completedAt: date.toISOString() };
}).filter((session) => session.minutes > 0);
const nav = [
  ['Dashboard', LayoutDashboard], ['Cursos', GraduationCap], ['Disciplinas', BookOpen],
  ['Tarefas', CheckCircle2], ['Cronômetro', Clock3], ['Ofensiva', Flame],
  ['Relatórios', BarChart3], ['Edu IA', Bot],
] as const;

function VisualFixture() {
  const [populated, setPopulated] = useState(false);
  const [hidden, setHidden] = useState(false);
  const [destination, setDestination] = useState('');
  return <>
    <div style={{ padding: '10px 18px', background: 'var(--surface)', borderBottom: '1px solid var(--border)', fontSize: 12, display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
      <strong>Teste visual isolado · dados fictícios · sem API</strong>
      <label><input type="checkbox" checked={populated} onChange={(event) => setPopulated(event.target.checked)} /> Mostrar histórico de teste</label>
      <button type="button" className="secondary-button compact" onClick={() => setHidden(!hidden)}>Alternar menu de teste</button>
      <ThemeToggle compact />
      <span role="status">{destination ? `Destino solicitado: ${destination}` : 'Nenhuma navegação solicitada'}</span>
    </div>
    <div className={`app-shell${hidden ? ' sidebar-hidden' : ''}`}>
      <aside className="app-sidebar">
        <div className="brand"><span className="brand-mark"><GraduationCap /></span>EduTrack</div>
        <nav>{nav.map(([label, Icon]) => <button type="button" key={label} className={label === 'Dashboard' ? 'active' : ''} onClick={() => setDestination(label)}><Icon size={19} />{label}</button>)}</nav>
      </aside>
      <main className="app-content"><div className="content-wrap">
        <Dashboard tasks={[]} courses={populated ? [{ id: 'fixture-course', title: 'Curso de teste visual', source: 'Fixture local', type: 'Curso livre', period: '', goal: '', status: 'Em andamento', progress: 0, color: 'violet' }] : []}
          sessions={populated ? history : []} profile={{ name: '', area: '', institution: '', preferences: '', weeklyGoal: '', focusTechnique: '', reminders: '' }} navigate={setDestination} />
      </div></main>
    </div>
  </>;
}

createRoot(document.getElementById('root')!).render(<VisualFixture />);
