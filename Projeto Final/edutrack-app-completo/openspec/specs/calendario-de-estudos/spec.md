# Especificação do calendário de estudos

## Purpose

Ocupar o topo do dashboard com um histórico útil de estudo, inspirado no calendário de contribuições do GitHub e adaptado à identidade do EduTrack. A funcionalidade utiliza as sessões já carregadas da conta autenticada, sem conectar ou importar dados do GitHub.

## Requirements

### Requirement: Cabeçalho compacto

O dashboard SHALL substituir o banner ilustrado grande por uma saudação compacta, preservando os atalhos para foco, primeiro curso e Edu IA e os indicadores existentes.

#### Scenario: Conta sem cursos

- **WHEN** uma conta sem cursos abre o dashboard
- **THEN** o cabeçalho oferece adicionar o primeiro curso e o calendário não insere sessões demonstrativas

### Requirement: Histórico por dia local

O calendário SHALL agrupar sessões concluídas pelo dia local da conclusão, contar IDs únicos e desconsiderar datas inválidas, futuras e minutos não positivos ou não finitos.

#### Scenario: Duas sessões no mesmo dia

- **WHEN** duas sessões distintas de 25 minutos terminam no mesmo dia local
- **THEN** o dia mostra 50 minutos, duas sessões e é contado como um único dia de estudo

#### Scenario: Registro repetido ou inválido

- **WHEN** a lista contém um ID repetido, data inválida ou sessão futura
- **THEN** o registro não aumenta o histórico, os totais nem a ofensiva

### Requirement: Períodos e intensidade

O calendário SHALL iniciar em 12 meses e permitir selecionar 3 ou 6 meses. SHALL mostrar semanas de segunda a domingo e níveis de intensidade de 0, 1–24, 25–49, 50–99 e 100 ou mais minutos por dia. Os totais SHALL corresponder ao período selecionado; a ofensiva SHALL manter a regra atual independente do filtro.

#### Scenario: Alteração do período

- **WHEN** o aluno seleciona os últimos três meses
- **THEN** o calendário e os totais exibem apenas os dias desse intervalo até hoje, sem consultar novamente a API

#### Scenario: Virada de mês ou ano bissexto

- **WHEN** o período atravessa fevereiro, o fim do ano ou uma mudança de horário local
- **THEN** cada data aparece uma única vez, sem lacunas nem inclusão de dias futuros

### Requirement: Interação acessível e responsiva

O calendário SHALL permitir consultar data, minutos e quantidade de sessões por mouse, toque e teclado. SHALL oferecer uma única parada de Tab na grade, setas para dias/semanas e Home/End para os limites. SHALL preservar os temas claro/escuro e permitir rolagem horizontal apenas na grade quando necessário.

#### Scenario: Navegação por teclado

- **WHEN** o aluno foca o calendário e pressiona uma seta
- **THEN** o foco e os detalhes mudam para a data correspondente dentro dos limites do período

#### Scenario: Tela estreita

- **WHEN** a largura não comporta todo o ano
- **THEN** o aluno pode deslizar a grade para consultar dias anteriores e a página não ganha rolagem horizontal por causa do calendário

### Requirement: Dados autorizados e ausência de efeitos externos

O componente SHALL receber somente as sessões fornecidas pela integração acadêmica existente. SHALL NOT alterar o banco, gerar sessões, importar atividades de outra conta ou exigir acesso ao GitHub. Os controles de autenticação da API SHALL permanecer ativos.

#### Scenario: Conta sem histórico

- **WHEN** a conta autenticada não possui sessões concluídas
- **THEN** todos os dias permanecem sem intensidade e os totais são zero

#### Scenario: Sessão não autorizada

- **WHEN** a autenticação falha ao carregar o dashboard
- **THEN** o fluxo existente de login é mantido, sem usar dados de outro usuário ou criar um modo de acesso alternativo
