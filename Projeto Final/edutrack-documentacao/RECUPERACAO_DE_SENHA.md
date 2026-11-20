# Recuperação de senha

O login oferece **Esqueci minha senha**. A pessoa informa seu e-mail, recebe um link de uso único e escolhe uma nova senha (10 a 128 caracteres). O link expira em 15 minutos. As sessões anteriores deixam de valer após a troca.

## Ativação

1. Revisar e aplicar, com autorização, `../edutrack-api/migrations/003_recuperacao_senha.sql` no banco correto. A migração apenas acrescenta a tabela de tokens e um índice; não modifica contas.
2. Configurar `EDUTRACK_PASSWORD_RESET_ENABLED=true` e `EDUTRACK_FRONTEND_URL` com a origem exata do site. Local: `http://localhost:3002`. Produção: HTTPS.
3. Manter JWT persistente, SendGrid e remetente verificado no ambiente privado do backend.
4. Reiniciar a API e conferir `/ready` e `/api/auth/options`.

## Contrato HTTP

| Rota | Corpo | Resultado |
|---|---|---|
| `POST /api/auth/forgot-password` | `email` | HTTP 202 e mensagem neutra, inclusive para e-mail desconhecido |
| `POST /api/auth/reset-password` | `token`, `senha` | Nova senha ou HTTP 400 para link inválido, expirado ou consumido |

As rotas estão no Swagger local. O proxy do frontend exige mesma origem e não exige sessão anterior. O token viaja no fragmento do link e é removido do endereço após a leitura; não aparece em logs HTTP de páginas. O banco armazena somente SHA-256. A senha é protegida com Argon2. Não há login automático após a troca e a confirmação de e-mail continua obrigatória quando habilitada.

## Limites e operação

- Intervalo mínimo de 60 segundos por conta; três solicitações por e-mail e dez por IP a cada 15 minutos.
- Consumo do token e alteração da senha na mesma transação; link anterior invalidado por nova solicitação.
- O limitador e a tarefa de e-mail operam numa única instância. Várias réplicas exigem limite distribuído e fila persistente.
- Falhas de envio não revelam a existência da conta. Nova solicitação pode ser feita depois do intervalo.
- A mudança da assinatura das sessões exige novo login de usuários que possuam tokens emitidos antes desta atualização.

Os testes automatizados usam e-mails capturados e SQLite em memória. Eles não comprovam entrega real pelo SendGrid. Uma conferência real deve ser feita pelo titular sem compartilhar senha ou link.
