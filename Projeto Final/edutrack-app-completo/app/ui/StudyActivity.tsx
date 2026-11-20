'use client';

import { useEffect, useId, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent } from 'react';
import { ArrowRight, CalendarDays, Flame } from 'lucide-react';
import { localDay, studyCalendar, studyCalendarTarget, type StudyDay, type StudySession } from '../lib/study-game';

const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
const dateFormatter = new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' });
const dateLabel = (key: string) => dateFormatter.format(new Date(key + 'T12:00:00'));
const timeLabel = (minutes: number) => minutes < 60 ? `${minutes} min` : `${Math.floor(minutes / 60)}h${minutes % 60 ? ` ${minutes % 60}min` : ''}`;
const dayLabel = (day: StudyDay) => `${dateLabel(day.key)}: ${day.minutes ? `${timeLabel(day.minutes)} de estudo em ${day.sessions} ${day.sessions === 1 ? 'sessão' : 'sessões'}` : 'nenhuma sessão concluída'}`;

export default function StudyActivity({ sessions, navigate }: { sessions: StudySession[]; navigate: (path: string) => void }) {
  const id = useId();
  const [months, setMonths] = useState<3 | 6 | 12>(12);
  const [now, setNow] = useState(() => new Date());
  const [selected, setSelected] = useState('');
  const [hovered, setHovered] = useState<string | null>(null);
  const scroll = useRef<HTMLDivElement>(null);
  const buttons = useRef(new Map<string, HTMLButtonElement>());
  const calendar = useMemo(() => studyCalendar(sessions, months, now), [sessions, months, now]);
  // Os rótulos não precisam ser formatados novamente ao passar o mouse ou usar as setas.
  const labels = useMemo(() => new Map(calendar.days.map((day) => [day.key, dayLabel(day)])), [calendar]);
  const selectedDay = calendar.days.find((day) => day.key === selected) ?? calendar.days.at(-1)!;
  const detail = calendar.days.find((day) => day.key === hovered) ?? selectedDay;
  const today = localDay(now);

  useEffect(() => {
    // Atualiza a virada do dia e o retorno à aba sem consultar novamente o banco.
    const refresh = () => { if (document.visibilityState === 'visible') setNow(new Date()); };
    const timer = window.setInterval(refresh, 60_000);
    document.addEventListener('visibilitychange', refresh);
    return () => { window.clearInterval(timer); document.removeEventListener('visibilitychange', refresh); };
  }, []);
  useEffect(() => {
    const viewport = scroll.current;
    if (!viewport) return;
    viewport.scrollLeft = viewport.scrollWidth;
    let width = viewport.clientWidth;
    let atEnd = true;
    const rememberPosition = () => { atEnd = viewport.scrollWidth - viewport.clientWidth - viewport.scrollLeft <= 2; };
    // Mantém os dias recentes visíveis ao recolher o menu ou girar o celular.
    // Se o aluno já explora o passado, a posição escolhida é preservada.
    const observer = new ResizeObserver(() => {
      if (viewport.clientWidth !== width && atEnd) viewport.scrollLeft = viewport.scrollWidth;
      width = viewport.clientWidth;
    });
    viewport.addEventListener('scroll', rememberPosition, { passive: true });
    observer.observe(viewport);
    return () => { observer.disconnect(); viewport.removeEventListener('scroll', rememberPosition); };
  }, [months, today]);

  function move(event: KeyboardEvent<HTMLButtonElement>, day: StudyDay) {
    const next = studyCalendarTarget(event.key, calendar.days.findIndex((item) => item.key === day.key), calendar.days.length);
    if (next === null) return;
    event.preventDefault();
    const target = calendar.days[next];
    setSelected(target.key);
    buttons.current.get(target.key)?.focus();
  }

  return <section className="study-activity" aria-labelledby={`${id}-title`}>
    <div className="study-activity-heading">
      <div><span className="activity-eyebrow"><CalendarDays size={15} aria-hidden="true" /> Seu ritmo de estudo</span>
        <h2 id={`${id}-title`}>{calendar.activeDays} {calendar.activeDays === 1 ? 'dia de estudo' : 'dias de estudo'} <span>nos últimos {months} meses</span></h2>
      </div>
      <label className="activity-period"><span className="activity-sr-only">Período do calendário</span>
        <select value={months} onChange={(event) => { setMonths(Number(event.target.value) as 3 | 6 | 12); setHovered(null); }}>
          <option value={12}>Últimos 12 meses</option><option value={6}>Últimos 6 meses</option><option value={3}>Últimos 3 meses</option>
        </select>
      </label>
    </div>
    <div className="activity-chart">
      <div className="activity-weekdays" aria-hidden="true"><span>Seg</span><span>Qua</span><span>Sex</span></div>
      <div className="activity-scroll" ref={scroll}>
        <div className="activity-calendar" style={{ '--activity-weeks': calendar.weeks.length } as CSSProperties}>
          <div className="activity-months" aria-hidden="true">{calendar.weeks.map((week, index) => {
            const first = week.find((day) => day && (index === 0 || day.key.endsWith('-01')));
            const nextMonthTooClose = index === 0 && calendar.weeks[1]?.some((day) => day?.key.endsWith('-01'));
            return <span key={index}>{first && !nextMonthTooClose ? monthNames[Number(first.key.slice(5, 7)) - 1] : ''}</span>;
          })}</div>
          <div className="activity-weeks" role="group" aria-label="Calendário de estudo por dia" aria-describedby={`${id}-help`} onMouseLeave={() => setHovered(null)}>
            {calendar.weeks.map((week, index) => <div className="activity-week" key={index}>{week.map((day, row) => day ?
              <button key={day.key} type="button" className={`activity-day activity-level-${day.level}${day.today ? ' is-today' : ''}`}
                ref={(element) => { if (element) buttons.current.set(day.key, element); else buttons.current.delete(day.key); }}
                tabIndex={selectedDay.key === day.key ? 0 : -1} aria-label={labels.get(day.key)} aria-pressed={selectedDay.key === day.key}
                title={labels.get(day.key)} onMouseEnter={() => setHovered(day.key)} onFocus={() => { setSelected(day.key); setHovered(null); }}
                onClick={() => { setSelected(day.key); setHovered(null); }} onKeyDown={(event) => move(event, day)} />
              : <span className="activity-day activity-padding" key={`empty-${row}`} aria-hidden="true" />)}</div>)}
          </div>
        </div>
      </div>
    </div>
    <div className="activity-chart-footer">
      <p id={`${id}-help`}>Cada quadrado é um dia. <span className="activity-desktop-help">Passe o mouse ou selecione para ver os detalhes.</span><span className="activity-mobile-help">Deslize e toque para explorar.</span><span className="activity-sr-only"> Use as setas para navegar, Home para o início e End para hoje.</span></p>
      <div className="activity-legend" aria-label="Intensidade: 0, de 1 a 24, de 25 a 49, de 50 a 99 e 100 minutos ou mais"><span>Menos</span>{[0, 1, 2, 3, 4].map((level) => <i className={`activity-level-${level}`} key={level} aria-hidden="true" />)}<span>Mais</span></div>
    </div>
    <div className="activity-bottom">
      <div className="activity-detail" role="status" aria-live="polite" aria-atomic="true"><span className={`activity-detail-dot activity-level-${detail.level}`} aria-hidden="true" /><p><strong>{detail.today ? 'Hoje' : dateLabel(detail.key)}</strong><span>{detail.minutes ? `${timeLabel(detail.minutes)} de estudo · ${detail.sessions} ${detail.sessions === 1 ? 'sessão concluída' : 'sessões concluídas'}` : 'Nenhuma sessão concluída. Comece um bloco de foco.'}</span></p></div>
      <div className="activity-summary"><p><strong>{timeLabel(calendar.totalMinutes)}</strong> de foco <span>·</span> <strong>{calendar.totalSessions}</strong> {calendar.totalSessions === 1 ? 'sessão no período' : 'sessões no período'}</p><button type="button" onClick={() => navigate('/ofensiva')}><Flame size={15} aria-hidden="true" /> {calendar.streak} {calendar.streak === 1 ? 'dia seguido' : 'dias seguidos'} <ArrowRight size={14} aria-hidden="true" /></button></div>
    </div>
  </section>;
}
