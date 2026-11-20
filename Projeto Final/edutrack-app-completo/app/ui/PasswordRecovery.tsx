'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { ArrowLeft, ArrowRight, CheckCircle2, KeyRound, Mail } from 'lucide-react';
import { api } from '../lib/academic-api';
import { Brand, ThemeToggle } from './Brand';
import { useStudyRouter } from './useStudyRouter';

export default function PasswordRecovery() {
  const router = useStudyRouter();
  const [token, setToken] = useState('');
  const [available, setAvailable] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    const value = new URLSearchParams(window.location.hash.slice(1)).get('token');
    // O token permanece somente na memória; remover o fragmento do histórico visível.
    if (value) {
      // Consome o fragmento externo uma vez após SSR, removendo-o imediatamente do histórico.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      if (/^[A-Za-z0-9_-]{43}$/.test(value)) setToken(value);
      else setError('Link inválido. Solicite um novo link abaixo.');
      window.history.replaceState(null, '', window.location.pathname + window.location.search);
    }
    api<{ password_reset_available: boolean }>('auth/options')
      .then((result) => { if (active) setAvailable(result.password_reset_available); })
      .catch(() => { if (active) { setAvailable(false); setError('Não foi possível conectar à API. Tente novamente mais tarde.'); } });
    return () => { active = false; };
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !available) return;
    const data = new FormData(event.currentTarget);
    if (token && data.get('senha') !== data.get('confirmation')) { setError('As senhas não coincidem.'); return; }
    setBusy(true); setError('');
    try {
      if (token) {
        await api('auth/reset-password', { method: 'POST', body: JSON.stringify({ token, senha: data.get('senha') }) });
        setToken(''); setDone(true);
      } else {
        await api('auth/forgot-password', { method: 'POST', body: JSON.stringify({ email: String(data.get('email')).trim() }) });
        setSent(true);
      }
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Não foi possível continuar.'); }
    finally { setBusy(false); }
  }

  return <main className="auth-shell compact-auth-shell">
    <section className="auth-panel auth-brand-panel recovery-brand-panel"><div className="auth-top"><Brand /><ThemeToggle compact /></div><div><span className="eyebrow"><KeyRound size={16} /> Acesso à sua conta</span><h1>Seus estudos continuam aqui.</h1><p>Recupere o acesso e retome sua jornada. Seus cursos, disciplinas e tarefas permanecem na sua conta.</p></div><small>EduTrack · Um passo de cada vez</small></section>
    <section className="auth-panel auth-form-panel"><form className="auth-form" onSubmit={submit}>
      <div className="email-verification-icon">{done ? <CheckCircle2 size={30} /> : token ? <KeyRound size={30} /> : <Mail size={30} />}</div>
      <div className="auth-heading"><span>{done ? 'Tudo pronto' : 'Esqueci minha senha'}</span><h2>{done ? 'Senha atualizada' : token ? 'Crie uma nova senha' : sent ? 'Confira seu e-mail' : 'Vamos recuperar seu acesso'}</h2><p>{done ? 'Entre com sua nova senha. As sessões anteriores foram encerradas.' : token ? 'Escolha uma senha de pelo menos 10 caracteres. O link vale por 15 minutos e só pode ser utilizado uma vez.' : sent ? 'Se houver uma conta com esse e-mail, você receberá um link. Confira também o spam e abra o link neste navegador.' : 'Informe o e-mail usado no cadastro para receber um link de recuperação.'}</p></div>
      {!done && !sent && <fieldset className="connected-fields" disabled={busy || !available}>{token ? <><label>Nova senha<input name="senha" type="password" required minLength={10} maxLength={128} autoComplete="new-password" /></label><label>Confirmar nova senha<input name="confirmation" type="password" required minLength={10} maxLength={128} autoComplete="new-password" /></label></> : <label>E-mail<input name="email" type="email" required maxLength={255} autoComplete="email" /></label>}</fieldset>}
      {available === false && <p className="auth-feedback" role="status">A recuperação por e-mail ainda não está disponível neste ambiente. Tente novamente depois da ativação pelo responsável.</p>}
      {error && <p className="form-error" role="alert">{error}</p>}
      {!done && !sent && <button className="primary-button auth-submit" disabled={busy || !available}>{busy ? 'Aguarde…' : available === null ? 'Conectando…' : token ? 'Salvar nova senha' : 'Enviar link de recuperação'} <ArrowRight size={18} /></button>}
      {token && <button className="secondary-button" type="button" disabled={busy} onClick={() => { setToken(''); setError(''); }}>Solicitar outro link</button>}
      <button className={done ? 'primary-button auth-submit' : 'secondary-button auth-submit'} type="button" disabled={busy} onClick={() => router.push('/login')}><ArrowLeft size={17} />{done ? 'Entrar com a nova senha' : 'Voltar para entrar'}</button>
    </form></section>
  </main>;
}
