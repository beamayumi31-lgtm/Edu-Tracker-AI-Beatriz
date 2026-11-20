## ADDED Requirements

### Requirement: Proposta sem implementação
O exercício SHALL descrever o lançamento de notas sem criar tabelas, endpoints ou permissões reais.
#### Scenario: Planejamento entregue
- **WHEN** o exercício é revisado
- **THEN** contém entidade candidata, POST e restrições de autorização, rotulados como não implementados
#### Scenario: Sem autorização de implementação
- **WHEN** ainda não existe definição do vínculo professor/turma
- **THEN** nenhuma permissão de lançamento de notas é concedida
