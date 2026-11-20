## ADDED Requirements

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
