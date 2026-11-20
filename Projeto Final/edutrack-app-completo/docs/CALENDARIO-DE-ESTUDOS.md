# Calendário de estudos do dashboard

## Objetivo

Substituir o banner ilustrado grande por uma saudação compacta e um calendário inspirado na visualização de contribuições do GitHub. Os quadrados representam **tempo de estudo concluído**, não commits nem simples acessos ao site. A identidade roxa do EduTrack e os temas claro/escuro são preservados.

## Como usar

1. Acesse o dashboard com sua conta.
2. Selecione os últimos 12, 6 ou 3 meses.
3. Passe o mouse, toque ou use o teclado em um dia para ver data, minutos e sessões.
4. No teclado, use setas para mudar de dia/semana, Home para o início e End para hoje. Tab sai da grade sem percorrer centenas de botões.
5. Em telas estreitas, deslize a grade; os dias recentes aparecem primeiro na área visível.
6. Use o atalho da ofensiva para abrir `/ofensiva`. Os atalhos do cabeçalho continuam levando ao foco, cursos e Edu IA.

Não é necessário conectar uma conta do GitHub. Novos usuários veem valores zerados, sem histórico inventado.

## Regra dos dados

Fonte: sessões concluídas da conta autenticada, já carregadas pela integração acadêmica (`GET /api/study-sessions` via proxy). O componente não adiciona requisições, tabelas ou gravações.

- Cada sessão entra no **dia local de conclusão**, mesmo que tenha começado no dia anterior.
- IDs repetidos são contados uma única vez. Datas inválidas/futuras, minutos não finitos, zero ou negativos são ignorados.
- Cor por total diário: 0; 1–24; 25–49; 50–99; 100 minutos ou mais.
- O intervalo começa no dia seguinte à data equivalente de 3, 6 ou 12 meses atrás, ajustando meses mais curtos, e termina hoje.
- Dias de estudo, minutos e sessões correspondem ao período escolhido. A ofensiva mantém a regra existente: dias consecutivos até hoje ou ontem, independentemente do filtro.
- A virada do dia é conferida a cada minuto com a aba visível e ao voltar à aba. Isso não consulta o banco; novas sessões entram quando o estado acadêmico do app é atualizado.
- A duração declarada pelo aluno não é prova de presença ou mecanismo antifraude.

## Organização do código

| Arquivo | Responsabilidade |
|---|---|
| [StudyActivity.tsx](../app/ui/StudyActivity.tsx) | Calendário, filtros, detalhes e acessibilidade. |
| [study-game.ts](../app/lib/study-game.ts) | Agregação por data local, níveis e navegação por teclado; reaproveita as regras da ofensiva. |
| [study-activity.css](../app/study-activity.css) | Cabeçalho compacto, grade responsiva e temas. |
| [EduTrackViews.tsx](../app/ui/EduTrackViews.tsx) | Integração com o dashboard e seus atalhos existentes. |
| [study-calendar.test.mjs](../tests/study-calendar.test.mjs) | Testes de contagem, limites, deduplicação, ano bissexto, fuso e teclado. |
| [spec.md](../openspec/specs/calendario-de-estudos/spec.md) | Requisitos e cenários no OpenSpec. |

Os cálculos e os rótulos são memoizados para evitar refazer toda a formatação a cada interação. Não foi adicionada biblioteca de gráficos nem dependência de terceiros.

## Validação reproduzível

Execute na pasta `work/edutrack-app-completo`:

```powershell
node --test tests/*.test.mjs
pnpm exec tsc --noEmit
pnpm exec eslint app/ui/StudyActivity.tsx app/lib/study-game.ts tests/study-calendar.test.mjs
pnpm run openspec:validate
pnpm build
```

Conferência visual: conta sem sessões e com histórico; temas claro/escuro; larguras de 320, 390, 768 e 1440 pixels; filtros; seleção por toque/teclado; atalhos. Não crie registros no banco apenas para colorir o calendário sem autorização.

Para reproduzir a conferência sem acessar contas reais:

```powershell
pnpm exec vite --config tests/visual-study-activity/vite.config.mjs
```

Abra <http://127.0.0.1:3013/>. Essa fixture renderiza o mesmo componente `Dashboard`, com uma moldura de teste e dados fictícios identificados na tela. Usa Arial como fonte de fallback, sem depender de download de fontes. Não carrega a API, arquivos `.env` nem autenticação. A opção de histórico permite alternar entre zero sessões e uma amostra; os botões exibem o destino solicitado, sem executar operações acadêmicas. Encerre o servidor com Ctrl+C. A fixture fica fora das rotas publicadas do aplicativo.

## Escopo da entrega

Alteração local do frontend. Não inclui publicação, migrações de banco, importação do GitHub nem mudanças na autenticação. A validação de código não comprova atualização do endereço público.

### Integração ao projeto principal

A funcionalidade está aplicada em `app/ui/EduTrackViews.tsx`, no `Dashboard` usado por `EduTrackApp.tsx`; não fica restrita à prévia. O fluxo é `loadAcademicData` → `academicView` → `Dashboard` → `StudyActivity`. As sessões são as mesmas usadas pelo cronômetro, pela ofensiva e pelos relatórios.

Foram preservados os indicadores, as próximas tarefas, os cursos, os atalhos, o menu recolhível, o tutorial, as telas de login/cadastro, a administração e a integração existente com a API. Apenas o banner superior foi substituído pelo cabeçalho compacto e pelo calendário. Os dados fictícios permanecem exclusivamente em `tests/visual-study-activity`; não são importados pelo aplicativo principal.

Os testes de integração do cálculo confirmam que o mapeamento das sessões da API alimenta o calendário sem modificar cursos, disciplinas, tarefas ou perfil recebidos. Também verificam que calcular um calendário vazio não reaproveita o histórico de outra conta. Esses testes são isolados, não enviam requisições nem gravam no SQL Server.

## Conferência em 20/10/2026

- 34 testes do frontend passaram, incluindo dez testes específicos do calendário e de sua integração com os dados existentes.
- Os dez testes do calendário também passaram em UTC, America/Sao_Paulo e America/New_York.
- TypeScript, lint dos arquivos novos/alterados do calendário e build local passaram.
- Cinco especificações OpenSpec passaram na validação estrita.
- Chrome: estados vazio/com histórico, temas claro/escuro, filtros de 3/6/12 meses, setas/Home/End/Tab, destino dos atalhos e larguras de 320/390/768/1440 pixels conferidos na fixture isolada. Nenhuma rolagem horizontal da página foi observada nessas larguras; a grade rola internamente.
- O dashboard autenticado não foi conferido com dados reais nesta etapa: o ambiente real solicitou login. Não foi criada conta temporária nem desativada autenticação; a prévia sem login usa dados fictícios e não acessa o banco.

As capturas da fixture estão na pasta `output/edutrack-calendario-2026-10-20`, na raiz FACULDADE. Elas demonstram o layout, não o histórico real de um aluno.
