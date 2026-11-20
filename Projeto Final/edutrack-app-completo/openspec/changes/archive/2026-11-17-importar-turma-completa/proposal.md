# Importação completa de uma turma

## Why

O aluno precisa importar uma turma de uma vez, incluindo publicações e links de anexos, sem selecionar cada atividade e sem depender de um curso previamente cadastrado.

## What Changes

- Modos completo, todas as atividades e seleção manual.
- Criação opcional do curso na mesma transação da disciplina, tarefas e conteúdos.
- Biblioteca paginada na disciplina, filtrada por atividades, materiais e avisos.
- Escopos adicionais de leitura, consentimento renovado, migração aditiva 005 e flag desligada por padrão.
- Preservação de edições pessoais e deduplicação. Importação pontual; não promete sincronização em segundo plano.

## Impact

FastAPI, BFF, frontend, OpenAPI, modelo de dados e documentação. Exige aprovação antes de aplicar a migração, alterar permissões Google e publicar na VPS. Não muda o Classroom nem ativa IA generativa.
