# CPF e confirmação de e-mail — localhost

## Implementado no código

- Cadastro exige CPF: formato e dígitos são conferidos no frontend e novamente na API. O CPF é descartado: não vai para banco, cookie, localStorage ou resposta HTTP. Isso não consulta titularidade/situação na Receita nem impede contas diferentes de utilizarem o mesmo CPF.
- Código de seis dígitos gerado com aleatoriedade criptográfica. Validade de dez minutos; cinco tentativas por código; intervalo mínimo de 60 segundos e até cinco envios por conta por hora.
- O banco guarda HMAC do código (não texto puro), validade, contadores e confirmação. A chave persistente JWT do servidor protege o HMAC; mudar essa chave invalida desafios pendentes e sessões.
- Solicitar/reenviar/confirmar exige e-mail e senha corretos. Um reenvio substitui o desafio anterior. A confirmação é atômica e de uso único.
- Com verificação ativada, login e rotas autenticadas bloqueiam contas não confirmadas, inclusive contas/sessões anteriores à ativação.
- SendGrid recebe somente destinatário e conteúdo da mensagem; nunca CPF, senha ou dados acadêmicos. Rastreamento de abertura/cliques desativado.
- HTTP 202 do SendGrid significa aceitação para envio, não entrega garantida. Falhas não viram sucesso na interface e não expõem o corpo de erro do provedor.

## Estado da ativação — 06/10/2026

Após autorização do titular, a migração `001_verificacoes_email.sql` foi aplicada em `DESKTOP-PBP3G2U\SQLEXPRESS / EduTrackIA`. As seis tabelas anteriores estavam vazias e permaneceram inalteradas; a nova tabela tem nove colunas, está vazia e sua chave estrangeira está habilitada e validada. A checagem ORM passou nas sete tabelas sem gravar registros.

O remetente **EduTrack / antoniombrites2716@gmail.com** está verificado no SendGrid. Após autorização, foi criada a chave **EduTrack localhost — envio restrito**, somente com `Mail Send`, sem acesso administrativo ou a agendamentos. A primeira chave foi revogada após exposição em retorno técnico; somente a substituta permanece ativa.

A chave atual e o segredo JWT persistente ficam em `%LOCALAPPDATA%/EduTrack/backend.env`, fora do Git e do OneDrive. O inicializador local carrega esse arquivo somente no processo Python; não passa seus valores ao frontend. Variáveis explicitamente definidas pelo operador têm prioridade. O assistente temporário de configuração foi encerrado após salvar.

A confirmação está **ativada no localhost**: tanto a API quanto o proxy retornaram `email_verification_required=true` e `email_delivery_configured=true`. `/ready`, `/docs` e `/cadastro` responderam HTTP 200. Um e-mail de teste autorizado foi aceito pelo SendGrid (HTTP 202), com assunto **EduTrack — teste de envio local**. Isso não confirma entrega na caixa de entrada nem verifica uma conta: o teste não criou conta nem alterou registros de alunos.

O fluxo completo de códigos continua coberto por testes com envio simulado. A confirmação real de uma conta deve ser feita pelo titular no cadastro, usando o código recebido. O site público não foi alterado.

Validação final desta configuração: **74 testes da API passaram**, Ruff sem erros e `pip check` sem dependências quebradas. O histórico do SendGrid ainda não apresentou registro do teste na consulta imediata; a entrega não foi presumida. O assistente temporário encerrou e apenas os servidores locais do projeto permaneceram escutando em loopback.

## Configuração em outra instalação

O recurso está desativado por padrão para não alterar silenciosamente o banco e o acesso atual. A migração não roda ao iniciar o servidor.

1. **Concluído nesta máquina:** migração aplicada e conferida. Em outra instalação, aplicar `Backend/migrations/001_verificacoes_email.sql` somente após autorização e backup, exclusivamente em `localhost\SQLEXPRESS`, banco `EduTrackIA`.
2. No SendGrid, verificar o remetente por **Single Sender Verification**, adequado aos testes sem domínio próprio. Essa etapa pode pedir dados de contato/endereço: devem ser fornecidos pelo titular.
3. Criar uma chave restrita a **Mail Send** com confirmação do titular. Não usar Full Access, não colar a chave em chat nem no frontend.
4. No Windows, preferir `%LOCALAPPDATA%/EduTrack/backend.env`, fora de pastas sincronizadas. `python -m edutrack.run` carrega esse arquivo. A alternativa portátil é `Backend/.env` (ignorado pelo Git), sem sincronizá-lo. Nunca colocar segredos em `NEXT_PUBLIC_*`, frontend ou documentação:

```dotenv
EDUTRACK_EMAIL_VERIFICATION_ENABLED=true
SENDGRID_API_KEY=<chave privada, preenchida localmente>
EDUTRACK_EMAIL_FROM=<remetente verificado no SendGrid>
EDUTRACK_EMAIL_FROM_NAME=EduTrack
EDUTRACK_JWT_SECRET=<segredo aleatório persistente com pelo menos 32 caracteres>
```

O assistente `Backend/scripts/configure_local_email.py` é uma ferramenta local de uso único: escuta somente em `127.0.0.1`, exige uma rota aleatória e mesma origem no envio, recebe a chave por campo de senha e encerra após salvar ou em dez minutos. Não imprime a chave e não substitui arquivo existente sem a opção explícita `--replace-revoked-key`, que deve ser usada somente após revogação autorizada. A substituição preserva o segredo JWT. Não é um endpoint permanente do EduTrack.

5. Reiniciar o inicializador local. `/ready` verifica também a tabela quando o recurso está ativo. Não trocar o endereço da API: permanece em `http://127.0.0.1:8000`.
6. Testar um envio real para um endereço autorizado pelo titular e confirmar no site. O código não é exposto no Swagger nem em logs. Conferir caixa de entrada e spam.

Não há publicação, domínio, alteração de DNS, webhook ou túnel público nesta implementação. O e-mail contém um código, não um link para localhost; digite-o no computador onde o EduTrack está rodando.

## API / Swagger

- `GET /api/auth/options`: informa se a verificação é obrigatória e se há configuração de envio, sem revelar segredos.
- `POST /api/auth/register`: nome, e-mail, senha e CPF. Não envia sozinho: o frontend solicita o código após criar a conta.
- `POST /api/auth/request-verification`: e-mail e senha. Retorna 202 quando o serviço aceita o envio; 429 para limites; 503 se desativado/não configurado/falha no envio.
- `POST /api/auth/verify-email`: e-mail, senha e `codigo`. Confirma a conta, mas não retorna token.
- `POST /api/auth/login`: retorna 403 com `EMAIL_VERIFICATION_REQUIRED` até a confirmação, quando o recurso está ativo.

## Testes e limites

Os testes de CPF e e-mail usam SQLite descartável e envio simulado. Nenhum teste automatizado dispara e-mail real. Para rodar: `Backend/.venv/Scripts/python.exe -m pytest -q` na pasta da API.

O limitador por IP é destinado a uma instância local; publicação multiworker requer limitador compartilhado. A entrega real depende da configuração e reputação do remetente e de eventuais limites do plano SendGrid. Verificação de e-mail prova acesso à caixa, não identidade civil. Recuperação de senha, SMS, consulta oficial de CPF e unicidade de CPF não fazem parte deste fluxo.

Referências oficiais: [Mail Send API](https://www.twilio.com/docs/sendgrid/api-reference/mail-send/mail-send) e [Single Sender Verification](https://www.twilio.com/docs/sendgrid/ui/sending-email/sender-verification).
