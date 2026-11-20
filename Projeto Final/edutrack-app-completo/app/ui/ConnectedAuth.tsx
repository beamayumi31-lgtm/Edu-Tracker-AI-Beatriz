'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { ArrowRight, MailCheck, ShieldCheck } from 'lucide-react';
import { Brand, ThemeToggle } from './Brand';
import { useStudyRouter } from './useStudyRouter';
import { api, ApiError } from '../lib/academic-api';
import { getCpfError } from '../lib/cpf';
import type { ApiUser } from '../lib/academic-types';

type AuthOptions = { email_verification_required: boolean; email_delivery_configured: boolean; restricted_adults_mode?: boolean; registration_enabled?: boolean };
type Credentials = { email: string; senha: string };

export default function ConnectedAuth({ register, onLogin }: { register: boolean; onLogin: (user: ApiUser) => void }) {
  const router = useStudyRouter();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [show, setShow] = useState(false);
  const [notice, setNotice] = useState('');
  const [verifying, setVerifying] = useState('');
  const [options, setOptions] = useState<AuthOptions | null>(null);
  const [retryAt, setRetryAt] = useState(0);
  const [remaining, setRemaining] = useState(0);
  const [cpf, setCpf] = useState('');
  const [cpfError, setCpfError] = useState('');
  // Credenciais somente na memória durante a confirmação; nunca em storage/URL.
  const credentials = useRef<Credentials>({ email: '', senha: '' });
  useEffect(() => {
    let active = true;
    api<AuthOptions>('auth/options').then((result) => { if (active) setOptions(result); }).catch((cause) => { if (active) setError(cause.message); });
    return () => { active = false; credentials.current = { email: '', senha: '' }; };
  }, []);
  useEffect(() => {
    const tick = () => setRemaining(Math.max(0, Math.ceil((retryAt - Date.now()) / 1000)));
    tick();
    if (!retryAt) return;
    const timer = window.setInterval(tick, 1000);
    return () => window.clearInterval(timer);
  }, [retryAt]);
  async function login(body: Credentials) {
    const result = await api<{ user: ApiUser }>('auth/login', { method: 'POST', body: JSON.stringify(body) });
    credentials.current = { email: '', senha: '' };
    onLogin(result.user); router.push('/dashboard');
  }
  async function sendCode() {
    setError(''); setNotice(''); setRetryAt(Date.now() + 60_000);
    const result = await api<{ message: string; already_verified?: boolean }>('auth/request-verification', { method: 'POST', body: JSON.stringify(credentials.current) });
    if (result.already_verified) { await login(credentials.current); return; }
    setNotice(result.message);
  }
  async function startVerification(body: Credentials) {
    credentials.current = body; setVerifying(body.email); await sendCode();
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !options || (register && options.registration_enabled === false)) return;
    const data = new FormData(event.currentTarget);
    const email = String(data.get('email')).trim();
    const senha = String(data.get('senha'));
    if (register) {
      const invalid = getCpfError(cpf); setCpfError(invalid || '');
      if (invalid) return;
    }
    if (register && senha !== data.get('confirmation')) { setError('As senhas não coincidem.'); return; }
    setError(''); setNotice(''); setBusy(true);
    let created = false;
    try {
      if (register) {
        await api('auth/register', { method: 'POST', body: JSON.stringify({ nome: String(data.get('nome')).trim(), email, senha, cpf }) });
        created = true; setCpf('');
        if (options.email_verification_required) { await startVerification({ email, senha }); return; }
      }
      try { await login({ email, senha }); }
      catch (cause) {
        if (cause instanceof ApiError && cause.code === 'EMAIL_VERIFICATION_REQUIRED') { await startVerification({ email, senha }); return; }
        throw cause;
      }
    } catch (cause) {
      setError((created ? 'Sua conta foi criada, mas ainda falta concluir o acesso. ' : '') + (cause instanceof Error ? cause.message : 'Não foi possível continuar.'));
    } finally { setBusy(false); }
  }
  async function confirm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const codigo = String(new FormData(event.currentTarget).get('codigo')).trim();
    setBusy(true); setError(''); setNotice('');
    try {
      await api('auth/verify-email', { method: 'POST', body: JSON.stringify({ ...credentials.current, codigo }) });
      setNotice('E-mail confirmado. Entrando na sua conta…');
      await login(credentials.current);
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Não foi possível confirmar.'); }
    finally { setBusy(false); }
  }
  async function resend() {
    if (busy || remaining) return;
    setBusy(true);
    try { await sendCode(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Não foi possível reenviar.'); }
    finally { setBusy(false); }
  }
  const unavailable = options?.email_verification_required && !options.email_delivery_configured;
  return <main className="auth-shell">
    <section className="auth-panel auth-brand-panel"><div className="auth-top"><Brand /><ThemeToggle compact /></div><div><span className="eyebrow">Sua rotina em um só lugar</span><h1>{register ? 'Comece do seu jeito.' : 'Continue de onde parou.'}</h1><p>Cursos, disciplinas, tarefas e planos de estudo conectados à sua conta.</p></div><small>EduTrack · Gestão acadêmica inteligente</small></section>
    <section className="auth-panel auth-form-panel">{register && options?.registration_enabled === false ? <div className="auth-form"><div className="auth-heading"><span>Acesso por aprovação</span><h2>Cadastro público fechado</h2><p>Esta versão é exclusiva para adultos convidados (18+), com conta previamente aprovada e e-mail confirmado. Não basta marcar uma declaração de idade.</p></div><button className="primary-button" onClick={() => router.push('/login')}>Entrar com conta autorizada</button></div> : verifying ? <form className="auth-form" onSubmit={confirm}>
      <div className="email-verification-icon"><MailCheck size={30} /></div>
      <div className="auth-heading"><span>Proteja sua conta</span><h2>Confirme seu e-mail</h2><p>Digite o código de seis dígitos para {verifying}. Ele vale por dez minutos.</p></div>
      <fieldset disabled={busy} className="connected-fields"><label>Código de confirmação<input className="verification-code" name="codigo" required pattern="[0-9]{6}" minLength={6} maxLength={6} inputMode="numeric" autoComplete="one-time-code" placeholder="000000" autoFocus /></label></fieldset>
      {notice && <p className="auth-feedback" role="status">{notice}</p>}
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="primary-button auth-submit" disabled={busy}>{busy ? 'Conferindo…' : 'Confirmar e entrar'} <ArrowRight size={18} /></button>
      <button className="secondary-button auth-submit" type="button" disabled={busy || remaining > 0} onClick={resend}>{remaining > 0 ? `Reenviar em ${remaining}s` : 'Reenviar código'}</button>
      <p className="prototype-note">Confira também o spam. Use somente o código mais recente. Nenhum código é mostrado pelo site ou salvo no navegador.</p>
      <p className="auth-switch"><button type="button" disabled={busy} onClick={() => { credentials.current = { email: '', senha: '' }; setVerifying(''); setError(''); setNotice(''); if (register) router.push('/login'); }}>Voltar para entrar</button></p>
    </form> : <form className="auth-form" onSubmit={submit}><div className="auth-heading"><span>{register ? 'Crie sua conta' : 'Bem-vindo de volta'}</span><h2>{register ? 'Seu espaço de estudos' : 'Entrar no EduTrack'}</h2><p>{register ? 'Seu painel começa vazio, pronto para a sua rotina.' : 'Use sua conta do EduTrack para continuar.'}</p></div>
      <fieldset disabled={busy} className="connected-fields">
        {register && <label>Nome completo<input name="nome" required maxLength={150} autoComplete="name" /></label>}
        {register && <label>CPF<input name="cpf" required value={cpf} onChange={(event) => { setCpf(event.target.value); setCpfError(''); }} onBlur={() => { if (cpf) setCpfError(getCpfError(cpf) || ''); }} maxLength={14} inputMode="numeric" autoComplete="off" placeholder="000.000.000-00" aria-invalid={!!cpfError} aria-describedby="cpf-help" /><small id="cpf-help">{cpfError || 'Validação dos dígitos. O número é descartado após a conferência; não comprova titularidade.'}</small></label>}
        <label>E-mail<input name="email" type="email" required maxLength={255} autoComplete="email" /></label>
        <label>Senha<div className="password-field"><input name="senha" required minLength={register ? 10 : 1} maxLength={128} type={show ? 'text' : 'password'} autoComplete={register ? 'new-password' : 'current-password'} placeholder={register ? 'Mínimo de 10 caracteres' : 'Sua senha'} /><button type="button" onClick={() => setShow(!show)}>{show ? 'Ocultar' : 'Mostrar'}</button></div></label>
        {register && <label>Confirmar senha<input name="confirmation" type={show ? 'text' : 'password'} required minLength={10} maxLength={128} autoComplete="new-password" /></label>}
      </fieldset>
      {unavailable && <p className="auth-feedback">O envio de confirmação está aguardando a configuração do SendGrid pelo responsável pelo projeto.</p>}
      {error && <p className="form-error" role="alert">{error}</p>}
      {!register && <button className="forgot-link" type="button" disabled={busy} onClick={() => router.push('/recuperar-senha')}>Esqueci minha senha</button>}
      <button className="primary-button auth-submit" disabled={busy || !options || !!(register && unavailable)} type="submit">{busy ? 'Conectando…' : !options ? 'Conectando à API…' : register ? 'Criar conta' : 'Entrar'} <ArrowRight size={18} /></button>
      <p className="prototype-note"><ShieldCheck size={16} /> Dados salvos no SQL Server pela API. Sua senha é protegida por hash e não é salva no navegador.</p>
      <p className="prototype-note">{options?.email_verification_required ? 'Confirme seu e-mail para acessar seus estudos. CPF e códigos não são salvos no navegador.' : 'Confirmação de e-mail ainda não ativada neste ambiente local.'}</p>
      {options?.restricted_adults_mode && <p className="auth-feedback">Acesso exclusivo para adultos convidados (18+). Sua conta deve estar aprovada pelo responsável.</p>}{(register || options?.registration_enabled) && <p className="auth-switch">{register ? 'Já tem uma conta?' : 'Ainda não tem conta?'} <button type="button" disabled={busy} onClick={() => router.push(register ? '/login' : '/cadastro')}>{register ? 'Entrar' : 'Cadastre-se'}</button></p>}
    </form>}</section>
  </main>;
}
