# Especificação da área administrativa

## Purpose

Definir o acesso e as responsabilidades do painel administrativo do EduTrack.

## Requirements

### Requirement: Acesso exclusivo de administrador

O sistema SHALL exibir e permitir operações da rota `/gerenciamento` somente para contas autenticadas com `role=admin` validado pela API.

#### Scenario: Administrador autorizado

- **WHEN** uma conta autenticada com `role=admin` abre `/gerenciamento`
- **THEN** o sistema apresenta indicadores, usuários, verificações, catálogo e estado das integrações

#### Scenario: Aluno tenta abrir a administração

- **WHEN** uma conta com `role=student` solicita a rota ou um endpoint administrativo
- **THEN** a interface mostra acesso restrito e a API responde com `403`

#### Scenario: Visitante não autenticado

- **WHEN** uma pessoa sem sessão válida solicita um endpoint administrativo
- **THEN** a API responde com `401`

### Requirement: Autorização no servidor

A API SHALL verificar a função administrativa em cada endpoint `/api/admin/*` e SHALL NOT confiar em valores de `localStorage` ou parâmetros enviados pelo navegador.

#### Scenario: Função adulterada no navegador

- **WHEN** uma pessoa altera localmente um campo visual de perfil
- **THEN** a API mantém a operação bloqueada porque a autorização é determinada pela sessão no servidor

### Requirement: Gestão auditável

O sistema SHALL registrar alterações administrativas de situação, função e catálogo com administrador responsável e data.

#### Scenario: Alteração de conta

- **WHEN** um administrador autorizado altera a situação ou função de um usuário
- **THEN** a API registra a ação em histórico de auditoria

