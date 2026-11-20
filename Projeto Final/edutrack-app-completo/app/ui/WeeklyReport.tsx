'use client';

import { useMemo, useState } from 'react';
import { ArrowLeft, ArrowRight, BarChart3, Download, Clock3, CalendarDays } from 'lucide-react';
import { weeklyReport, reportCsv } from '../lib/weekly-report';
import type { StudySession } from '../lib/study-game';
import type { Discipline } from '../lib/academic-types';
import { progressReportPdf } from '../lib/academic-api';

export default function WeeklyReport({ disciplines, sessions }: { disciplines: Discipline[]; sessions: StudySession[] }) {
  const [offset, setOffset] = useState(0);
  const [pdfBusy, setPdfBusy] = useState(false);
  const [pdfError, setPdfError] = useState('');
  const report = useMemo(() => weeklyReport(sessions, offset), [sessions, offset]);
  const lastDay = new Date(report.end); lastDay.setDate(lastDay.getDate() - 1);
  const fmt = (date: Date) => date.toLocaleDateString('pt-BR');
  const maximum = Math.max(...report.days.map((day) => day.minutes), 1);
  function download() {
    const url = URL.createObjectURL(new Blob([reportCsv(report)], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a'); link.href = url; link.download = `edutrack-semana-${report.days[0].key}.csv`; link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function downloadPdf() {
    setPdfBusy(true); setPdfError('');
    try {
      const url = URL.createObjectURL(await progressReportPdf());
      const link = document.createElement('a'); link.href = url; link.download = 'edutrack-progresso.pdf'; link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) { setPdfError(error instanceof Error ? error.message : 'Falha ao gerar relatório.'); }
    finally { setPdfBusy(false); }
  }
  return <>
    <header className="page-heading"><div><span className="eyebrow">Evolução</span><h1>Relatórios</h1><p>Veja o que seu tempo de estudo constrói, uma semana de cada vez.</p></div><button className="secondary-button" onClick={download}><Download size={17} /> Baixar CSV</button></header>
    <div className="report-period"><div><strong>Seu progresso em PDF</strong><span>Disciplinas e tarefas acumuladas · todas as datas</span></div><button className="primary-button" type="button" disabled={pdfBusy} onClick={() => void downloadPdf()}><Download size={17} />{pdfBusy ? 'Gerando PDF…' : 'Baixar PDF de progresso'}</button></div>
    {pdfError && <p role="alert">{pdfError}</p>}
    <div className="report-period"><button className="icon-button" aria-label="Semana anterior" onClick={() => setOffset(offset - 1)}><ArrowLeft size={18} /></button><div aria-live="polite"><strong>{offset === 0 ? 'Esta semana' : offset === -1 ? 'Semana passada' : 'Semana selecionada'}</strong><span>{fmt(report.start)} — {fmt(lastDay)}</span></div><button className="icon-button" aria-label="Próxima semana" disabled={offset === 0} onClick={() => setOffset(offset + 1)}><ArrowRight size={18} /></button>{offset !== 0 && <button className="text-link" onClick={() => setOffset(0)}>Voltar para hoje</button>}</div>
    <section className="report-statistics" aria-label="Resumo da semana"><article className="surface"><Clock3 size={21} /><span>Tempo estudado</span><strong>{Math.floor(report.minutes / 60)}h {report.minutes % 60}min</strong></article><article className="surface"><BarChart3 size={21} /><span>Sessões concluídas</span><strong>{report.completed.length}</strong></article><article className="surface"><CalendarDays size={21} /><span>Dias de estudo</span><strong>{report.activeDays} de 7</strong></article></section>
    <section className="surface report-main"><div className="section-heading"><div><span>Seu ritmo</span><h2>Tempo de estudo por dia</h2></div></div>
      {report.completed.length ? <div className="bar-chart" role="img" aria-label={report.days.map((day) => `${day.label}: ${day.minutes} minutos`).join('; ')}>{report.days.map((day) => <div key={day.key}><span style={{ height: `${day.minutes / maximum * 100}%` }} title={`${day.minutes} minutos · ${day.sessions} sessões`} /><small>{day.label}</small></div>)}</div> : <div className="report-empty"><BarChart3 size={32} /><h3>Nenhuma sessão nesta semana</h3><p>Conclua um bloco no cronômetro ou consulte uma semana anterior.</p></div>}
      <details className="report-data"><summary>Ver os números por dia</summary><table><thead><tr><th scope="col">Data</th><th scope="col">Minutos</th><th scope="col">Sessões</th></tr></thead><tbody>{report.days.map((day) => <tr key={day.key}><td>{fmt(new Date(day.key + 'T12:00:00'))} · {day.label}</td><td>{day.minutes}</td><td>{day.sessions}</td></tr>)}</tbody></table></details>
    </section>
    <section className="surface comparison"><div className="section-heading"><div><span>Progresso acumulado · todas as datas</span><h2>Conclusão por disciplina</h2></div></div>{disciplines.length ? disciplines.map((item) => <div className="comparison-row" key={item.id}><span>{item.title}</span><div className="progress-track"><i className={item.color} style={{ width: `${item.progress}%` }} /></div><strong>{item.progress}%</strong></div>) : <p>Adicione disciplinas e conclua tarefas para acompanhar seu progresso.</p>}</section>
  </>;
}
