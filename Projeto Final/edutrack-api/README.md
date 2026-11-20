# EduTrack API

API em Python/FastAPI para o banco SQL Server `EduTrackIA`, com autenticação, CRUD multiusuário e agente Edu IA. O código do site permanece separado em `../edutrack-app-completo`.

## Estado real desta entrega

Atualização de 09/11/2026: integração Classroom e adaptador Gemini implementados e testados localmente. Consulte [configuração e privacidade](../edutrack-documentacao/CLASSROOM_E_GEMINI.md) e [resultados atuais](../edutrack-documentacao/VALIDACAO_INTEGRACOES.md). São 122 testes de backend aprovados. A migração 004 ainda não foi aplicada; OAuth e Gemini reais dependem de credenciais e ativação. Os resultados históricos abaixo não representam a validação dessa nova integração.

Atualização final: consulte [ESTADO_ATUAL.md](../edutrack-documentacao/ESTADO_ATUAL.md). Recuperação implementada e migração 003 aplicada localmente em 03/11/2026, com autorização. Resultados abaixo descrevem também etapas históricas; não são prova de publicação na Hostinger.

Atualização local de CPF/e-mail: CPF validado e descartado no cadastro. Confirmação SendGrid ativada nesta máquina após migração autorizada, remetente verificado e chave restrita. O teste real recebeu HTTP 202 (aceito para envio, não comprovante de entrega). Veja [CPF_E_EMAIL.md](../edutrack-documentacao/CPF_E_EMAIL.md).

- Implementados: cadastro, login, identificação do usuário, CRUD de cursos/disciplinas/tarefas, registro e consulta de sessões, resumo acadêmico, contexto do aluno e proposta de plano de estudo.
- Agente implementado com ferramentas restritas de consulta e planejamento. `EDUTRACK_AI_PROVIDER` seleciona OpenAI ou Gemini; cada provedor exige chave/modelo no backend. Gemini também exige ativação explícita e revisão do público/termos. Nenhuma chave está incluída no código.
- Planejamento por regras funciona sem IA, com `origem: "regras"`. Não simula resposta de um modelo.
- SQL Server foi validado com **83 verificações de integração**, após autorização: gravação, leitura, atualização, exclusão e isolamento de duas contas fictícias. Ao final, todos os dados de teste foram removidos e a estrutura e os dados foram comparados ao estado anterior, sem diferenças. Os **49 testes automatizados** usam SQLite descartável em memória e provedor de IA simulado; nenhuma chamada real ao modelo foi feita.
- **O frontend local já consome esta API.** Login/cadastro, nome do perfil, CRUD acadêmico, cronômetro e planejamento estão conectados. Também passaram 52 verificações HTTP via proxy e uma conferência no Chrome. O site público continua inalterado.
- Gravação continua desativada por padrão. O inicializador integrado habilita escrita somente no processo local contra localhost\SQLEXPRESS / EduTrackIA, sem editar `.env`. Nenhuma migração é executada ao iniciar.

## Administração local

O perfil `student` é o padrão; `admin` é definido exclusivamente pelo operador no servidor. Cadastro público e edição do perfil rejeitam o campo `role`. `GET /api/admin/access` exige sessão válida, papel administrativo atual no banco e e-mail confirmado, mesmo se a verificação geral estiver desativada. A rota está documentada no Swagger.

Aplicar `migrations/002_perfis_administrador.sql` somente com autorização, na instância local `localhost\SQLEXPRESS`, banco `EduTrackIA`. A migração é transacional, idempotente e aditiva: acrescenta `usuarios.role` e `convites_administrador`, preservando os dados anteriores e mantendo todas as contas existentes como alunos. Não é executada automaticamente ao iniciar a API.

Depois da migração, para reservar uma autorização explicitamente aprovada:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_admin.py --email EMAIL_AUTORIZADO --confirm-local-write
```

Se a conta já existir e tiver e-mail confirmado, o script promove essa conta sem modificar senha ou estudos. Caso contrário, reserva a autorização por sete dias. O titular conclui o cadastro normal em <http://localhost:3002/cadastro>, escolhendo sua própria senha e confirmando o código recebido por e-mail. O convite é consumido uma única vez na mesma transação da verificação; não é uma senha nem um link de acesso. Nenhuma chave ou senha é gerada/exposta pelo script. Repetir uma reserva consumida não restaura privilégios revogados.

O menu **Administração** e o painel protegido usam o perfil da API. Nesta etapa, a gestão de outras contas e do catálogo ainda não está disponível. Ser administrador não remove o isolamento dos cursos, disciplinas e tarefas por usuário.

Reversão lógica, somente após nova autorização do operador: alterar `usuarios.role` da conta exata para `student` e expirar eventual convite pendente. O acesso administrativo é recusado já na próxima chamada, inclusive com JWT anterior. Preservar o convite consumido como registro; não excluir contas, tabelas ou dados acadêmicos. Para voltar ao código anterior, a coluna/tabela aditivas podem permanecer sem uso, sem executar DROP.

Validação desta alteração: testes de API em SQLite isolado cobrem convite, expiração, e-mail incorreto, uso único, isolamento entre alunos, recusa a autopromoção e revogação imediata. Testes não enviam mensagens reais e não criam contas no SQL Server local.

## Abrir o projeto inteiro no VS Code

Abra `../../EduTrack.code-workspace`. Na lateral: `Frontend`, `Backend`, `Documentacao` e referências antigas claramente separadas. Leia primeiro `../edutrack-documentacao/COMECE_AQUI.md`.

## Executar no Windows

Para iniciar **site + API + Swagger**, abra `../../Iniciar EduTrack.cmd` ou a tarefa **EduTrack: iniciar site + API + Swagger** no VS Code. O Chrome abre depois da confirmação de disponibilidade. Leia o [guia do Swagger](../edutrack-documentacao/TESTAR_APIS.md).

Pré-requisitos: Python 3.12+, SQL Server e ODBC Driver 18. Já existe um ambiente virtual `.venv` nesta máquina.

```powershell
# Execute dentro da pasta work/edutrack-api.
.\.venv\Scripts\python.exe -m edutrack.run --local-sql-certificate
```

Documentação interativa: <http://127.0.0.1:8000/docs>. Saúde: `/health`; conexão somente leitura: `/ready`.

O servidor escuta apenas em `127.0.0.1`. O parâmetro de certificado é exclusivo para o SQL Express local e não deve ser usado em produção. Windows Integrated Authentication usa a conta que executa a API.

Para instalar em outra máquina:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
```

No Windows, mantenha segredos em `%LOCALAPPDATA%/EduTrack/backend.env`, carregado por `python -m edutrack.run`, fora do Git e do OneDrive. A configuração privada já existe nesta máquina; não a exponha nem substitua sem autorização. Em outras instalações, use os nomes de `.env.example`; `.env` continua sendo uma alternativa portátil, desde que fora de sincronização. Sem chave JWT, desenvolvimento usa uma chave efêmera; reiniciar invalida os tokens existentes. Verificação por e-mail e produção exigem chave persistente. Variáveis do ambiente têm prioridade sobre arquivos.

**Somente após autorização para gravar no banco**, habilite `EDUTRACK_DB_WRITES_ENABLED=true` no `.env` e inicie pelo terminal. A tarefa de consulta do VS Code força `false`, mesmo se o `.env` estiver habilitado.

## Fluxo de uso da API

1. `POST /api/auth/register`: `{ "nome": "Aluno", "email": "aluno@example.com", "senha": "uma senha longa", "cpf": "00000000191" }` (CPF somente matemático de teste, sem comprovação de titularidade).
   Se a confirmação estiver ativa, solicitar código em `POST /api/auth/request-verification` e confirmar em `POST /api/auth/verify-email` antes do login. Usar caixa de e-mail própria/autorizada para o envio real.
2. `POST /api/auth/login`: e-mail e senha. Copie `access_token` para **Authorize** no Swagger.
3. Crie um curso, depois uma disciplina com seu `curso_id`, depois uma tarefa com sua `disciplina_id`.
4. Consulte e edite pelos endpoints abaixo. `PUT` substitui todos os campos editáveis; não é um PATCH parcial.
5. Gere uma proposta de estudo. O agente não salva o plano nem altera as tarefas por conta própria.

| Recurso | Endpoints |
|---|---|
| Conta | `POST /api/auth/register`, `POST /api/auth/login`, `GET/PUT /api/me` |
| Cursos | `GET/POST /api/courses`, `GET/PUT/DELETE /api/courses/{id}` |
| Disciplinas | `GET/POST /api/disciplines`, `GET/PUT/DELETE /api/disciplines/{id}` |
| Tarefas | `GET/POST /api/tasks`, `GET/PUT/DELETE /api/tasks/{id}` |
| Estudo | `GET/POST /api/study-sessions`, `GET /api/dashboard` |
| Edu IA | `GET /api/edu-ia/status`, `GET /api/edu-ia/context`, `POST /api/edu-ia/chat`, `POST /api/edu-ia/study-plan` |

Listas são paginadas: `?limit=50&offset=0`, máximo 100. Disciplinas aceitam `curso_id`; tarefas aceitam `disciplina_id` e `status`. Estados: `pendente`, `em_andamento`, `concluida`, `cancelada`.

UUIDs de titularidade são definidos pelo servidor, nunca pelo cliente. O acesso a IDs de terceiros retorna `404`; listas não retornam registros alheios. Senhas usam Argon2id. Tokens expiram após 20 minutos. Não há renovação automática ou revogação individual de tokens. A recuperação por e-mail usa links de uso único e invalida sessões anteriores ao trocar a senha; veja ../edutrack-documentacao/RECUPERACAO_DE_SENHA.md.

Exclusão de curso com disciplinas, disciplina com tarefas ou tarefa com histórico retorna `409`. Essa proteção evita perda de histórico no esquema atual, que usa FKs sem cascata. Não existe cascata silenciosa.

`data_prevista`, início e fim de sessão devem incluir fuso, por exemplo `2030-01-02T20:00:00-03:00`. O banco usa UTC. Sessões precisam de tarefa vinculada e duração de 1 a 240 minutos. A entrada é declarada pelo cliente, não comprova presença/foco; não usar como sistema antifraude. Envie um UUID em `Idempotency-Key` para repetir a mesma sessão sem duplicar. A mesma chave com dados diferentes retorna 409. Sem a chave, repetir POST pode duplicar registros.

`duracao_minutos` é calculada pelo próprio SQL Server com `DATEDIFF(minute)` e não deve ser enviada no INSERT. O mapeamento respeita a coluna calculada já existente. O cálculo conta viradas de minuto, podendo diferir do arredondamento para baixo dos segundos decorridos.

## Agente Edu IA

```json
{
  "data_inicio": "2030-01-01",
  "dias": 7,
  "minutos_por_dia": 60,
  "objetivo": "Revisar SQL e entregar as atividades pendentes",
  "usar_ia": false,
  "enviar_dados_ia": false
}
```

Envie para `POST /api/edu-ia/study-plan`. A data é um exemplo; escolha a data desejada. Para explicação pelo agente, configure o servidor e envie ambos os booleanos como `true`.

Chat: `{ "messages": [{ "role": "user", "text": "Me ajude com meu plano de estudos" }], "enviar_dados_ia": true }`.

O consentimento é obrigatório para chamadas externas. São enviados mensagens e contexto acadêmico limitado (nomes, descrições curtas, prazos, estimativas e IDs), não campos de cadastro, CPF, telefone, hash de senha ou lista de alunos. Não coloque dados pessoais em descrições acadêmicas. A chave não vai ao navegador.

Ferramentas permitidas: `consultar_contexto_academico` e `propor_plano_estudo`. Nenhuma recebe `usuario_id`. Não existem ferramentas para executar SQL, navegar na internet ou alterar registros. Máximo de quatro etapas/chamadas do agente, timeout de 30 segundos por chamada, sem repetição automática do provedor. O limitador permite oito solicitações de IA/planejamento por minuto por aluno.

O planejador prioriza prazos, divide estimativas em blocos de até 25 minutos, respeita disponibilidade e alerta sobre atividades não cobertas ou posteriores à entrega. Estimativas ausentes recebem 50 minutos. Pausas não são somadas ao orçamento diário. As comparações de prazo desta versão são em UTC. Planos são propostas, não garantia de conclusão. Títulos/descrições e mensagens são tratados como dados não confiáveis; argumentos de ferramentas são revalidados.

## Verificar

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check edutrack tests scripts
.\.venv\Scripts\python.exe scripts/check_database.py --local-sql-certificate
```

Os testes usam FK e unicidade habilitadas em memória. O script de banco consulta metadados e executa `SELECT TOP 0`; não faz `INSERT`, `UPDATE`, `DELETE` ou DDL.

Há também `scripts/test_sqlserver_integration.py`, separado da suíte comum. Ele só grava quando executado explicitamente com `--executar`, contra o servidor/banco locais fixados no código. Cria contas exclusivas, testa as rotas via cliente ASGI e transações SQL reais, faz limpeza por identidade exata em `finally` e compara dados/estrutura antes e depois. **Novas execuções exigem autorização do responsável pelo banco.** Não publica servidor HTTP nem chama a IA externa. Veja `docs/TESTES_SQLSERVER.md`.

## Limites e próximos passos antes de produção

- Integração das telas concluída localmente. O proxy mantém o JWT em cookie HttpOnly/SameSite, valida a origem das escritas e só confirma gravações após a resposta da API. Revisar novamente no ambiente de produção.
- Revisar com autorização uma migração para campos do frontend que não existem no banco: CPF/telefone e verificação, perfil administrativo, preferências, sessões livres, planos persistentes e campos extras dos cursos.
- Confirmar a chegada do teste SendGrid à caixa autorizada e concluir uma confirmação real pelo cadastro; aceitação HTTP 202 já verificada. SMS, renovação automática e revogação individual de sessões continuam pendentes; códigos nunca são fixos em execução real.
- Persistir histórico do chat/planos somente após definir retenção e autorização. Hoje a conversa recebida limita-se às últimas dez mensagens enviadas pelo cliente.
- Hospedar API Python em serviço separado com HTTPS e credenciais de banco de menor privilégio. Sites não executa esta aplicação Python; o site público não deve apontar para localhost.
- Usar limite distribuído em Redis/gateway para múltiplos processos, limites de gasto do provedor, auditoria sem dados sensíveis, backup e monitoramento. O limitador em memória é destinado à instância local.
- Configurar chave e modelo de IA, revisar compartilhamento de dados/custos e testar uma chamada real. `store=false` não equivale a promessa de retenção zero do provedor.
- CRUD e fluxo local no Chrome validados. Repetir os testes após a configuração da hospedagem HTTPS; resultados locais não certificam produção.

Referências da implementação: [FastAPI — segurança JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [SQLAlchemy — SQL Server](https://docs.sqlalchemy.org/en/20/dialects/mssql.html), [OpenAI — function calling](https://developers.openai.com/api/docs/guides/function-calling).
