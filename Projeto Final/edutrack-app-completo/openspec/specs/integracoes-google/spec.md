# Integrações Google Classroom

## Purpose

Permitir importação voluntária de turmas e atividades, com isolamento por aluno, sem modificar o Classroom.

## Requirements

### Requirement: Escopos concedidos e transparência

O sistema SHALL validar as permissões concedidas, aceitando apenas os nomes solicitados e seus equivalentes explicitamente suportados de leitura do próprio aluno. A interface SHALL explicar que a permissão Google agrupa atividades e notas, embora o EduTrack não consulte notas ou entregas.

#### Scenario: Retorno com nome alternativo do escopo de atividades

- **WHEN** o Google retorna `classroom.student-submissions.me.readonly` com identificação, e-mail e leitura de turmas
- **THEN** a conexão é validada sem ampliar o acesso solicitado, mantendo as demais verificações OAuth

#### Scenario: Permissão de outro público ou operação

- **WHEN** faltam as permissões requeridas e aparecem apenas escopos de professor, escrita ou nomes desconhecidos
- **THEN** a conexão é recusada e a credencial recebida tem sua revogação solicitada

### Requirement: Autorização individual protegida

O sistema SHALL exigir sessão EduTrack e OAuth Google individual com state de uso único, PKCE, escopos somente leitura e tokens cifrados no servidor.

#### Scenario: Retorno válido

- **WHEN** o aluno conclui a autorização na conta Google
- **THEN** a página remove a query e conclui o callback por POST de mesma origem, mantendo o cookie Strict

#### Scenario: Replay ou outro titular

- **WHEN** o callback usa state expirado, consumido ou de outro aluno
- **THEN** a API rejeita a conexão sem expor credenciais

### Requirement: Prévia e importação controladas

O sistema SHALL listar turmas ACTIVE do aluno e atividades PUBLISHED com paginação limitada, permitir seleção e revalidar origem e curso de destino antes da gravação.

#### Scenario: Conta sem curso cadastrado

- **WHEN** o aluno conectado ainda não possui cursos no EduTrack
- **THEN** ele pode buscar turmas e visualizar a prévia, escolhendo um curso próprio ou informando o nome de um novo curso para criá-lo na mesma importação

#### Scenario: Seleção confirmada

- **WHEN** o aluno escolhe um curso próprio, uma turma e atividades
- **THEN** a API cria a disciplina e tarefas correspondentes em transação

#### Scenario: Dados incompletos

- **WHEN** uma página falha, o limite é atingido ou um item foi removido
- **THEN** a API não importa resultados parciais

### Requirement: Preservação e isolamento

O sistema SHALL deduplicar por aluno, conta Google e IDs de origem, preservar edições e conclusões e não recriar automaticamente itens excluídos.

#### Scenario: Importar novamente

- **WHEN** a mesma seleção é importada outra vez
- **THEN** as tarefas pessoais existentes são preservadas sem duplicação ou sobrescrita; cópias de publicações podem ser atualizadas sem alterar essas tarefas

#### Scenario: Desconectar

- **WHEN** o aluno confirma a desconexão
- **THEN** a credencial local é removida, a revogação Google é tentada e os dados acadêmicos são preservados

### Requirement: Transparência e IA

O sistema SHALL informar que conclusão e edição são locais e SHALL excluir dados importados do contexto enviado automaticamente à IA externa.

#### Scenario: Plano completo

- **WHEN** o aluno deseja planejar atividades importadas
- **THEN** o planejador local usa seus dados sem enviá-los a um provedor generativo


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


### Requirement: Resultado visível de busca

O sistema SHALL exibir cada turma retornada em um botão selecionável na página, com contagem de resultados, estado de carregamento e mensagem para lista vazia ou falha.

#### Scenario: Google indisponível

- **WHEN** a consulta de turmas falha
- **THEN** o aluno vê uma mensagem e um botão de nova tentativa, e os resultados existentes não são apagados


### Requirement: Atualização sem perda das escolhas

O sistema SHALL preservar a turma selecionada, o destino e as atividades manuais ainda disponíveis quando a busca for atualizada. Uma turma que já foi importada SHALL usar o vínculo original para reimportação.

#### Scenario: Atualizar após preencher destino

- **WHEN** a mesma turma continua disponível após atualizar a busca
- **THEN** o nome do novo curso e as atividades válidas selecionadas continuam preenchidos


### Requirement: Importação com ação e retorno próximos

O sistema SHALL apresentar a confirmação antes da lista de atividades, explicar bloqueios e exibir falhas e sucesso junto da etapa correspondente, com atalho para a disciplina criada.

#### Scenario: Repetir importação

- **WHEN** o aluno importa novamente a mesma turma no vínculo original
- **THEN** o resultado explicita registros novos, conteúdos atualizados e registros pessoais preservados, sem duplicar os dados
