## ADDED Requirements

### Requirement: Importação completa em uma ação

O sistema SHALL consultar novamente todas as atividades publicadas, materiais, avisos e tópicos acessíveis da turma escolhida e gravar disciplina, tarefas e conteúdos em uma transação. O aluno SHALL poder usar um curso próprio existente ou criar um curso nessa operação.

#### Scenario: Conta sem curso

- **WHEN** o aluno informa o nome do novo curso e confirma a importação completa
- **THEN** curso, disciplina, tarefas e biblioteca são gravados juntos após concluir a consulta Google

#### Scenario: Atividade publicada após a prévia

- **WHEN** há nova atividade acessível antes da consulta final de importação
- **THEN** ela é incluída automaticamente, sem exigir seleção individual

#### Scenario: Uma página falha

- **WHEN** há erro, permissão insuficiente ou excesso de limite em qualquer recurso solicitado
- **THEN** nenhum curso, disciplina, tarefa ou conteúdo dessa operação é gravado

### Requirement: Conteúdos de leitura separados das tarefas pessoais

O sistema SHALL armazenar publicações e links de anexos por titular e disciplina, com filtros e paginação. Não SHALL baixar arquivos nem importar notas, entregas, comentários ou lista de alunos.

#### Scenario: Importar novamente

- **WHEN** a mesma turma é importada novamente
- **THEN** publicações são atualizadas e novas atividades são adicionadas sem duplicar registros nem sobrescrever tarefas editadas ou concluídas pelo aluno

#### Scenario: Outro titular

- **WHEN** outro aluno tenta acessar a biblioteca por ID
- **THEN** a API retorna 404 e não revela conteúdo

### Requirement: Renovação explícita de consentimento

O sistema SHALL exigir a ativação da importação completa e os escopos de leitura de materiais, avisos e tópicos. Uma conexão básica existente não SHALL ser tratada como autorização ampliada.

#### Scenario: Conexão antiga

- **WHEN** o aluno conectado anteriormente solicita a importação completa
- **THEN** a interface solicita nova autorização Google, preservando os dados e a importação básica
