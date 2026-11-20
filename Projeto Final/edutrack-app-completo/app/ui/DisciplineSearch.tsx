'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Search, ArrowRight } from 'lucide-react';
import { api } from '../lib/academic-api';
import type { ApiDiscipline } from '../lib/academic-types';

type SearchPage = { items: ApiDiscipline[]; total: number; limit: number; offset: number };

export default function DisciplineSearch({ navigate }: { navigate: (path: string) => void }) {
  const [name, setName] = useState('');
  const [overdue, setOverdue] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<SearchPage | null>(null);
  const controller = useRef<AbortController | null>(null);
  const applied = useRef({ name: '', overdue: false });
  useEffect(() => () => controller.current?.abort(), []);

  async function search(offset = 0) {
    controller.current?.abort();
    const request = new AbortController(); controller.current = request;
    setBusy(true); setError('');
    if (!offset) { applied.current = { name, overdue }; setResult(null); }
    const query = new URLSearchParams({ q: applied.current.name, overdue: String(applied.current.overdue), limit: '20', offset: String(offset) });
    try {
      const page = await api<SearchPage>('search/disciplines?' + query, { signal: request.signal });
      if (!request.signal.aborted) setResult(page);
    } catch (cause) {
      if (!request.signal.aborted) setError(cause instanceof Error ? cause.message : 'Não foi possível buscar.');
    } finally { if (!request.signal.aborted) setBusy(false); }
  }
  function submit(event: FormEvent) { event.preventDefault(); void search(); }

  return <details className="surface academic-search"><summary><Search size={17} /> Busca avançada de disciplinas</summary>
    <form onSubmit={submit}><label>Nome da disciplina<input value={name} onChange={(event) => setName(event.target.value)} maxLength={150} placeholder="Ex.: Banco de Dados" /></label>
      <label className="academic-search-check"><input type="checkbox" checked={overdue} onChange={(event) => setOverdue(event.target.checked)} />Incluir também disciplinas com tarefas atrasadas</label>
      <p>Com os dois filtros, aparecem as disciplinas com esse nome <strong>ou</strong> com atividades pendentes cujo prazo já passou.</p>
      <button className="secondary-button" disabled={busy} type="submit"><Search size={16} />{busy ? 'Buscando…' : 'Buscar disciplinas'}</button>
    </form>
    {error && <p role="alert">{error}</p>}
    {result && <div aria-live="polite"><p>{result.total} disciplina(s) encontrada(s).</p>
      <ul>{result.items.map((item) => <li key={item.id}><button type="button" className="text-link" onClick={() => navigate('/disciplinas/' + item.id)}>{item.nome}<ArrowRight size={15} /></button></li>)}</ul>
      <div className="academic-search-pages">{result.offset > 0 && <button type="button" className="secondary-button" disabled={busy} onClick={() => void search(Math.max(0, result.offset - result.limit))}>Anterior</button>}
      {result.offset + result.items.length < result.total && <button type="button" className="secondary-button" disabled={busy} onClick={() => void search(result.offset + result.limit)}>Próxima página</button>}</div>
    </div>}
  </details>;
}
