'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { ArrowUp, BookOpen, CalendarDays, Check, Copy, Download, MessageSquare, Plus, ShieldCheck, Sparkles, Square } from 'lucide-react';
import { api, localDateInput } from '../lib/academic-api';
import type { StudyPlan } from '../lib/academic-types';
import { studyPlanText } from '../lib/study-plan-export';
import { chatContext, conversationText, type ChatMessage } from '../lib/edu-chat';
import EduResponse from './EduResponse';
import './edu-chat.css';

const suggestions = [
  { title: 'Entender um conceito', detail: 'Do complicado ao simples', prompt: 'Explique normalização de banco de dados com uma analogia simples e um exemplo em SQL.' },
  { title: 'Praticar com exercícios', detail: 'Aprender fazendo', prompt: 'Crie 3 exercícios de lógica de programação. Mostre um por vez e espere minha resposta antes de explicar.' },
  { title: 'Revisar para a prova', detail: 'Uma pergunta por vez', prompt: 'Faça uma revisão de SQL com perguntas, uma de cada vez. Comece pelo básico e ajuste a dificuldade pelas minhas respostas.' },
];
function download(text: string, filename: string) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }));
  const link = document.createElement('a'); link.href = url; link.download = filename;
  document.body.appendChild(link); link.click(); link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export default function ConnectedEduAI() {
  const [tab, setTab] = useState<'chat' | 'plan'>('chat');
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [provider, setProvider] = useState('');
  const [contextAllowed, setContextAllowed] = useState(false);
  const [adult, setAdult] = useState(false);
  const [consent, setConsent] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [busy, setBusy] = useState<'chat' | 'plan' | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState('');
  const [pendingQuestion, setPendingQuestion] = useState('');
  const [copied, setCopied] = useState<number | null>(null);
  const [statusAttempt, setStatusAttempt] = useState(0);
  const request = useRef<AbortController | null>(null);
  const bottom = useRef<HTMLDivElement | null>(null);
  const composer = useRef<HTMLTextAreaElement | null>(null);
  const eligible = provider !== 'Gemini' || adult;
  const ready = configured === true && consent && eligible;
  useEffect(() => {
    let active = true;
    api<{ configured: boolean; provider: string; academic_context_allowed: boolean }>('edu-ia/status')
      .then(result => { if (active) { setConfigured(result.configured); setProvider(result.provider === 'gemini' ? 'Gemini' : 'OpenAI'); setContextAllowed(result.academic_context_allowed); } })
      .catch(cause => { if (active) { setConfigured(false); setError(cause instanceof Error ? cause.message : 'Não foi possível verificar o serviço.'); } });
    return () => { active = false; };
  }, [statusAttempt]);
  useEffect(() => () => { request.current?.abort(); }, []);
  useEffect(() => { if (messages.length || pendingQuestion) bottom.current?.scrollIntoView({ block: 'nearest' }); }, [messages, pendingQuestion]);
  async function makePlan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (request.current) return;
    const data = new FormData(event.currentTarget);
    const controller = new AbortController(); request.current = controller;
    setBusy('plan'); setError(''); setNotice('');
    try {
      const result = await api<StudyPlan>('edu-ia/study-plan', { method: 'POST', signal: controller.signal, body: JSON.stringify({ data_inicio: data.get('data_inicio'), dias: Number(data.get('dias')), minutos_por_dia: Number(data.get('minutos_por_dia')), objetivo: data.get('objetivo'), usar_ia: useAI && ready, enviar_dados_ia: useAI && ready, maior_de_idade: adult }) });
      if (!controller.signal.aborted) setPlan(result);
    } catch (cause) { if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : 'Não foi possível gerar o plano.'); }
    finally { if (request.current === controller) { request.current = null; setBusy(null); } }
  }
  async function send(event?: FormEvent) {
    event?.preventDefault();
    const question = draft.trim();
    if (!question || !ready || request.current || question.length > 2000) return;
    const pending: ChatMessage[] = [...messages, { role: 'user', text: question }];
    const controller = new AbortController(); request.current = controller;
    setBusy('chat'); setError(''); setNotice(''); setPendingQuestion(question);
    try {
      const result = await api<{ reply: string; plan: StudyPlan | null }>('edu-ia/chat', { method: 'POST', signal: controller.signal, body: JSON.stringify({ messages: chatContext(pending), enviar_dados_ia: true, maior_de_idade: adult }) });
      if (!controller.signal.aborted) { setMessages([...pending, { role: 'assistant', text: result.reply }]); setDraft(''); if (result.plan) { setPlan(result.plan); setNotice('Plano pronto. Abra Planejar estudos para revisar e baixar.'); } }
    } catch (cause) { if (!controller.signal.aborted) setError((cause instanceof Error ? cause.message : 'Não foi possível enviar.') + ' Sua pergunta foi mantida para tentar novamente.'); }
    finally { if (request.current === controller) { request.current = null; setBusy(null); setPendingQuestion(''); } }
  }
  function cancel() {
    request.current?.abort(); request.current = null; setBusy(null); setPendingQuestion('');
    setNotice('Espera interrompida. A pergunta foi mantida. Se o provedor já recebeu a solicitação, ele ainda pode processá-la.');
  }
  function revoke() { request.current?.abort(); request.current = null; setBusy(null); setPendingQuestion(''); setUseAI(false); setMessages([]); setConsent(false); }
  async function copy(text: string, index: number) {
    try { await navigator.clipboard.writeText(text); setCopied(index); setNotice('Resposta copiada.'); }
    catch { setNotice('Não foi possível copiar automaticamente. Selecione o texto ou baixe a conversa.'); }
  }
  return <div className="connected-ai edu-workspace">
    <header className="edu-topbar"><div className="edu-identity"><span className="edu-mark"><Sparkles size={23} /></span><div><h1>Edu IA</h1><span>{configured === null ? 'Verificando disponibilidade' : configured ? `Conversa com ${provider}` : 'Chat aguardando ativação'}</span></div></div><button className="secondary-button" disabled={!!busy || !messages.length} onClick={() => { setMessages([]); setCopied(null); setError(''); setNotice('Nova conversa. O histórico anterior foi removido desta tela.'); }}><Plus size={16} /> Nova conversa</button></header>
    <div className="edu-mode-switch" role="group" aria-label="Modo de estudo"><button aria-pressed={tab === 'chat'} onClick={() => setTab('chat')}><MessageSquare size={16} /> Conversar</button><button aria-pressed={tab === 'plan'} onClick={() => setTab('plan')}><CalendarDays size={16} /> Planejar estudos <span>Local</span></button></div>
    {error && <div className="form-error edu-feedback" role="alert">{error}</div>}
    {notice && <p className="edu-feedback" role="status">{notice}</p>}
    {tab === 'chat' ? <section className="edu-conversation" aria-label="Conversa de estudos">
      {!messages.length && !pendingQuestion && <div className="edu-welcome"><span className="edu-orbit"><Sparkles size={35} /></span><span className="eyebrow">UM ESPAÇO PARA APRENDER</span><h2>O que vamos<br /><em>entender hoje?</em></h2><p>Explore uma ideia, pratique ou revise no seu ritmo.</p><div className="edu-starters">{suggestions.map(item => <button key={item.title} disabled={!!busy} onClick={() => { setDraft(item.prompt); composer.current?.focus(); }}><BookOpen size={19} /><strong>{item.title}</strong><span>{item.detail}</span></button>)}</div></div>}
      {configured === false && <div className="edu-availability"><ShieldCheck size={21} /><div><strong>Uma boa conversa precisa de um modelo conectado.</strong><p>A interface está pronta, mas a IA generativa ainda não está ativa. Você pode preparar sua pergunta ou usar o planejador local, que já funciona com suas tarefas. Não simulamos respostas de IA.</p><button onClick={() => setTab('plan')}>Criar um plano local →</button> <button onClick={() => { setError(''); setConfigured(null); setStatusAttempt(v => v + 1); }}>Verificar novamente</button></div></div>}
      {configured && <details className="edu-consent" open={!consent || !eligible}><summary><ShieldCheck size={16} /> Privacidade e autorização {ready ? '· autorizado nesta tela' : '· antes de conversar'}</summary><p>Suas mensagens{contextAllowed ? ' e o contexto acadêmico cadastrado manualmente' : ''} serão enviados ao {provider}. Conteúdos do Classroom não são enviados automaticamente. Não cole dados pessoais nem materiais privados.</p>{provider === 'Gemini' && <label className="checkbox-line"><input type="checkbox" checked={adult} disabled={!!busy} onChange={e => { setAdult(e.target.checked); if (!e.target.checked) revoke(); }} /> Tenho 18 anos ou mais.</label>}<label className="checkbox-line"><input type="checkbox" checked={consent} disabled={!!busy} onChange={e => { if (e.target.checked) setConsent(true); else revoke(); }} /> Autorizo este envio para a conversa atual.</label>{provider === 'Gemini' && <small>Serviços gratuitos do Gemini podem usar mensagens para melhorar seus produtos.</small>}</details>}
      <div className="edu-transcript" role="log" aria-live="polite" aria-label="Mensagens da conversa">{messages.map((message, index) => <article className={`edu-message edu-message-${message.role}`} key={index}><span className="edu-author">{message.role === 'user' ? 'Você' : <><Sparkles size={16} /> Edu IA</>}</span>{message.role === 'assistant' ? <EduResponse text={message.text} /> : <p className="preserve-lines">{message.text}</p>}{message.role === 'assistant' && <button className="edu-copy" onClick={() => copy(message.text, index)}>{copied === index ? <Check size={14} /> : <Copy size={14} />}{copied === index ? 'Copiado' : 'Copiar resposta'}</button>}</article>)}{pendingQuestion && <><article className="edu-message edu-message-user"><span className="edu-author">Você</span><p className="preserve-lines">{pendingQuestion}</p></article><p className="edu-thinking" role="status"><Sparkles size={18} /> Preparando uma resposta…</p></>}<div ref={bottom} /></div>
      <form className="edu-composer" onSubmit={send}><label htmlFor="edu-message">Sua pergunta</label><textarea ref={composer} id="edu-message" maxLength={2000} rows={3} value={draft} onChange={e => setDraft(e.target.value)} disabled={!!busy} placeholder="Pergunte, explore uma ideia ou escolha uma sugestão…" onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void send(); } }} /><div className="edu-composer-bottom"><span>{draft.length}/2000 <span className="edu-keyboard">· Enter envia · Shift+Enter quebra linha</span></span>{busy === 'chat' ? <button type="button" className="edu-send" onClick={cancel} aria-label="Interromper espera"><Square size={17} /></button> : <button className="edu-send" disabled={!ready || !!busy || !draft.trim()} aria-label="Enviar pergunta"><ArrowUp size={22} /></button>}</div></form>
      <footer className="edu-chat-footer"><p>{!configured ? 'Envio indisponível até a ativação do modelo.' : !ready ? 'Autorize o envio acima para conversar.' : 'A IA pode errar. Confira as respostas com seus materiais.'} Histórico apenas nesta tela; trechos das últimas 4 trocas acompanham a próxima pergunta.</p>{!!messages.length && <button className="edu-copy" onClick={() => download(conversationText(messages), 'edutrack-conversa.txt')}><Download size={15} /> Baixar conversa</button>}</footer>
    </section> : <section className="edu-planner"><header><span className="eyebrow">{useAI && ready ? `PLANEJADOR COM ${provider.toUpperCase()}` : 'PLANEJADOR LOCAL · SEM IA EXTERNA'}</span><h2>Faça o tempo trabalhar a seu favor.</h2><p>Distribua suas tarefas em blocos possíveis. Seus dados ficam no EduTrack quando você usa as regras locais.</p></header><section className="surface connected-plan"><form onSubmit={makePlan}><fieldset className="connected-fields" disabled={!!busy}><div className="connected-grid"><label>Começar em<input name="data_inicio" type="date" required defaultValue={localDateInput(new Date())} /></label><label>Período (dias)<input name="dias" type="number" min={1} max={14} required defaultValue={7} /></label><label>Minutos por dia<input name="minutos_por_dia" type="number" min={15} max={240} required defaultValue={60} /></label></div><label>Seu objetivo<input name="objetivo" maxLength={1000} required defaultValue="Organizar minhas atividades pendentes" /></label>{configured && contextAllowed && <label className="checkbox-line"><input type="checkbox" checked={useAI} disabled={!ready} onChange={e => setUseAI(e.target.checked)} /> Usar IA generativa também (autorize o envio na aba Conversar; exclui conteúdos importados do Classroom).</label>}<button className="primary-button" disabled={!!busy}>{busy === 'plan' ? 'Organizando seu plano…' : 'Criar plano de estudo'}</button></fieldset></form></section>
      {plan && <section className="surface connected-plan" aria-live="polite"><span className="eyebrow">{plan.origem === 'ia' ? 'Plano com IA' : 'Planejador por regras'}</span><h2>Seu plano proposto</h2><button type="button" className="secondary-button" onClick={() => download(studyPlanText(plan), 'edutrack-plano-de-estudos.txt')}><Download size={16} /> Baixar plano (.txt)</button><p className="preserve-lines">{plan.resumo}</p><small>Proposta para revisão. Não modifica tarefas, prazos nem agenda. Baixe para guardar antes de sair desta tela.</small>{plan.alertas.map((alert,i) => <p className="connection-notice" key={i}>{alert}</p>)}<div className="plan-blocks">{plan.blocos.map((block,i) => <article key={i}><strong>{new Date(block.data + 'T12:00:00').toLocaleDateString('pt-BR')} · {block.minutos} min</strong><h3>{block.titulo}</h3><p>{block.orientacao}</p></article>)}</div>{!plan.blocos.length && <p>Cadastre tarefas pendentes e gere novamente seu plano.</p>}{plan.tarefas_nao_planejadas.length > 0 && <p>{plan.tarefas_nao_planejadas.length} tarefa(s) não couberam neste período. Amplie sua disponibilidade ou revise os alertas.</p>}</section>}</section>}
  </div>;
}
