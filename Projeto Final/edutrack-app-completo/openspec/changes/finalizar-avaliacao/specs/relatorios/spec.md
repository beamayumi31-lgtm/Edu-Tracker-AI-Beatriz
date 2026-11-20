## MODIFIED Requirements

### Requirement: Semana local

O sistema SHALL calcular semanas de segunda-feira a domingo no fuso do estudante usando somente sessões concluídas da conta autenticada.

#### Scenario: Mesmo dia em semanas diferentes

- **WHEN** há sessões em duas segundas-feiras de semanas diferentes
- **THEN** cada sessão contribui somente para a semana correspondente

#### Scenario: Sem registros

- **WHEN** a semana não possui sessões válidas
- **THEN** o sistema mostra zero, sem barras ou dados fictícios

### Requirement: Navegação e exportação

O estudante SHALL poder consultar semanas passadas e baixar um CSV cujas datas, minutos e sessões correspondam ao período visível.

#### Scenario: Semana anterior

- **WHEN** o estudante muda a semana
- **THEN** o intervalo, os totais, o gráfico, a tabela acessível e o CSV usam o mesmo conjunto de dados

#### Scenario: Dados inválidos

- **WHEN** uma sessão é duplicada, futura, inválida ou tem duração não positiva
- **THEN** o cálculo desconsidera o registro sem inventar tempo estudado

### Requirement: Progresso acumulado explícito

O sistema SHALL identificar a comparação de disciplinas como progresso acumulado, separado do período semanal.

#### Scenario: Consulta por disciplina

- **WHEN** o aluno consulta conclusão por disciplina
- **THEN** o indicador considera tarefas válidas da conta e informa que utiliza todas as datas
