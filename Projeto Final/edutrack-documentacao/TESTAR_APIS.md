# EduTrack — iniciar o projeto e testar no Swagger

## Abrir tudo

Na pasta FACULDADE, dê dois cliques em **Iniciar EduTrack.cmd**.
Ele inicia API + frontend, verifica a conexão e abre duas abas no Chrome:

- Site: http://localhost:3002/login
- Swagger: http://127.0.0.1:8000/docs
- Atalho alternativo da API: http://127.0.0.1:8000/swagger
- Contrato OpenAPI: http://127.0.0.1:8000/openapi.json

O arquivo **Swagger EduTrack.url** apenas abre a documentação; ele não inicia a API.
No VS Code, abra **EduTrack.code-workspace** e use Terminal → Executar Tarefa → **EduTrack: iniciar site + API + Swagger**.

Mantenha o terminal aberto enquanto testa. Para encerrar site e API, pressione **Ctrl+C** ou digite **sair** e Enter. Se o Chrome não for encontrado, abra os endereços manualmente. O comando não instala serviços nem inicia junto com o Windows. Portas ocupadas geram aviso; outros processos não são encerrados.

## Atenção ao banco

O inicializador integrado habilita gravações reais em **localhost\SQLEXPRESS / EduTrackIA** durante sua execução, usando sua conta Windows. Não altera tabelas nem executa migrações.

Use dados de teste. POST cria registros, PUT edita e DELETE exclui sem lixeira. Cursos com disciplinas, disciplinas com tarefas e tarefas com histórico de tempo não podem ser excluídos: a API responde 409 para preservar os vínculos.

A tarefa separada **EduTrack: iniciar API local (consulta)** mantém gravações desativadas. Nesse modo, POST/PUT/DELETE acadêmicos retornarão 503.

## 1. Criar uma conta de teste

No Swagger, expanda **Autenticação → POST /api/auth/register**, clique em **Try it out**, preencha e clique em **Execute**:

~~~json
{
  "nome": "Aluno de teste",
  "email": "aluno.teste@example.com",
  "senha": "Troque-por-uma-senha-de-teste",
  "cpf": "00000000191"
}
~~~

Resposta esperada: **201**. Nome, e-mail, CPF matematicamente válido e senha são obrigatórios. O CPF de exemplo é apenas para testes matemáticos e não comprova titularidade; o número é descartado. A senha precisa de 10 a 128 caracteres. Se o e-mail já existir, faça login ou use outro e-mail de teste. Não existe uma conta administrativa pronta.

Se `GET /api/auth/options` informar verificação obrigatória, use uma caixa de e-mail própria/autorizada, não example.com. Chame `POST /api/auth/request-verification` com e-mail e senha e depois `POST /api/auth/verify-email` com esses campos e `codigo` recebido. Consulte [CPF_E_EMAIL.md](CPF_E_EMAIL.md). Sem confirmar, o login responde 403. O cadastro responde 503 se a verificação estiver ativa sem SendGrid configurado.

## 2. Entrar e autorizar as rotas

Execute **POST /api/auth/login** com o mesmo e-mail e senha:

~~~json
{
  "email": "aluno.teste@example.com",
  "senha": "Troque-por-uma-senha-de-teste"
}
~~~

Copie **somente o valor** de access_token retornado. Clique em **Authorize**, cole em **Value**, confirme **Authorize** e feche o diálogo. Não digite a palavra Bearer; o Swagger a adiciona.

Execute **GET /api/me**. Deve retornar a conta usada no login, sem senha ou hash.

O token expira em 20 minutos na configuração padrão. Refaça o login e substitua o token quando receber 401. Sem uma chave JWT fixa no backend, reiniciar o servidor também invalida os tokens. O Swagger não mantém a autorização depois de recarregar a página. Não compartilhe capturas que exibam o token.

O login do site usa cookie HttpOnly; ele é separado da autorização do Swagger. Faça login no Swagger mesmo que já esteja no dashboard.

## 3. Curso → disciplina → tarefa

### Curso: POST /api/courses

~~~json
{
  "nome": "Ciência da Computação",
  "instituicao": "Faculdade de teste",
  "data_inicio": "2026-08-01",
  "data_fim": "2026-12-15"
}
~~~

Copie o id da resposta.

### Disciplina: POST /api/disciplines

Substitua o marcador pelo UUID real do curso, mantendo as aspas:

~~~json
{
  "curso_id": "COLE_O_ID_DO_CURSO",
  "nome": "Banco de Dados",
  "professor": "Professor de teste",
  "carga_horaria": 40
}
~~~

Copie o id da disciplina.

### Tarefa: POST /api/tasks

~~~json
{
  "disciplina_id": "COLE_O_ID_DA_DISCIPLINA",
  "titulo": "Revisar consultas JOIN",
  "descricao": "Praticar INNER JOIN e LEFT JOIN.",
  "data_prevista": "2026-10-12T20:00:00-03:00",
  "status": "pendente",
  "minutos_estimados": 45
}
~~~

Os marcadores acima são ilustrativos e não são UUIDs válidos. Para não definir prazo, envie data_prevista como null. O horário precisa incluir o fuso; a API retorna datas em UTC.

Consulte GET /api/courses, /api/disciplines e /api/tasks. Use limit e offset para paginação.

## 4. Editar e excluir

PUT /api/tasks/{item_id} exige o ID da tarefa no caminho e todos os campos editáveis no corpo. Para concluir, mantenha os demais valores e altere status para **concluida**. Para reabrir, use **pendente**. Outros estados: **em_andamento** e **cancelada**.

PUT não é atualização parcial: campos opcionais omitidos podem ser limpos. Não envie id, usuario_id, senha_hash, criado_em ou concluido_em no corpo de edição.

PUT /api/me aceita somente nome.

Exclua, se não houver histórico: tarefa → disciplina → curso. Não existe DELETE de usuário nesta versão. Para contas de teste que você criar manualmente, a limpeza do banco deve ser planejada separadamente.

## 5. Plano de estudo, sem gastar créditos de IA

Execute POST /api/edu-ia/study-plan com uma tarefa pendente:

~~~json
{
  "data_inicio": "2026-10-05",
  "dias": 7,
  "minutos_por_dia": 60,
  "objetivo": "Revisar SQL e organizar minhas entregas",
  "usar_ia": false,
  "enviar_dados_ia": false
}
~~~

Ajuste a data para o período que quiser. O resultado usa somente os registros da conta autenticada, indica origem **regras** e não altera tarefas nem agenda. Chat generativo só funciona após configurar OPENAI_API_KEY e OPENAI_MODEL no backend e autorizar o envio do contexto. Nenhuma chave está incluída nesta entrega.

## 6. Sessões e relatórios

GET /api/study-sessions lista sessões da conta. GET /api/dashboard retorna totais e progresso.

POST /api/study-sessions exige tarefa_id, iniciado_em e finalizado_em, com fuso e término no passado. Duração permitida: 1 a 240 minutos. O banco calcula duracao_minutos; não envie esse campo.

Para repetir com segurança a mesma sessão, use o mesmo UUID no cabeçalho **Idempotency-Key** e os mesmos dados. Repetir sem essa chave pode criar outro registro. Reutilizar a chave para dados diferentes retorna 409.

## Respostas mais comuns

| Código | Significado |
|---|---|
| 200 / 201 / 204 | Consulta/edição, criação ou exclusão concluída. |
| 401 | Login necessário, token inválido ou expirado. |
| 403 | Origem da escrita não autorizada no proxy do site. |
| 404 | Registro inexistente ou de outra conta. |
| 409 | E-mail já usado, vínculo que impede exclusão ou chave de sessão em conflito. |
| 422 | Campo inválido, desconhecido ou obrigatório ausente. |
| 429 | Limite de solicitações; aguarde o período indicado. |
| 503 | API/banco indisponível, escrita desativada ou IA sem configuração. |

Se aparecer “conexão recusada”, inicie **Iniciar EduTrack.cmd**. Se o terminal informar falha de banco, confira o serviço SQL Server (SQLEXPRESS) e suas permissões. Não desative firewall ou autenticação para contornar erros.

## Limites desta etapa

A integração é local. O endereço público anterior não foi modificado. CPF, telefone, envio de códigos, recuperação de senha, administração real, pagamentos, importação automática do navegador e persistência de planos/chat continuam fora desta entrega. Os dados antigos do navegador foram preservados, sem serem associados automaticamente a uma conta.
