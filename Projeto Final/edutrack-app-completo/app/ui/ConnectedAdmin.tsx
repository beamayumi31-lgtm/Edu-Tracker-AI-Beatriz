'use client';

import { useEffect, useState } from 'react';
import { ArrowRight, KeyRound, MailCheck, ShieldCheck } from 'lucide-react';
import { api } from '../lib/academic-api';
import type { ApiUser } from '../lib/academic-types';

type AdminAccess = { role: 'admin'; email_verificado: true; gestao_usuarios_disponivel: false };

export default function ConnectedAdmin({ role, navigate }: { role: ApiUser['role']; navigate: (path: string) => void }) {
  const [access, setAccess] = useState<AdminAccess | null>(null);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    if (role === 'admin') {
      // Mostrar o conteúdo apenas após confirmação própria do endpoint protegido.
      api<AdminAccess>('admin/access')
        .then((result) => { if (active) setAccess(result); })
        .catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : 'Não foi possível conferir seu acesso.'); });
    }
    return () => { active = false; };
  }, [role, attempt]);

  if (role !== 'admin') return <section className="admin-restricted surface">
    <span className="admin-restricted-icon"><ShieldCheck /></span><span className="eyebrow">Área protegida</span>
    <h1>Acesso exclusivo para administradores</h1><p>Sua conta é de aluno. As permissões são conferidas pela API, não pelo navegador.</p>
    <button className="primary-button" onClick={() => navigate('/dashboard')}>Voltar ao meu painel <ArrowRight size={17} /></button>
  </section>;
  if (error) return <section className="admin-restricted surface"><h1>Acesso não confirmado</h1><p role="alert">{error}</p><button className="secondary-button" onClick={() => { setAccess(null); setError(''); setAttempt((value) => value + 1); }}>Tentar novamente</button></section>;
  if (!access) return <p className="connection-loading" role="status">Conferindo sua permissão de administrador…</p>;
  return <>
    <header className="page-heading"><div><span className="eyebrow">Acesso administrativo</span><h1>Painel administrativo</h1><p>Seu perfil foi validado pela API do EduTrack.</p></div><span className="admin-role-badge"><ShieldCheck size={16} /> Administrador</span></header>
    <section className="admin-summary-grid">
      <article className="surface"><span className="admin-summary-icon violet"><ShieldCheck /></span><div><small>PERFIL ATIVO</small><strong>Administrador</strong><span>Permissão armazenada no SQL Server</span></div></article>
      <article className="surface"><span className="admin-summary-icon emerald"><MailCheck /></span><div><small>CONTA PROTEGIDA</small><strong>E-mail confirmado</strong><span>Verificação obrigatória para administradores</span></div></article>
    </section>
    <section className="surface admin-catalog"><div><span className="eyebrow">Recursos disponíveis</span><h2>Controle de acesso ativo</h2><p>Você pode acessar esta área e continuar usando seus cursos, disciplinas e tarefas normalmente.</p><p>A gestão de outras contas e a edição do catálogo ainda não estão implementadas. Seus estudos continuam separados dos dados dos outros alunos.</p><div className="admin-security-note"><KeyRound size={17} /><span><strong>Proteção no servidor</strong><small>Cadastro público e edição do perfil não podem conceder privilégios.</small></span></div><button className="secondary-button" onClick={() => navigate('/dashboard')}>Ir para meus estudos <ArrowRight size={17} /></button></div></section>
  </>;
}
