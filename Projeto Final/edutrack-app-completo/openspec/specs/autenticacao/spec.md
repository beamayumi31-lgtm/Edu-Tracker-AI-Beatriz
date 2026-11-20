# Especificação de autenticação

## Purpose

Definir os fluxos de acesso, cadastro, verificação de contato e recuperação de senha do EduTrack.

## Requirements

### Requirement: Cadastro de aluno

O sistema SHALL permitir o cadastro público de uma conta de aluno com nome, e-mail, senha, CPF válido, telefone e canal de verificação.

#### Scenario: Cadastro válido

- **WHEN** uma pessoa informa dados válidos e aceita os termos
- **THEN** o sistema inicia a verificação por e-mail ou SMS e atribui o perfil `student`

#### Scenario: CPF inválido

- **WHEN** o CPF não possui formato e dígitos verificadores válidos
- **THEN** o sistema bloqueia o cadastro e informa o campo que precisa ser corrigido

### Requirement: Proteção da senha

A API SHALL armazenar somente `senha_hash` e SHALL NOT registrar ou persistir a senha em texto puro.

#### Scenario: Persistência de credencial

- **WHEN** uma conta é criada ou a senha é redefinida
- **THEN** a API calcula um hash seguro antes de gravar a credencial no SQL Server

### Requirement: Verificação de contato

O sistema SHALL confirmar a posse do e-mail ou telefone por um código temporário, com expiração e limite de tentativas.

#### Scenario: Código aceito

- **WHEN** o usuário informa um código válido e não expirado
- **THEN** o contato é marcado como verificado e o código não pode ser reutilizado

#### Scenario: Código inválido ou expirado

- **WHEN** o código não confere, expirou ou excedeu o limite de tentativas
- **THEN** a API rejeita a verificação sem revelar dados sensíveis

### Requirement: Recuperação de senha

O sistema SHALL permitir solicitar e concluir a recuperação de senha sem revelar se um e-mail está cadastrado.

#### Scenario: Solicitação de recuperação

- **WHEN** uma pessoa envia um endereço de e-mail
- **THEN** a interface apresenta uma resposta neutra e a API envia instruções somente se a conta existir

#### Scenario: Link válido de recuperação

- **WHEN** o titular utiliza um token válido dentro de 15 minutos e informa uma senha de 10 a 128 caracteres
- **THEN** a API consome o token e atualiza o hash da senha na mesma transação, exigindo novo login

#### Scenario: Link expirado ou reutilizado

- **WHEN** o token expirou, já foi utilizado ou não existe
- **THEN** a API recusa a alteração e orienta solicitar outro link sem modificar a conta

#### Scenario: Sessão anterior à troca

- **WHEN** um token de sessão emitido antes da redefinição é apresentado
- **THEN** a API recusa a sessão, preservando os registros acadêmicos e o perfil da conta


### Requirement: Acesso adulto fechado por aprovação

O sistema SHALL disponibilizar um modo restrito a contas adultas previamente aprovadas, SHALL manter cadastro público fechado nesse modo e SHALL exigir e-mail confirmado e aprovação no servidor em cada acesso autenticado. Avisos ou autodeclarações na interface não SHALL substituir essa autorização.

#### Scenario: Conta removida da lista

- **WHEN** uma conta com sessão existente não pertence à lista aprovada
- **THEN** as rotas autenticadas e integrações recusam o acesso sem apagar seus dados

#### Scenario: Configuração restrita incompleta

- **WHEN** o modo adulto fechado está habilitado sem lista válida ou com público incompatível
- **THEN** o acesso falha fechado e o Gemini não é considerado configurado

#### Scenario: Cadastro público fechado

- **WHEN** o modo adulto fechado está ativo
- **THEN** o servidor recusa cadastros e a interface orienta entrar com uma conta previamente autorizada, sem publicar a lista de usuários
