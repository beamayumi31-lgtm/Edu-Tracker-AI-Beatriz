# Google Classroom e Gemini — implementação e ativação

Implementação de 09/11/2026, com ativação acompanhada em 10 e 11/11/2026. **Código publicado na Hostinger, migração 004 aplicada com backup e Classroom habilitado na VPS. Conexão individual e prévia real validadas no Chrome: seis turmas e dezesseis atividades de SQL Fundamentals, sem importação.** A correção que permite consultar a prévia sem curso cadastrado foi publicada na release `edutrack-entrega-final-20261110-202738`; importar continua exigindo um curso válido. OAuth permanece em modo de testes, com somente a conta acadêmica autorizada. O público passou a ser 13+: Gemini permanece desligado. A chave criada foi revogada sem uso; consulte [ATIVACAO_INTEGRACOES.md](ATIVACAO_INTEGRACOES.md). Os 129 testes automatizados aprovados na imagem Linux usam provedores simulados. A importação real ainda não foi executada.

## Importação completa publicada em 12/11/2026

A nova [importação completa](IMPORTACAO_COMPLETA_CLASSROOM.md) acrescenta materiais, avisos, tópicos, links e criação opcional do curso. Está publicada na release `edutrack-entrega-final-20261112-171329`, com migração 005 aplicada após backup verificado e três escopos adicionais configurados. Após consentimento e autorização do titular, SQL Fundamentals foi importada para o novo curso Ciência da Computação: 16 tarefas, 24 materiais, 16 avisos, 16 atividades originais e 43 links. A importação repetida preservou os mesmos registros, sem duplicação, conforme [o teste real](IMPORTACAO_REAL_SQL_FUNDAMENTALS_2026-11-12.md). OAuth permanece Externo/Testando, sem habilitar outros alunos automaticamente. Consulte também [o registro de publicação](PUBLICACAO_CLASSROOM_COMPLETO_2026-11-12.md). As seções abaixo preservam o histórico da versão básica e a arquitetura comum.

## Histórico: experiência da versão básica

Em **Integrações**, o aluno conecta sua própria conta Google. A página mostra a conta conectada, busca turmas ativas em que ele é aluno e apresenta uma prévia das atividades publicadas. Ele escolhe um curso do EduTrack, uma turma e as atividades desejadas. A turma torna-se uma disciplina e as atividades tornam-se tarefas pendentes.

É possível trazer apenas a disciplina. Uma nova importação da mesma origem preserva os títulos, descrições, prazos e conclusões já existentes; não sincroniza automaticamente alterações remotas. Uma turma já importada em outro curso pede o curso original. Itens apagados localmente não são recriados automaticamente. A primeira versão não vincula turmas a disciplinas criadas manualmente nem importa anexos, notas, entregas, avisos ou materiais do Drive.

Trocar a conta Google exige desconectar a anterior explicitamente. Importações de contas Google diferentes são independentes e podem representar disciplinas semelhantes; não há fusão automática. Uma conta Google pode ser autorizada em contas EduTrack distintas, mas cada titular precisa concluir OAuth e os dados permanecem isolados por usuário EduTrack.

O status de conclusão no EduTrack é local. O aluno continua entregando trabalhos no Classroom. A desconexão remove a credencial do EduTrack e tenta revogar o acesso no Google, preservando os registros acadêmicos. Se a revogação falhar, a tela orienta remover o acesso em `https://myaccount.google.com/permissions`.

Na **Edu IA**, o planejador local continua usando as atividades da conta, inclusive as importadas, sem depender de chave externa. O chat aceita Gemini ou OpenAI. Por padrão, Gemini funciona como tutor de dúvidas gerais, sem consulta automática ao banco. A interface oferece explicação de conceitos, exercícios e revisão guiada; a conversa fica somente na sessão da página.

## Arquitetura e segurança

```mermaid
sequenceDiagram
  actor Aluno
  participant Web as Next / BFF
  participant API as FastAPI
  participant Google
  participant SQL as SQL Server
  Aluno->>Web: Conectar Classroom
  Web->>API: POST start + sessão
  API->>SQL: Hash do state, PKCE cifrado, validade de 10 min
  API-->>Web: URL Google com PKCE S256
  Web->>Google: Consentimento individual de leitura
  Google-->>Web: Retorno com código e state
  Note over Web: Remove query da URL e mantém código em memória
  Web->>API: POST callback de mesma origem + sessão
  API->>SQL: Confere titular e consome state atomicamente
  API->>Google: Troca código usando secret e PKCE
  API->>SQL: Confere cancelamento; salva refresh token cifrado
  Aluno->>Web: Prévia e seleção
  Web->>API: Importar IDs e curso escolhido
  API->>Google: Reconsulta dados autorizados
  API->>SQL: Lock por conexão + transação + deduplicação
```

- Cookie de sessão permanece `HttpOnly`, `SameSite=Strict` e `Secure` em HTTPS. O retorno Google usa página pública seguida de POST de mesma origem; não enfraquece o cookie para permitir callback.
- `state` aleatório, hash SHA-256, uso único e validade de dez minutos. A tentativa pertence ao aluno autenticado. Nova tentativa invalida a anterior.
- PKCE S256; redirect fixo derivado de `EDUTRACK_FRONTEND_URL`; credenciais e refresh token somente no backend. O token de acesso é transitório, em memória.
- Fernet com chave própria e identificador do titular dentro do conteúdo autenticado. Não reutiliza o segredo JWT. Perder a chave exige reconexão; não trocar a chave sem plano de rotação.
- Validação de escopos realmente concedidos; Google `sub` identifica a conta. E-mail Google pode ser diferente do e-mail EduTrack.
- Curso de destino e todos os vínculos são filtrados pelo usuário. Não recebe título, descrição ou prazo confiados ao navegador para importação.
- Leitura completa antes de gravar; limite de 200 turmas, 500 atividades por turma e 500 selecionadas por importação, no máximo dez turmas por chamada e vinte páginas por recurso. A tela importa uma turma por vez. Falha parcial cancela a operação.
- Chamadas externas limitadas por tempo, tamanho e frequência. IDs não permitem construir URLs arbitrárias. A API chama apenas destinos Google fixos.
- Importações da mesma conexão são serializadas por atualização da linha; índices únicos também impedem duplicação. FK `SET NULL` mantém chaves de origem após exclusão local. A API valida titularidade ao usar referências locais.
- Prazos Classroom são data e hora em UTC; campo de hora `{}` significa meia-noite, não ausência de prazo. Resposta inconsistente é recusada. O navegador apresenta no fuso do aluno.
- Erros não expõem corpos do provedor, tokens ou cabeçalhos. Saída da IA é texto React, sem HTML/Markdown executável, imagens remotas ou ferramentas de escrita.

## Configurar o Google Cloud

1. Criar ou selecionar um projeto próprio no [Google Cloud](https://console.cloud.google.com/), habilitar **Google Classroom API** e configurar **Google Auth Platform**. Aceite de termos e concessão de acesso devem ser realizados/confirmados pelo titular.
2. Definir o nome EduTrack, suporte e dados de contato. Para testes, usar público **External / Testing** e cadastrar explicitamente as contas Google participantes. Uma conta escolar pode depender de liberação da instituição.
3. Solicitar somente estes escopos:

   ```text
   openid
   https://www.googleapis.com/auth/userinfo.email
   https://www.googleapis.com/auth/classroom.courses.readonly
   https://www.googleapis.com/auth/classroom.coursework.me.readonly
   ```

   No console Google, o último escopo foi normalizado para `https://www.googleapis.com/auth/classroom.student-submissions.me.readonly`. O adaptador aceita explicitamente esse nome alternativo e `email` para a identificação, mantendo obrigatórias as quatro permissões de leitura do próprio aluno. Não aceita escopos de professor, escrita ou nomes desconhecidos como substitutos. A lista de atividades continua sendo solicitada com `classroom.coursework.me.readonly`, conforme a documentação de `courses.courseWork.list`; a conexão e a leitura real de atividades foram confirmadas em 11/11/2026.

   A permissão Google descreve **atividades e notas** em conjunto. O EduTrack não consulta nem importa notas ou entregas, mas o consentimento precisa informar esse alcance da permissão. Esse esclarecimento foi publicado nas telas de Integrações e Privacidade.

4. Criar um **OAuth Client ID do tipo Web application**. Não usar chave de API nem cliente Desktop para conectar os alunos.
5. Cadastrar os redirects exatos necessários, em clientes separados para desenvolvimento/produção quando possível:

   ```text
   http://localhost:3002/integracoes/google/callback
   https://srv1834976.hstgr.cloud/integracoes/google/callback
   ```

   Não trocar `localhost` por `127.0.0.1` durante o fluxo. Não cadastrar a porta 8014 de QA como cliente real.

6. Após obter Client ID e Client secret, executar no terminal do VS Code, dentro de `work/edutrack-api`:

   ```powershell
   .\.venv\Scripts\python.exe scripts/configure_google.py
   ```

   A entrada do secret é oculta. O script grava em `%LOCALAPPDATA%\EduTrack\backend.env`, fora do Git e OneDrive, preserva uma chave Fernet existente e **não ativa** a integração. Não envie esses valores pelo chat.

7. Revisar e aprovar [004_integracoes_google.sql](../edutrack-api/migrations/004_integracoes_google.sql). Ela acrescenta quatro tabelas e índices; não altera os dados acadêmicos. A compilação do DDL não comprova execução no SQL Server. Após aplicar em ambiente autorizado e verificar estrutura/permissões, definir `EDUTRACK_CLASSROOM_ENABLED=true` e reiniciar a API.
8. Fazer teste real com uma conta listada como test user: conectar, selecionar uma atividade, importar, repetir, editar e confirmar preservação, desconectar. Só então ampliar o uso.

Aplicativos externos em Testing podem ter refresh tokens de sete dias e limites de participantes. Para disponibilização ampla, revisar os escopos, requisitos de verificação Google, propriedade de domínio e política de privacidade. A hospedagem em `hstgr.cloud` não comprova que podemos verificar a propriedade do domínio no Google. Não há promessa de aprovação pública sem essa etapa.

## Configurar o Gemini

**Não executar para o público atual do EduTrack (13+).** As instruções abaixo documentam o adaptador existente. A configuração local `EDUTRACK_AI_AUDIENCE=includes_teens` bloqueia Gemini, mesmo com chave/modelo/flag e declaração individual de maioridade. Não mudar a classificação para contornar as restrições; a alternativa para adolescentes deve seguir [PUBLICO_13_MAIS.md](PUBLICO_13_MAIS.md).

1. Criar/selecionar projeto próprio no [Google AI Studio](https://aistudio.google.com/) e conferir os termos e a região elegível. **Os termos consultados exigem 18 anos e proíbem clientes direcionados a, ou provavelmente acessados por, menores de 18 anos.** O responsável aceitou anteriormente os termos para público adulto, mas depois escolheu público 13+; por isso a ativação foi interrompida.
2. Criar uma chave da Gemini API e restringi-la à API necessária quando o painel permitir. A chave pertence ao backend. Nunca usar `NEXT_PUBLIC_*`, repositório GitHub, JavaScript do navegador ou Swagger para armazená-la.
3. Conferir o nome exato de um modelo disponível no projeto e seus limites/custos atuais. O código não fixa um modelo nem presume créditos ou gratuidade ilimitada.
4. Executar:

   ```powershell
   .\.venv\Scripts\python.exe scripts/configure_ai.py
   ```

   Escolher `gemini`, informar o modelo e colar a chave na entrada oculta. O script não faz chamadas ao provedor, não ativa faturamento e mantém `EDUTRACK_GEMINI_PAID_SERVICE=false` e `EDUTRACK_GEMINI_ENABLED=false`.

5. Somente após revisão dos termos e do público, autorizar `EDUTRACK_GEMINI_ENABLED=true`, reiniciar a API e conferir `GET /api/edu-ia/status`. `configured=true` significa que o recurso foi habilitado e chave/modelo preenchidos; não comprova validade, cota ou acesso. A interface usa essa distinção.
6. Testar uma pergunta geral, mediante consentimento, observando a resposta e o tratamento de cota. Configure limites no projeto Google. Nunca testar com dados sensíveis reais.

A interface solicita declaração de 18 anos ou mais; a API também exige `maior_de_idade=true` para chamadas Gemini. Isso é uma declaração da sessão, não uma verificação documental de idade, e não substitui a revisão do público e dos requisitos do provedor. Sem flag de ativação ou sem declaração, nenhuma chamada ao Gemini sai da API. O planejador local não exige essa declaração.

No serviço gratuito, apenas as mensagens digitadas são enviadas. O contexto acadêmico e as ferramentas do agente não são habilitados. Um serviço pago só pode liberar contexto manual após revisão do responsável e configuração explícita `EDUTRACK_GEMINI_PAID_SERVICE=true`; isso não é feito pelo script. **Dados de origem Classroom continuam excluídos de todos os provedores externos**, mesmo após desconexão ou desativação da integração. A opção mais completa para esses dados é o planejador local.

O adaptador REST preserva `thoughtSignature` durante chamadas de ferramentas. O agente valida argumentos novamente, limita quatro etapas/quatro consultas e mantém o ID do aluno no servidor. Há limite de oito pedidos por aluno/minuto e vinte pedidos generativos globais/minuto por processo; cada pedido pode fazer até quatro chamadas. A implantação atual usa um worker. Antes de escalar, compartilhar limites por Redis e revisar cotas/custos. Não há retry automático que possa multiplicar consumo.

## API e banco

| Método | Caminho | Função |
|---|---|---|
| GET | `/api/integrations/google/status` | Configuração e conexão da própria conta |
| POST | `/api/integrations/google/start` | Iniciar OAuth autenticado |
| POST | `/api/integrations/google/callback` | Consumir autorização e conectar |
| GET | `/api/integrations/google/courses` | Listar turmas ativas do aluno |
| POST | `/api/integrations/google/preview` | Prévia de atividades de uma turma |
| POST | `/api/integrations/google/import` | Importar seleção em curso próprio |
| DELETE | `/api/integrations/google/connection` | Desconectar e solicitar revogação |
| GET | `/api/edu-ia/status` | Provedor, configuração e política de contexto |
| POST | `/api/edu-ia/chat` | Conversa autorizada com provedor selecionado |
| POST | `/api/edu-ia/study-plan` | Plano local ou generativo conforme configuração |

Swagger normal: `http://127.0.0.1:8000/docs`, disponível somente quando a API local estiver iniciada. No QA isolado: `http://127.0.0.1:8014/docs`. A documentação não é pública em produção. Os contratos completos e exemplos de autenticação aparecem no Swagger; Execute realiza a operação no ambiente em execução.

As novas tabelas são `conexoes_google`, `autorizacoes_google`, `vinculos_classroom_disciplinas` e `vinculos_classroom_tarefas`. A VPS foi verificada com treze tabelas após a migração 004 em 10/11/2026. Isso não afirma que o SQL Server local também recebeu essa migração. Ver [dicionário](DICIONARIO_DE_DADOS.md) e [DER](MODELO_DE_DADOS.md).

## Publicação posterior — plano para aprovação

1. Backup verificado e registro da release atual; preservar CRM e demais sites.
2. Aplicar somente a migração 004 no banco autorizado, verificar índices, FKs e permissões do login da API.
3. Publicar o frontend/backend revisados, com dependência `cryptography` travada. Não copiar `.env`, banco de teste ou credenciais no pacote público.
4. Configurar segredos no arquivo privado da VPS. Acrescentar a exceção de log do callback preparada em `entrega/deploy/hostinger/classroom-callback.nginx.snippet`, validar `nginx -t` e recarregar somente após aprovação. A mudança impede que o código OAuth entre no access log; não reduz validações de TLS ou autenticação.
5. Registrar os redirects reais e a página `/privacidade` no cliente OAuth. Aprovar o conteúdo/contato antes de publicação.
6. Ativar Classroom apenas depois do teste de credenciais. Gemini permanece desligado até chave/modelo e revisão do público/termos. Testar callback no Chrome com cookie Strict e sessão expirada.
7. Em reversão, retornar a release anterior; preservar as tabelas aditivas. Desativar chamadas externas e revogar acessos conforme necessário. Nunca remover as chaves Fernet de tokens existentes sem planejamento.

## Revisão com Claude Desktop

Foi utilizada a sessão gratuita do Claude Desktop em duas revisões: arquitetura inicial e riscos remanescentes. Compartilhamos somente o resumo técnico, sem chaves, arquivos privados ou dados de alunos. A revisão destacou OAuth/IDOR, deduplicação, datas UTC, limites do provedor e proteção dos dados Classroom. Foram reforçados o bloqueio de retorno cancelado, a declaração de maioridade, a troca explícita de conta Google e os testes do conteúdo enviado ao provedor. As sugestões foram conferidas com documentação oficial; não foram tratadas como autorização para alterar serviços. Concorrência real do SQL Server ainda integra a etapa de validação da migração autorizada.

## Fontes oficiais consultadas

- [OAuth para aplicações Web](https://developers.google.com/identity/protocols/oauth2/web-server).
- [PKCE e endpoints Google](https://developers.google.com/identity/protocols/oauth2/native-app#step1-code-verifier).
- [Expiração de tokens OAuth](https://developers.google.com/identity/protocols/oauth2#expiration).
- [Listar turmas](https://developers.google.com/workspace/classroom/reference/rest/v1/courses/list).
- [Listar atividades](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork/list).
- [Campos e datas de CourseWork](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork).
- [Política de dados das APIs Google](https://developers.google.com/terms/api-services-user-data-policy).
- [Termos Gemini, dados e público](https://ai.google.dev/gemini-api/terms).
- [Function calling e assinaturas](https://ai.google.dev/gemini-api/docs/function-calling).
- [Esquema das funções Gemini](https://ai.google.dev/api/caching#FunctionDeclaration).
- [Preços](https://ai.google.dev/gemini-api/docs/pricing) e [limites](https://ai.google.dev/gemini-api/docs/rate-limits).

Políticas, cotas e nomes de modelos devem ser conferidos novamente no momento da ativação.
