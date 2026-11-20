# Dicionário de dados — EduTrack

Modelo alvo gerado do código, sem consultar valores de usuários. SQL Server; datas DATETIME2 seguem UTC.

O modelo alvo contém 14 tabelas. As tabelas Google dependem das migrações 004 e 005. A existência no modelo não comprova aplicação no banco; consulte ATIVACAO_INTEGRACOES.md para o estado de cada ambiente.

CPF é validado e descartado. Senhas são armazenadas somente como hash Argon2; códigos de confirmação usam HMAC e tokens de recuperação usam SHA-256. Tokens Google e verificadores PKCE usam Fernet com vinculação ao usuário e chave independente do JWT.

## usuarios

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `nome` | `NVARCHAR(150)` | Não | — |
| `email` | `NVARCHAR(255)` | Não | UNIQUE |
| `senha_hash` | `VARCHAR(255)` | Não | — |
| `role` | `VARCHAR(16)` | Não | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `atualizado_em` | `DATETIME2(3)` | Não | — |

Restrições: role IN ('student', 'admin').

## autorizacoes_google

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `state_hash` | `VARCHAR(64)` | Não | PK |
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | UNIQUE; FK → usuarios.id |
| `verifier_cifrado` | `VARCHAR(max)` | Não | — |
| `expira_em` | `DATETIME2(3)` | Não | — |
| `usado_em` | `DATETIME2(3)` | Sim | — |

Restrições: .

## conexoes_google

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | PK; FK → usuarios.id |
| `google_sub` | `VARCHAR(128)` | Não | — |
| `email` | `VARCHAR(255)` | Não | — |
| `refresh_cifrado` | `VARCHAR(max)` | Não | — |
| `versao` | `UNIQUEIDENTIFIER` | Não | — |
| `conteudo_autorizado` | `BIT` | Não | — |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `atualizado_em` | `DATETIME2(3)` | Não | — |

Restrições: .

## convites_administrador

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `email` | `NVARCHAR(255)` | Não | PK |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `expira_em` | `DATETIME2(3)` | Não | — |
| `usado_em` | `DATETIME2(3)` | Sim | — |
| `usuario_id` | `UNIQUEIDENTIFIER` | Sim | FK → usuarios.id |

Restrições: (usado_em IS NULL AND usuario_id IS NULL) OR (usado_em IS NOT NULL AND usuario_id IS NOT NULL); expira_em > criado_em.

## cursos

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → usuarios.id |
| `nome` | `NVARCHAR(150)` | Não | — |
| `instituicao` | `NVARCHAR(200)` | Sim | — |
| `data_inicio` | `DATETIME` | Sim | — |
| `data_fim` | `DATETIME` | Sim | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `atualizado_em` | `DATETIME2(3)` | Não | — |

Restrições: data_inicio IS NULL OR data_fim IS NULL OR data_fim >= data_inicio.

## recuperacoes_senha

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → usuarios.id |
| `token_hash` | `VARCHAR(64)` | Não | UNIQUE |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `expira_em` | `DATETIME2(3)` | Não | — |
| `usado_em` | `DATETIME2(3)` | Sim | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |

Restrições: expira_em > criado_em.

## relatorios_semanais

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → usuarios.id |
| `periodo_inicio` | `DATETIME` | Não | — |
| `periodo_fim` | `DATETIME` | Não | — |
| `url_arquivo` | `NVARCHAR(2048)` | Sim | — |
| `gerado_em` | `DATETIME2(3)` | Não | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |

Restrições: .

## verificacoes_email

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | PK; FK → usuarios.id |
| `codigo_hash` | `VARCHAR(64)` | Sim | — |
| `expira_em` | `DATETIME2(3)` | Sim | — |
| `confirmado_em` | `DATETIME2(3)` | Sim | — |
| `enviado_em` | `DATETIME2(3)` | Sim | — |
| `janela_em` | `DATETIME2(3)` | Sim | — |
| `envios` | `INTEGER` | Não | — |
| `tentativas` | `INTEGER` | Não | — |
| `versao` | `INTEGER` | Não | — |

Restrições: .

## disciplinas

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `curso_id` | `UNIQUEIDENTIFIER` | Não | FK → cursos.id |
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → cursos.usuario_id; FK → usuarios.id |
| `nome` | `NVARCHAR(150)` | Não | — |
| `professor` | `NVARCHAR(150)` | Sim | — |
| `carga_horaria` | `INTEGER` | Sim | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `atualizado_em` | `DATETIME2(3)` | Não | — |

Restrições: carga_horaria IS NULL OR carga_horaria >= 0.

## conteudos_classroom

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → disciplinas.usuario_id; FK → usuarios.id |
| `google_sub` | `VARCHAR(128)` | Não | — |
| `turma_id` | `VARCHAR(128)` | Não | — |
| `origem_id` | `VARCHAR(128)` | Não | — |
| `tipo` | `VARCHAR(20)` | Não | — |
| `disciplina_id` | `UNIQUEIDENTIFIER` | Não | FK → disciplinas.id |
| `titulo` | `NVARCHAR(3000)` | Não | — |
| `descricao` | `NVARCHAR(max)` | Não | — |
| `topico` | `NVARCHAR(200)` | Não | — |
| `url` | `NVARCHAR(max)` | Sim | — |
| `anexos_json` | `NVARCHAR(max)` | Não | — |
| `publicado_em` | `DATETIME2(3)` | Sim | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `atualizado_em` | `DATETIME2(3)` | Não | — |

Restrições: tipo IN ('atividade', 'material', 'aviso').

## tarefas_academicas

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `disciplina_id` | `UNIQUEIDENTIFIER` | Não | FK → disciplinas.id |
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → disciplinas.usuario_id; FK → usuarios.id |
| `titulo` | `NVARCHAR(200)` | Não | — |
| `descricao` | `NTEXT` | Sim | — |
| `data_prevista` | `DATETIME2(3)` | Sim | — |
| `status` | `VARCHAR(20)` | Não | — |
| `minutos_estimados` | `INTEGER` | Sim | — |
| `concluido_em` | `DATETIME2(3)` | Sim | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `atualizado_em` | `DATETIME2(3)` | Não | — |

Restrições: status IN ('pendente', 'em_andamento', 'concluida', 'cancelada'); status <> 'concluida' OR concluido_em IS NOT NULL; minutos_estimados IS NULL OR minutos_estimados >= 0.

## vinculos_classroom_disciplinas

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → usuarios.id |
| `google_sub` | `VARCHAR(128)` | Não | — |
| `turma_id` | `VARCHAR(128)` | Não | — |
| `disciplina_id` | `UNIQUEIDENTIFIER` | Sim | FK → disciplinas.id |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |

Restrições: .

## registros_tempo_tarefa

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `tarefa_id` | `UNIQUEIDENTIFIER` | Não | FK → tarefas_academicas.id |
| `iniciado_em` | `DATETIME2(3)` | Não | — |
| `finalizado_em` | `DATETIME2(3)` | Sim | — |
| `duracao_minutos` | `INTEGER` | Sim | Calculado: CASE WHEN finalizado_em IS NULL THEN NULL ELSE DATEDIFF(minute, iniciado_em, finalizado_em) END |
| `criado_em` | `DATETIME2(3)` | Não | — |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |

Restrições: .

## vinculos_classroom_tarefas

| Campo | Tipo SQL Server | Nulo | Chave / regra |
|---|---|---|---|
| `usuario_id` | `UNIQUEIDENTIFIER` | Não | FK → usuarios.id |
| `google_sub` | `VARCHAR(128)` | Não | — |
| `turma_id` | `VARCHAR(128)` | Não | — |
| `atividade_id` | `VARCHAR(128)` | Não | — |
| `tarefa_id` | `UNIQUEIDENTIFIER` | Sim | FK → tarefas_academicas.id |
| `id` | `UNIQUEIDENTIFIER` | Não | PK |

Restrições: .

## Integridade e uso

Os vínculos compostos de disciplina/curso e tarefa/disciplina incluem usuario_id para impedir associações entre contas. Exclusões com dependências são recusadas pela API. O agente consulta somente dados da conta autenticada.

`relatorios_semanais` é uma estrutura reservada para artefatos persistidos. Atualmente a tela calcula o relatório a partir das sessões e permite exportar CSV; ela não grava nessa tabela.

Ver [DER](MODELO_DE_DADOS.md) e [recuperação de senha](RECUPERACAO_DE_SENHA.md).