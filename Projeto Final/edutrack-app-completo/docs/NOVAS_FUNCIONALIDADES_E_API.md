# EduTrack — novas funcionalidades e contrato para a API

## Objetivo desta etapa

Esta versão implementa a experiência visual e os fluxos locais das novas funcionalidades. Ela não envia e-mail ou SMS, não cria usuários reais e não realiza cobranças. A API será construída separadamente e conectada depois.

## O que já existe no protótipo web

- Cadastro com nome, e-mail, senha, confirmação de senha, CPF e telefone.
- Máscara e validação matemática de CPF no navegador, com aviso no próprio campo ao completar o número ou sair dele.
- Validação de telefone brasileiro com DDD.
- Escolha de verificação por e-mail ou SMS.
- Tela de código de seis dígitos com reenvio e contagem regressiva.
- Recuperação de senha em modo demonstração.
- Página de sugestões gerais de cursos, com filtros e inclusão no painel.
- Página administrativa de gerenciamento, invisível para contas de aluno.
- Página de upgrade sem pagamento ou cobrança.
- Planejamento de um futuro cliente Flutter consumindo a mesma API.

> Código de demonstração da tela de verificação: `123456`.

### CPF: validação e duplicidade

A validação implementada confere os 11 dígitos, rejeita sequências repetidas e verifica os dois dígitos de controle. Ela não comprova que o CPF foi emitido pela Receita Federal ou pertence à pessoa que está preenchendo o cadastro.

A consulta de duplicidade depende da API e do banco de usuários, ainda não conectados. O navegador não deve simular essa consulta com `localStorage` nem afirmar que um CPF está disponível sem uma resposta do servidor.

Ao conectar `POST /api/auth/register`, a API deve repetir a validação, normalizar o CPF e garantir a unicidade no SQL Server. A restrição de unicidade deve proteger também contra dois cadastros simultâneos; uma consulta prévia sozinha não basta. O conflito deve retornar `409` com `code: "CPF_ALREADY_REGISTERED"`, para apresentar “Este CPF já está cadastrado. Entre na sua conta ou recupere sua senha.”, sem divulgar informações do titular. A rota deve ter limite de tentativas e não registrar o CPF nos logs.

Confirmar emissão ou situação cadastral exige uma integração contratada/autorizada com uma fonte oficial, como a [API Consulta CPF do Serpro](https://centraldeajuda.serpro.gov.br/duvidas/pt/avisos/avisoconsultacpfv3/). Essa integração é independente da verificação de duplicidade dentro do EduTrack.

Testes da validação: `node --experimental-strip-types --test tests/cpf.test.mjs`.

## Regras de segurança

- A senha nunca deve ser persistida em texto puro. A API deve salvar somente `senha_hash`, usando Argon2id ou bcrypt com fator de custo adequado.
- O CPF deve ser validado novamente no servidor, normalizado para 11 dígitos e protegido contra duplicidade por usuário.
- Dados sensíveis não devem aparecer em logs. E-mail, telefone e CPF devem ser mascarados quando exibidos.
- Códigos de verificação precisam ser aleatórios, ter expiração curta, limite de tentativas e limite de reenvio.
- O código de verificação também não deve ser salvo em texto puro; armazene um hash temporário.
- Tokens de sessão devem ter expiração, rotação e revogação.
- Toda entrada deve ser validada no servidor, mesmo que a interface já valide no navegador.
- SQL Server deve usar consultas parametrizadas ou um ORM; nunca concatenar entrada do usuário em SQL.
- A permissão de administrador deve ser conferida em cada endpoint protegido. Esconder o menu na interface não substitui autorização no servidor.

## Endpoints propostos

### Autenticação

`POST /api/auth/register`

Cria uma conta e inicia a verificação.

```json
{
  "nome": "Nome do aluno",
  "email": "aluno@exemplo.com",
  "senha": "senha recebida somente por HTTPS",
  "cpf": "00000000000",
  "telefone": "11999999999",
  "canal_verificacao": "email"
}
```

`POST /api/auth/login`

```json
{
  "email": "aluno@exemplo.com",
  "senha": "senha recebida somente por HTTPS"
}
```

`POST /api/auth/verification/send`

Solicita um código por `email` ou `sms`.

`POST /api/auth/verification/confirm`

Confirma o código e ativa a conta.

`POST /api/auth/password/recover`

Inicia a recuperação sem informar se o e-mail existe, evitando enumeração de usuários.

`POST /api/auth/password/reset`

Valida o token temporário e substitui `senha_hash`.

### Conta e perfil

- `GET /api/me`
- `PUT /api/me`
- `GET /api/me/security-status`

O retorno autenticado deve incluir o perfil de acesso (`student` ou `admin`). Contas criadas pelo cadastro público sempre começam como `student`; somente um processo administrativo protegido pode promover uma conta.

### Administração

- `GET /api/admin/overview`
- `GET /api/admin/users`
- `PATCH /api/admin/users/{id}/status`
- `PATCH /api/admin/users/{id}/role`
- `GET /api/admin/verifications`
- `GET /api/admin/integrations/status`
- `POST /api/admin/course-suggestions`
- `PUT /api/admin/course-suggestions/{id}`
- `DELETE /api/admin/course-suggestions/{id}`

Todos os endpoints `/api/admin/*` devem rejeitar usuários anônimos com `401` e usuários autenticados sem o perfil `admin` com `403`.

### Cursos e sugestões

No protótipo, **Editar curso → Excluir curso** abre uma confirmação com o nome do curso e a quantidade de disciplinas e tarefas vinculadas. Cancelar ou pressionar Escape não altera os dados. Confirmar remove essa hierarquia do armazenamento local e retorna à lista de cursos. As sessões concluídas mantêm minutos e datas, com a tarefa excluída desvinculada.

A futura API deve executar a exclusão e o tratamento dos vínculos em uma transação, validando a titularidade pelo usuário autenticado. O cliente não deve remover os registros antes da confirmação de sucesso da API.

- `GET /api/courses`
- `POST /api/courses`
- `PUT /api/courses/{id}`
- `DELETE /api/courses/{id}`
- `GET /api/course-suggestions?category=Tecnologia`

As sugestões devem ser separadas dos cursos do usuário. Um curso sugerido só passa a pertencer ao aluno depois de uma ação explícita.

### Upgrade

- `GET /api/plans`
- `POST /api/billing/checkout`
- `GET /api/billing/subscription`
- `POST /api/billing/webhook`

O checkout deve ser criado no servidor por um provedor de pagamentos. A interface não deve receber ou armazenar dados de cartão diretamente. O status da assinatura só deve mudar após confirmação autenticada do webhook.

### Edu IA

- `POST /api/edu-ia/chat`

O servidor deve selecionar apenas o contexto acadêmico autorizado do usuário, limitar tamanho e frequência das mensagens e manter avisos de que a IA pode cometer erros.

## Estrutura mínima esperada no SQL Server

- `usuarios`: identificação, `senha_hash`, situação, perfil de acesso e datas de auditoria.
- `contatos_verificacao`: canal, destino normalizado, status e datas.
- `codigos_verificacao`: hash do código, expiração, tentativas e consumo.
- `recuperacoes_senha`: hash do token, expiração e consumo.
- `cursos`, `disciplinas`, `tarefas` e `sessoes_estudo`: sempre vinculados por `usuario_id`.
- `planos`, `assinaturas` e `eventos_pagamento`: histórico do upgrade.

O modelo deve ser multiusuário desde o início. Toda consulta acadêmica precisa filtrar pelo usuário autenticado.

## Flutter

O aplicativo Flutter é uma etapa futura, não uma substituição da versão web atual. Web e mobile devem reutilizar:

- a mesma API REST;
- o mesmo modelo de autenticação;
- as mesmas regras de validação;
- o mesmo banco SQL Server;
- contratos de resposta versionados.

## OpenSpec

O OpenSpec está configurado na raiz do projeto com o perfil `core`, idioma Português do Brasil e integrações para Codex e Claude Code.

Especificações-base disponíveis:

- `openspec/specs/autenticacao/spec.md`
- `openspec/specs/organizacao-academica/spec.md`
- `openspec/specs/administracao/spec.md`
- `openspec/specs/edu-ia/spec.md`

Comandos do projeto:

- `pnpm run openspec:list`: lista as especificações atuais.
- `pnpm run openspec:validate`: valida todas as especificações em modo estrito.
- `pnpm run openspec -- view`: abre o painel interativo do OpenSpec.

Para uma nova mudança, use `$openspec-propose "descrição da mudança"` no Codex ou `/opsx:propose "descrição da mudança"` no Claude Code. Depois da revisão da proposta, use o fluxo de aplicação e arquivamento correspondente.
