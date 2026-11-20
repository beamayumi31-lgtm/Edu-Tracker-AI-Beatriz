import AccessNotice from '../ui/AccessNotice';
import Link from 'next/link';
import { ArrowRight, BookOpen, CalendarDays, Check, Clock3, GraduationCap, Layers3, ShieldCheck } from 'lucide-react';
import './presentation.css';

export const metadata = { title: 'EduTrack | Apresentação acadêmica' };
const features = [
  { icon: BookOpen, title: 'Tudo no seu lugar', text: 'Cursos, disciplinas, tarefas e materiais reunidos em uma rotina de estudo organizada.' },
  { icon: Clock3, title: 'Foco que vira progresso', text: 'Cronômetro, sessões de estudo, calendário de atividade e relatórios semanais com exportação CSV.' },
  { icon: CalendarDays, title: 'Um plano possível', text: 'Planejamento por regras com as tarefas da conta, os prazos e o tempo disponível. Funciona sem IA externa.' },
];
export default function Presentation() {
  return <main className="presentation">
    <nav className="presentation-nav"><Link href="/" className="presentation-brand"><GraduationCap /> EduTrack</Link><Link href="/login">Acessar o sistema <ArrowRight size={16} /></Link></nav>
    <header className="presentation-hero"><span className="presentation-kicker">PROJETO ACADÊMICO · ORGANIZAÇÃO DE ESTUDOS</span><h1>Menos dispersão.<br /><em>Mais aprendizado.</em></h1><p>Um espaço para transformar conteúdos, tarefas e tempo disponível em uma rotina de estudos clara.</p><div className="presentation-actions"><Link className="presentation-cta" href="/login">Conhecer o EduTrack <ArrowRight size={18} /></Link><a href="#demonstracao">Ver roteiro da demonstração ↓</a></div><div className="presentation-stack"><span>React + TypeScript</span><span>Python + FastAPI</span><span>SQL Server</span></div></header>
    <AccessNotice /><section className="presentation-features" aria-label="Recursos principais">{features.map(({ icon: Icon, title, text }, i) => <article key={title}><span className="presentation-number">0{i + 1}</span><Icon size={28} /><h2>{title}</h2><p>{text}</p></article>)}</section>
    <section className="presentation-section" id="demonstracao"><div><span className="presentation-kicker">DO PLANEJAMENTO À PRÁTICA</span><h2>Uma demonstração<br />em cinco passos.</h2><p>Use uma conta autorizada. Dados de estudantes e credenciais não devem aparecer na apresentação.</p></div><ol className="presentation-steps"><li><strong>Organizar</strong><span>Abra um curso, suas disciplinas e as tarefas.</span></li><li><strong>Conectar</strong><span>Mostre os materiais já importados do Classroom. A conexão Google depende de uma conta de teste autorizada.</span></li><li><strong>Planejar</strong><span>Gere um plano local com o tempo disponível e revise a proposta.</span></li><li><strong>Estudar</strong><span>Inicie, pause e retome uma sessão de foco.</span></li><li><strong>Acompanhar</strong><span>Apresente o relatório semanal, a tabela acessível e o CSV.</span></li></ol></section>
    <section className="presentation-foundation"><div><ShieldCheck size={28} /><h2>Privacidade faz parte do projeto.</h2><p>Dados separados por usuário, acesso autenticado e permissões do Google preservadas. A validação matemática de CPF não comprova identidade, e o CPF não é armazenado.</p></div><div><Layers3 size={28} /><h2>Uma arquitetura explicável.</h2><p>A interface conversa com a API, que aplica as regras e persiste no SQL Server. Cursos, disciplinas, tarefas e sessões formam a estrutura central do modelo relacional.</p></div></section>
    <section className="presentation-status"><span className="presentation-kicker">ESCOPO DA ENTREGA</span><h2>Transparência, sem promessas vazias.</h2><div><p><Check size={18} /> Organização acadêmica, foco, relatórios e planejador local implementados.</p><p><Check size={18} /> Importação do Classroom validada em uma conta autorizada em 12/11/2026.</p></div><p className="presentation-limit">Google OAuth permanece em modo de teste. O chat generativo depende de configuração do provedor e autorização de envio. Pagamentos e aplicativo móvel não estão ativos nesta versão. A página é um guia do projeto, não uma demonstração automática nem prova de disponibilidade de todas as integrações.</p></section>
    <footer className="presentation-footer"><span>EduTrack · Seu aprendizado, organizado.</span><Link href="/privacidade">Privacidade</Link><Link href="/login">Abrir o sistema →</Link></footer>
  </main>;
}
