## MODIFIED Requirements

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

