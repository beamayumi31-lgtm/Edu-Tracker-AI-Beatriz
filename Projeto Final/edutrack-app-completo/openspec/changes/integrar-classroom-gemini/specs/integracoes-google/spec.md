## ADDED Requirements

### Requirement: Conexão e importação por aluno

O EduTrack SHALL oferecer conexão Google Classroom individual, importação explícita de turmas/atividades em curso próprio e desconexão sem eliminar dados acadêmicos.

#### Scenario: Importação repetida

- **WHEN** o aluno importa a mesma origem novamente
- **THEN** o sistema preserva registros existentes e evita duplicação

#### Scenario: Dados não autorizados

- **WHEN** a seleção contém curso de outro aluno ou atividade indisponível no Google
- **THEN** a operação é rejeitada sem gravar resultados parciais
