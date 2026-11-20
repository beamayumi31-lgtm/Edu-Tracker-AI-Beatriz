# Validação de Google Classroom e Gemini

Data: 09/11/2026. Escopo: implementação local do EduTrack no workspace `EduTrack.code-workspace`.

## Resultado e limites

A página Integrações, o fluxo OAuth, a importação de disciplinas e tarefas e o adaptador Gemini foram implementados. A validação automatizada e visual local passou. As chamadas Google e de IA dos testes foram simuladas; nenhum dado de aluno real foi enviado a esses provedores. Não foram configuradas credenciais reais, aplicadas migrações no SQL Server ou publicadas alterações na Hostinger/GitHub nesta etapa.

A migração `004_integracoes_google.sql` está preparada. O dicionário e o DER descrevem o modelo alvo de treze tabelas, não uma migração já executada. A última entrega confirmada em produção tem nove tabelas. A ativação está descrita em [CLASSROOM_E_GEMINI.md](CLASSROOM_E_GEMINI.md).

## Verificações executadas

| Verificação | Resultado | Limite da evidência |
|---|---|---|
| Backend — pytest | **122 testes aprovados** | SQLite descartável e transportes externos simulados |
| Backend — Ruff | Aprovado | Análise estática de código, scripts e testes |
| Frontend — testes Node | **40 testes aprovados** | Inclui rotas permitidas do BFF, autenticação e proteção de origem |
| Frontend — TypeScript e ESLint | Aprovados | Tipos e análise estática |
| Build Next para Hostinger | Aprovado | Compilação local; não houve implantação |
| OpenSpec estrito | **9 itens aprovados** | Validação estrutural de especificações e mudança |
| DDL SQL Server | Compilação verificada | Não executado no SQL Server; não comprova concorrência real |
| Chrome desktop e celular | Aprovado com dados fictícios | Prévia em loopback, separada do SQL Server |

O pytest apresentou um aviso de depreciação já existente relacionado a Starlette/httpx TestClient, sem falha de teste. Não foi suprimido para esconder o aviso.

## Cobertura de segurança e comportamento

- OAuth com state de uso único, expiração, PKCE, vínculo ao usuário, escopos mínimos e criptografia do refresh token. Repetição, usuário diferente, escopos incompletos e retorno após cancelamento são rejeitados.
- Prévia e importação consultam novamente as permissões no servidor. Um aluno não pode escolher o curso local de outra conta nem importar uma turma Google não autorizada.
- Paginação, limites, falha parcial, datas UTC e horário `00:00` foram testados. Falhas na obtenção das atividades não geram importações parciais silenciosas.
- Repetir a importação preserva registros existentes, edições e conclusão local. Itens excluídos não são recriados automaticamente. A troca de conta Google exige desconexão explícita.
- Desconexão remove a credencial local e tenta revogação remota, preservando os estudos. Há cobertura para indisponibilidade do Google e perda da chave de criptografia.
- Intercalações controladas cobrem cancelamento durante a troca de código e desconexão durante leitura. Esses testes não substituem testes simultâneos reais de bloqueio/transação no SQL Server.
- Dados importados do Classroom são excluídos do contexto automático enviado a provedores externos. Um teste verifica o conteúdo efetivo enviado ao cliente simulado. O planejador por regras continua podendo usar essas atividades localmente.
- Gemini usa chave no cabeçalho, modelo configurável, timeout, limites de resposta e erros sanitizados. Há cobertura de cotas, respostas inválidas, bloqueio de conteúdo e chamadas de ferramentas com assinatura preservada.
- Sem ativação, credenciais ou declaração de maioridade, o chat Gemini não chama o provedor. No serviço gratuito, somente mensagens da conversa são enviadas, sem ferramentas/contexto acadêmico automático. A declaração não substitui a análise do público e dos termos pelo responsável.

## Conferência visual no Chrome

Foi usado um banco SQLite temporário exclusivo da prévia, com usuário `QA local — Google simulado` e e-mail Google fictício `google-simulado@example.com`. Nenhuma conta real foi criada ou alterada.

1. Login e acesso ao novo item Integrações no menu.
2. Consulta de duas turmas simuladas e seleção da turma SQL Classroom.
3. Prévia de duas atividades publicadas, incluindo prazo UTC e atividade sem prazo.
4. Importação de uma disciplina e duas tarefas; a tela confirmou os registros criados.
5. Repetição da operação sem novos registros; a disciplina existente foi preservada.
6. Consulta das tarefas importadas na página Tarefas, vinculadas à disciplina e ao curso corretos.
7. Geração de plano local com onze blocos, incluindo atividades importadas. Não houve chamada generativa.
8. Layout em temas claro/escuro e viewport móvel de 390 × 844. A largura do documento não excedeu a viewport.
9. Retorno de autorização cancelada com mensagem compreensível e remoção dos parâmetros da URL.
10. Política de privacidade e navegação de retorno. Uma sessão de teste expirada foi encaminhada ao login; após novo login a navegação funcionou.

Durante essa conferência foi identificado um conflito de `next/link` com o runtime Vinext. Os novos links passaram a utilizar o roteador já compartilhado pelo projeto, mantendo o elemento HTML acessível e os atalhos de abertura em nova aba. A navegação foi novamente verificada e o build passou após a correção.

### Evidências — somente dados simulados

![Integrações em desktop, tema escuro](evidencias/integracoes-2026-11-09/classroom-desktop-dark.jpg)

![Integrações em celular, tema claro](evidencias/integracoes-2026-11-09/classroom-mobile-light.jpg)

![Seleção de atividades em celular](evidencias/integracoes-2026-11-09/classroom-mobile-selecao.jpg)

![Plano por regras com atividades importadas fictícias](evidencias/integracoes-2026-11-09/edu-ia-plano-local-mobile.jpg)

![Autorização cancelada, mensagem de retorno](evidencias/integracoes-2026-11-09/oauth-cancelado-mobile.jpg)

## Reproduzir os testes

Na pasta `work/edutrack-api`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check edutrack tests scripts
```

Na pasta `work/edutrack-app-completo`:

```powershell
node --experimental-strip-types --test tests/*.test.mjs
pnpm exec tsc --noEmit
pnpm run lint
pnpm run openspec:validate
pnpm run build:hostinger
```

### Prévia descartável, separada do ambiente normal

Para repetir a conferência visual, abra dois terminais. No primeiro, dentro de `work/edutrack-api`:

```powershell
$env:EDUTRACK_QA_PREVIEW='1'
.\.venv\Scripts\python.exe tests/preview_integrations.py
```

No segundo, dentro de `work/edutrack-app-completo`:

```powershell
$env:EDUTRACK_API_URL='http://127.0.0.1:8014'
$env:EDUTRACK_SITE_URL='http://localhost:3014'
node node_modules/vinext/dist/cli.js dev --host 127.0.0.1 --port 3014 --strictPort
```

- Tela: <http://localhost:3014/integracoes>.
- Swagger desse ambiente simulado: <http://127.0.0.1:8014/docs>.
- Conta de teste exclusivamente local: `avaliacao@example.com` / `Demonstracao-local-2026`.
- Os dados são temporários e reiniciam com o processo da API. O script não deve ser implantado e escuta somente em loopback.
- O estado “Conta conectada” nessa prévia é fornecido por uma fixture. Não demonstra autorização real do Google. Não utilize o botão de conectar da prévia para autorizar uma conta real.

As portas normais do projeto continuam sendo 3002/8000. As portas 3014/8014 são exclusivas de QA; abrir um link depende de os respectivos processos estarem ativos.

## Revisão com Claude e pendências externas

Claude Desktop foi utilizado em duas revisões técnicas, com resumo da arquitetura e dos riscos. Não recebeu segredos nem dados privados de alunos. As observações ajudaram a reforçar troca de conta, retorno OAuth cancelado, proteção do contexto e ativação explícita do Gemini.

Antes de considerar a integração operacional com dados reais, ainda é necessário:

- Criar/configurar o projeto Google, cliente OAuth Web, escopos, redirects e contas de teste; verificar restrições da instituição e requisitos de verificação pública.
- Revisar e autorizar a migração 004, aplicá-la no SQL Server escolhido e testar transações/concorrência nesse banco.
- Configurar chave/modelo Gemini em arquivo privado, revisar público/termos e autorizar sua ativação. Realizar uma pergunta de teste sem dados sensíveis e conferir cotas.
- Testar o redirecionamento Google real no Chrome, incluindo o retorno com cookie Strict e sessão expirada.
- Aprovar a publicação da release, a configuração privada e a proteção de logs do callback na Hostinger.

Nenhuma dessas pendências externas é comprovada pelos testes simulados desta entrega.
