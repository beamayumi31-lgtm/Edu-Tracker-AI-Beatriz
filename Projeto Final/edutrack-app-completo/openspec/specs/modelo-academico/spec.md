# Modelo acadêmico Specification

## Purpose

Definir a propriedade, os campos e as relações de disciplinas e tarefas acadêmicas do aluno, preservando o contrato CRUD e o isolamento entre contas.

## Requirements


### Requirement: Disciplinas pertencentes ao aluno
A API SHALL manter nome, professor opcional e carga horária opcional não negativa para cada disciplina vinculada ao curso e usuario_id.
#### Scenario: Disciplina válida
- **WHEN** o aluno cria uma disciplina em seu curso
- **THEN** os campos são persistidos e retornados apenas ao proprietário
#### Scenario: Curso de outro aluno
- **WHEN** uma conta informa curso_id alheio
- **THEN** a criação é recusada sem alterar o curso


### Requirement: Tarefas e CRUD protegido
A API SHALL manter tarefas vinculadas à disciplina do mesmo aluno, com título, descrição, prazo e status validado, e permitir CRUD autenticado de disciplinas.
#### Scenario: Ciclo CRUD
- **WHEN** o aluno cria, lê, edita e exclui uma disciplina de demonstração
- **THEN** cada operação retorna o estado esperado e a exclusão é verificável
#### Scenario: Acesso cruzado
- **WHEN** outra conta tenta alterar a disciplina ou vincular uma tarefa
- **THEN** não recebe acesso nem modifica os dados
