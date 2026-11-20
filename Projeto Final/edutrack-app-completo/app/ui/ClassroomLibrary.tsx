'use client';

import { useEffect, useState } from 'react';
import { BookOpen, ExternalLink, FileText, Megaphone, Paperclip } from 'lucide-react';
import { api } from '../lib/academic-api';

type Kind = 'atividade' | 'material' | 'aviso';
type Item = { id: string; tipo: Kind; titulo: string; descricao: string; topico: string; url: string | null; publicado_em: string | null; anexos: { tipo: string; titulo: string; url: string | null }[] };
type Page = { total: number; items: Item[] };
const labels = { atividade: 'Atividade original', material: 'Material de estudo', aviso: 'Aviso' };
const icons = { atividade: FileText, material: BookOpen, aviso: Megaphone };

function ResourceLink({ url, children }: { url: string | null; children: React.ReactNode }) {
  // Defesa adicional para dados históricos. Links nunca são carregados automaticamente.
  const valid = url && /^https?:\/\//i.test(url);
  return valid ? <a href={url} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">{children}<ExternalLink size={14} aria-hidden="true" /></a> : <span>{children} · Abra pela publicação original</span>;
}

export default function ClassroomLibrary({ disciplineId }: { disciplineId: string }) {
  const [filter, setFilter] = useState('');
  const [offset, setOffset] = useState(0);
  const [page, setPage] = useState<Page | null>(null);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    api<Page>(`integrations/google/disciplines/${encodeURIComponent(disciplineId)}/content?limit=30&offset=${offset}${filter ? '&tipo=' + filter : ''}`)
      .then((value) => { if (active) { setPage(value); setError(''); } })
      .catch((problem) => { if (active) setError(problem instanceof Error ? problem.message : 'Não foi possível carregar os conteúdos.'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [disciplineId, filter, offset, reload]);
  return <section className="surface classroom-library" aria-busy={loading}>
    <div className="section-heading"><div><span>Google Classroom</span><h2>Conteúdo da turma</h2></div><BookOpen aria-hidden="true" /></div>
    <p>Materiais e avisos importados, com os links originais. Os arquivos mantêm as permissões do Google.</p>
    <label className="library-filter">Mostrar<select aria-label="Filtrar conteúdo da turma" value={filter} disabled={loading} onChange={(e) => { setFilter(e.target.value); setOffset(0); setLoading(true); }}><option value="">Todos os conteúdos</option><option value="material">Materiais de estudo</option><option value="aviso">Avisos</option><option value="atividade">Atividades e anexos originais</option></select></label>
    {loading ? <p role="status">Carregando conteúdos…</p> : error ? <div role="alert"><p>{error}</p><button className="secondary-button" onClick={() => { setLoading(true); setReload((value) => value + 1); }}>Tentar novamente</button></div> : <>
      {page?.items.length ? <div className="library-items">{page.items.map((item) => {
        const Icon = icons[item.tipo];
        return <article className="library-item" key={item.id}>
          <div className="library-item-meta"><span><Icon size={16} />{labels[item.tipo]}</span>{item.topico && <span>{item.topico}</span>}{item.publicado_em && <time dateTime={item.publicado_em}>{new Date(item.publicado_em).toLocaleDateString('pt-BR')}</time>}</div>
          <h3>{item.titulo}</h3>
          {item.descricao && <details><summary>Ler descrição</summary><p className="preserve-lines">{item.descricao}</p></details>}
          {!!item.anexos.length && <ul className="library-attachments">{item.anexos.map((attachment, index) => <li key={index}><Paperclip size={15} aria-hidden="true" /><ResourceLink url={attachment.url}>{attachment.titulo} <small>({attachment.tipo})</small></ResourceLink></li>)}</ul>}
          {item.url && <div className="library-source"><ResourceLink url={item.url}>Abrir publicação original</ResourceLink></div>}
        </article>;
      })}</div> : <p className="library-empty">Nenhum conteúdo importado neste filtro. Em Integrações, escolha a turma e use “Importar turma completa”.</p>}
      {!!page?.total && <div className="library-pagination"><span>{offset + 1}–{Math.min(offset + 30, page.total)} de {page.total} conteúdos</span><div><button className="secondary-button" disabled={offset === 0} onClick={() => { setOffset((value) => Math.max(0, value - 30)); setLoading(true); }}>Anterior</button><button className="secondary-button" disabled={offset + 30 >= page.total} onClick={() => { setOffset((value) => value + 30); setLoading(true); }}>Próxima</button></div></div>}
    </>}
  </section>;
}
