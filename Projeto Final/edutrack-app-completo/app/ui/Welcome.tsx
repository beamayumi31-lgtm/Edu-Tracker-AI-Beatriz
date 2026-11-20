'use client';

import { ArrowRight, CheckCircle2, ChevronRight, Clock3, GraduationCap, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Brand, ThemeToggle } from './Brand';
import { useAccessPolicy } from './AccessNotice';

export default function Welcome() {
  const router = useRouter();
  const policy = useAccessPolicy();
  return (
    <main className="welcome-shell">
      <div className="welcome-glow welcome-glow-one" />
      <div className="welcome-glow welcome-glow-two" />
      <nav className="welcome-nav">
        <Brand />
        <div className="welcome-nav-actions">
          <ThemeToggle compact />
          <button className="text-button" onClick={() => router.push('/login')}>Já tenho uma conta</button>
        </div>
      </nav>
      <section className="welcome-content">
        <div className="welcome-copy">
          <span className="eyebrow"><Sparkles size={15} /> Organização acadêmica inteligente</span>
          <h1>Estudar com clareza muda tudo.</h1>
          <p>Organize seus estudos, acompanhe seu progresso e construa uma rotina que faça sentido para você.</p>
          {policy?.restricted_adults_mode && <p className="connection-notice">Exclusivo para adultos convidados (18+). Cadastro público fechado; acesso aprovado individualmente.</p>}<div className="welcome-actions">
            {policy?.registration_enabled && <button className="primary-button" onClick={() => router.push('/cadastro')}>Criar conta <ArrowRight size={18} /></button>}
            <button className="secondary-button" onClick={() => router.push('/login')}>Entrar</button>
          </div>
          <div className="welcome-proof">
            <span><CheckCircle2 size={17} /> Faculdade e cursos livres no mesmo lugar</span>
            <span><CheckCircle2 size={17} /> Dados preenchidos pelo próprio estudante</span>
          </div>
        </div>
        <div className="welcome-preview" aria-label="Prévia de um painel vazio do EduTrack">
          <div className="preview-top"><span>Seu painel</span><strong>Pronto para começar</strong></div>
          <div className="ring-wrap"><div className="progress-ring empty-ring"><span>0%</span><small>seu progresso</small></div></div>
          <div className="preview-row"><span className="preview-icon violet"><GraduationCap size={18} /></span><div><strong>Adicione seu primeiro curso</strong><small>Faculdade, plataforma ou estudo independente</small></div><ChevronRight size={16} /></div>
          <div className="preview-row"><span className="preview-icon cyan"><Clock3 size={18} /></span><div><strong>Planeje sua primeira sessão</strong><small>Use o cronômetro do seu jeito</small></div><ChevronRight size={16} /></div>
        </div>
      </section>
      <footer className="welcome-footer">EduTrack · Seu aprendizado, organizado. <Link href="/apresentacao">Conheça o projeto acadêmico →</Link></footer>
    </main>
  );
}
