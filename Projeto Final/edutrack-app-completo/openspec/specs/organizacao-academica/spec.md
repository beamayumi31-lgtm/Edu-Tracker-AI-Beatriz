# Especificação de organização acadêmica

## Purpose

Definir como cada estudante organiza e acompanha seus próprios cursos, disciplinas, tarefas e sessões de estudo.

## Requirements

### Requirement: Isolamento por usuário

A API SHALL vincular cursos, disciplinas, tarefas e sessões a `usuario_id` e SHALL retornar somente registros pertencentes ao usuário autenticado.

#### Scenario: Consulta dos próprios dados

- **WHEN** um estudante autenticado abre o painel
- **THEN** a API retorna apenas os registros vinculados ao seu identificador

#### Scenario: Tentativa de acessar outro usuário

- **WHEN** um estudante solicita um registro pertencente a outra conta
- **THEN** a API rejeita a operação sem expor o conteúdo do registro

### Requirement: Hierarquia acadêmica

O sistema SHALL permitir que cursos contenham disciplinas e que tarefas possam ser vinculadas a uma disciplina do mesmo usuário.

#### Scenario: Tarefa vinculada

- **WHEN** o estudante cria uma tarefa para uma disciplina válida
- **THEN** a tarefa aparece na disciplina, na lista geral e nos indicadores do painel

### Requirement: Progresso responsivo

A interface SHALL recalcular os resumos conforme cursos, disciplinas, tarefas e sessões forem adicionados ou atualizados.

#### Scenario: Primeiro registro acadêmico

- **WHEN** um novo usuário adiciona seu primeiro curso
- **THEN** o estado vazio é substituído pelos dados reais sem inserir conteúdo demonstrativo duplicado

### Requirement: Sugestões de cursos

O sistema SHALL manter sugestões gerais separadas dos cursos pessoais e SHALL exigir uma ação explícita para adicionar uma sugestão ao painel do aluno.

#### Scenario: Adicionar uma sugestão

- **WHEN** o estudante escolhe adicionar um curso sugerido
- **THEN** uma cópia personalizável é criada para esse estudante sem realizar matrícula externa

