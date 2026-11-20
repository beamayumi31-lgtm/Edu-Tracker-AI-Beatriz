## ADDED Requirements

### Requirement: Progresso calculado em Python
O sistema SHALL calcular percentage como concluídas divididas pelo total elegível, excluindo canceladas e retornando zero para total zero.

#### Scenario: Script isolado
- **WHEN** o CLI recebe 3 concluídas e total 4
- **THEN** retorna JSON com percentage igual a 75 sem acessar banco ou rede

#### Scenario: Entrada inválida
- **WHEN** a quantidade concluída excede o total ou um valor é negativo
- **THEN** o CLI recusa a entrada com código de saída não zero

### Requirement: Busca por nome ou atraso
A API SHALL retornar somente disciplinas do aluno autenticado, por nome literal parcial OU existência de tarefa pendente atrasada, com paginação.

#### Scenario: União de resultados
- **WHEN** um nome corresponde à disciplina A e outra disciplina B possui tarefas atrasadas
- **THEN** a busca com os dois filtros retorna A e B uma única vez

#### Scenario: Acesso negado
- **WHEN** o solicitante não possui sessão válida
- **THEN** a busca responde 401 e não consulta dados de outros alunos

### Requirement: Relatório PDF privado
O sistema SHALL disponibilizar PDF com disciplina e progresso acumulado através de download autenticado, sem persistir documentos públicos.

#### Scenario: Relatório do próprio aluno
- **WHEN** o aluno solicita o link e baixa o relatório
- **THEN** recebe PDF legível com suas disciplinas, totais elegíveis e progresso, sem dados de terceiros

#### Scenario: Limite explícito
- **WHEN** a conta excede 500 disciplinas
- **THEN** a API responde erro claro em vez de gerar PDF incompleto

#### Scenario: Sessão inválida
- **WHEN** o link é aberto sem autenticação
- **THEN** a API responde 401 sem entregar o documento
