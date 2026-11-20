'use client';

import { ArrowLeft, ArrowRight, BarChart3, BookOpen, Bot, CheckCircle2, CirclePlay, Clock3, Compass, GraduationCap, LayoutDashboard, ShieldCheck, Sparkles, X } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

type TutorialStep = {
  label: string;
  eyebrow: string;
  title: string;
  description: string;
  points: string[];
  icon: LucideIcon;
  previewTitle: string;
  previewRows: { label: string; value: string; progress: number }[];
};

const tutorialSteps: TutorialStep[] = [
  {
    label: 'Introdução', eyebrow: 'Bem-vindo ao seu espaço de estudos',
    title: 'Organize sua jornada com o EduTrack',
    description: 'Um lugar único para planejar o que estudar, acompanhar seu progresso e manter o foco sem perder a simplicidade.',
    points: ['Comece com tudo vazio e personalize no seu ritmo.', 'Alterne entre modo claro e escuro quando quiser.', 'Seus registros acadêmicos ficam salvos na sua conta, no SQL Server.'],
    icon: Sparkles, previewTitle: 'Sua jornada, do seu jeito',
    previewRows: [
      { label: 'Organize', value: 'Cursos e disciplinas', progress: 88 },
      { label: 'Planeje', value: 'Tarefas e metas', progress: 68 },
      { label: 'Evolua', value: 'Foco e progresso', progress: 78 },
    ],
  },
  {
    label: 'Dashboard', eyebrow: 'Visão geral', title: 'Entenda seu momento em poucos segundos',
    description: 'O Dashboard reúne os principais indicadores e mostra o próximo passo mais útil para a sua rotina.',
    points: ['Veja tarefas pendentes, horas estudadas, progresso e sequência.', 'Use os atalhos para cadastrar ou iniciar uma sessão de foco.', 'Os números são calculados somente com os seus registros reais.'],
    icon: LayoutDashboard, previewTitle: 'Resumo da sua semana',
    previewRows: [
      { label: 'Progresso', value: 'Atualizado', progress: 74 },
      { label: 'Tarefas', value: 'Próximas entregas', progress: 56 },
      { label: 'Foco', value: 'Sessões registradas', progress: 82 },
    ],
  },
  {
    label: 'Cursos', eyebrow: 'Sua formação', title: 'Cadastre cursos de qualquer origem',
    description: 'Reúna sua faculdade, plataformas online, cursos livres e estudos independentes no mesmo lugar.',
    points: ['Informe o nome, a instituição e as datas do curso.', 'Edite os dados; o progresso é calculado pelas tarefas concluídas.', 'Abra um curso para visualizar suas disciplinas vinculadas.'],
    icon: GraduationCap, previewTitle: 'Seus cursos',
    previewRows: [
      { label: 'Faculdade', value: 'Em andamento', progress: 72 },
      { label: 'Curso online', value: 'No seu ritmo', progress: 48 },
      { label: 'Estudo livre', value: 'Meta semanal', progress: 61 },
    ],
  },
  {
    label: 'Disciplinas', eyebrow: 'Organização acadêmica', title: 'Divida cada curso em disciplinas',
    description: 'Depois de criar um curso, vincule as matérias e acompanhe cada uma separadamente.',
    points: ['Associe a disciplina ao curso correto.', 'Registre o professor e a carga horária.', 'Conclua tarefas para atualizar automaticamente o percentual.'],
    icon: BookOpen, previewTitle: 'Progresso por disciplina',
    previewRows: [
      { label: 'Banco de Dados', value: '72%', progress: 72 },
      { label: 'Python', value: '58%', progress: 58 },
      { label: 'Engenharia', value: '43%', progress: 43 },
    ],
  },
  {
    label: 'Tarefas', eyebrow: 'Planejamento diário', title: 'Transforme seus objetivos em ações',
    description: 'Cadastre trabalhos, provas, revisões e qualquer atividade que precise concluir.',
    points: ['Defina data, horário, status e duração estimada.', 'Edite, conclua ou reabra uma tarefa quando necessário.', 'Use a tarefa como foco de uma sessão no cronômetro.'],
    icon: CheckCircle2, previewTitle: 'Próximas tarefas',
    previewRows: [
      { label: 'Hoje', value: 'Prioridade alta', progress: 86 },
      { label: 'Esta semana', value: 'Em andamento', progress: 63 },
      { label: 'Concluídas', value: 'Seu histórico', progress: 92 },
    ],
  },
  {
    label: 'Cronômetro', eyebrow: 'Modo foco', title: 'Estude em blocos que funcionam para você',
    description: 'Escolha uma duração, vincule uma tarefa e registre o tempo dedicado ao estudo.',
    points: ['Use sessões de 15, 25, 45 ou 60 minutos.', 'Pause, retome ou reinicie sem perder o controle.', 'Cada sessão confirmada pela API alimenta seus relatórios.'],
    icon: Clock3, previewTitle: 'Sessão de foco',
    previewRows: [
      { label: 'Duração', value: '25 minutos', progress: 72 },
      { label: 'Tarefa', value: 'Selecionada', progress: 58 },
      { label: 'Registro', value: 'Automático', progress: 84 },
    ],
  },
  {
    label: 'Relatórios', eyebrow: 'Acompanhe sua evolução', title: 'Descubra como seu esforço está distribuído',
    description: 'Os relatórios transformam sessões e progresso em uma leitura simples da sua rotina.',
    points: ['Compare o tempo estudado ao longo da semana.', 'Observe a evolução das disciplinas cadastradas.', 'Use os resultados para ajustar metas e prioridades.'],
    icon: BarChart3, previewTitle: 'Evolução semanal',
    previewRows: [
      { label: 'Segunda', value: 'Foco', progress: 42 },
      { label: 'Quarta', value: 'Foco', progress: 76 },
      { label: 'Sexta', value: 'Foco', progress: 91 },
    ],
  },
  {
    label: 'Edu IA', eyebrow: 'Apoio inteligente', title: 'Converse com uma IA que conhece seu contexto',
    description: 'A Edu IA usa as informações do EduTrack para ajudar a organizar estudos, prioridades e próximos passos.',
    points: ['Peça planos de estudo, revisões ou ajuda para priorizar tarefas.', 'Sem chave de IA, use o planejador por regras; ele consulta somente sua conta.', 'Revise informações importantes antes de aplicá-las aos estudos.'],
    icon: Bot, previewTitle: 'Sua assistente de estudos',
    previewRows: [
      { label: 'Contexto', value: 'Seus registros', progress: 88 },
      { label: 'Conversa', value: 'Natural e direta', progress: 74 },
      { label: 'Próximo passo', value: 'Personalizado', progress: 94 },
    ],
  },
  {
    label: 'Descobrir', eyebrow: 'Novas possibilidades', title: 'Encontre ideias para continuar aprendendo',
    description: 'Explore sugestões gerais e adicione ao seu painel somente o que combinar com seus objetivos.',
    points: ['Filtre sugestões por área de interesse.', 'Adicione um curso com um clique e personalize depois.', 'As sugestões são referências, não matrículas automáticas.'],
    icon: Compass, previewTitle: 'Sugestões para você explorar',
    previewRows: [
      { label: 'Tecnologia', value: 'Novos fundamentos', progress: 89 },
      { label: 'Idiomas', value: 'Comunicação', progress: 64 },
      { label: 'Carreira', value: 'Habilidades práticas', progress: 76 },
    ],
  },
  {
    label: 'Conta', eyebrow: 'Segurança e plano', title: 'Proteja o acesso e personalize seu perfil',
    description: 'O login identifica a sua conta e a API protege o acesso aos seus registros.',
    points: ['Cadastre nome, e-mail e senha de pelo menos 10 caracteres.', 'Atualize seu nome na página Perfil.', 'Verificação de contato e plano Pro ainda não estão disponíveis.'],
    icon: ShieldCheck, previewTitle: 'Conta protegida e transparente',
    previewRows: [
      { label: 'Identidade', value: 'Conta autenticada', progress: 100 },
      { label: 'Plano', value: 'Gratuito', progress: 48 },
      { label: 'API', value: 'Conectada', progress: 34 },
    ],
  },
];

export default function TutorialModal({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState(0);
  const dialogRef = useRef<HTMLElement>(null);
  const current = tutorialSteps[step];
  const CurrentIcon = current.icon;
  const isLast = step === tutorialSteps.length - 1;

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dialogRef.current?.focus();

    function handleKeyboard(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose();
      if (event.key === 'ArrowLeft') setStep((value) => Math.max(0, value - 1));
      if (event.key === 'ArrowRight') setStep((value) => Math.min(tutorialSteps.length - 1, value + 1));
    }

    window.addEventListener('keydown', handleKeyboard);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyboard);
    };
  }, [onClose]);

  return (
    <div className="tutorial-backdrop" onMouseDown={onClose}>
      <section
        className="tutorial-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tutorial-title"
        ref={dialogRef}
        tabIndex={-1}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <aside className="tutorial-agenda" aria-label="Etapas do tutorial">
          <div className="tutorial-agenda-brand"><span><GraduationCap size={21} /></span><strong>EduTrack</strong></div>
          <div className="tutorial-agenda-copy"><span>Primeiros passos</span><p>Conheça seu espaço de estudos.</p></div>
          <nav>
            {tutorialSteps.map((item, index) => {
              const StepIcon = item.icon;
              return (
                <button key={item.label} className={index === step ? 'active' : index < step ? 'complete' : ''} onClick={() => setStep(index)} aria-current={index === step ? 'step' : undefined}>
                  <span>{index < step ? <CheckCircle2 size={16} /> : <StepIcon size={16} />}</span>
                  <strong>{item.label}</strong>
                  <small>{String(index + 1).padStart(2, '0')}</small>
                </button>
              );
            })}
          </nav>
          <button className="tutorial-skip" type="button" onClick={onClose}>Pular tutorial</button>
        </aside>

        <div className="tutorial-stage">
          <header className="tutorial-stage-header">
            <div><span>Apresentação</span><strong>{step + 1} de {tutorialSteps.length}</strong></div>
            <button className="tutorial-close" onClick={onClose} aria-label="Fechar tutorial"><X size={20} /></button>
          </header>

          <article className="tutorial-slide" key={current.label}>
            <div className="tutorial-slide-copy">
              <span className="tutorial-slide-icon"><CurrentIcon size={23} /></span>
              <span className="tutorial-eyebrow">{current.eyebrow}</span>
              <h2 id="tutorial-title">{current.title}</h2>
              <p>{current.description}</p>
              <ul>{current.points.map((point) => <li key={point}><CheckCircle2 size={18} /><span>{point}</span></li>)}</ul>
            </div>

            <div className="tutorial-preview" aria-label={'Prévia de ' + current.label}>
              <div className="tutorial-preview-top"><span /><span /><span /><strong>EduTrack</strong></div>
              <div className="tutorial-preview-body">
                <div className="tutorial-preview-sidebar"><span className="active" /><span /><span /><span /><span /></div>
                <div className="tutorial-preview-content">
                  <span className="tutorial-preview-kicker">{current.label}</span>
                  <h3>{current.previewTitle}</h3>
                  <div className="tutorial-preview-hero"><CurrentIcon size={34} /><span /></div>
                  <div className="tutorial-preview-rows">
                    {current.previewRows.map((row) => (
                      <div key={row.label}>
                        <p><strong>{row.label}</strong><span>{row.value}</span></p>
                        <span className="tutorial-preview-track"><i style={{ width: row.progress + '%' }} /></span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </article>

          <footer className="tutorial-footer">
            <div className="tutorial-progress" aria-label={'Etapa ' + (step + 1) + ' de ' + tutorialSteps.length}>
              {tutorialSteps.map((item, index) => <button key={item.label} className={index === step ? 'active' : ''} onClick={() => setStep(index)} aria-label={'Ir para ' + item.label} />)}
            </div>
            <div className="tutorial-actions">
              <button className="tutorial-back" type="button" onClick={() => setStep((value) => Math.max(0, value - 1))} disabled={step === 0}><ArrowLeft size={17} /> Anterior</button>
              <button className="tutorial-next" type="button" onClick={() => isLast ? onClose() : setStep((value) => value + 1)}>
                {isLast ? 'Começar a usar' : 'Próximo'} {isLast ? <CirclePlay size={18} /> : <ArrowRight size={17} />}
              </button>
            </div>
          </footer>
        </div>
      </section>
    </div>
  );
}
