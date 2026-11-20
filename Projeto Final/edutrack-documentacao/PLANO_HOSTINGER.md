# Plano de implantação — aprovado e executado

Inspeção inicial em 03/11/2026 pela sessão Chrome da Hostinger e SSH. O responsável aprovou posteriormente os serviços abaixo, a transferência SendGrid e os termos Microsoft. A implantação foi executada; consulte [resultado, evidências e operação](PUBLICACAO_HOSTINGER.md). As seções seguintes preservam o plano revisado antes da execução.

## Destino e recursos

- VPS própria `srv1834976.hstgr.cloud`, IP `179.197.79.177`, Ubuntu 24.04 LTS, KVM 2.
- 2 núcleos, 8 GB RAM, 100 GB de disco. Na inspeção: aproximadamente 7 GB de memória disponível e 90 GB livres no disco.
- Serviços existentes: Nginx, CRM Adonai (Docker/PostgreSQL) e envio de leads. Permanecem com seus arquivos, volumes e portas.
- Porta 3333 do CRM e porta 8787 do serviço Python já utilizadas. Reservar 3002 para EduTrack web, 8000 para a API e 14330 para SQL Server, todas em loopback.
- O DNS de `srv1834976.hstgr.cloud` já aponta para a VPS. URL proposta: `https://srv1834976.hstgr.cloud`, sem compra de domínio nem alteração de DNS. A emissão HTTPS ainda deve ser validada.
- Os domínios listados no painel pertencem a contas compartilhadas; não utilizá-los automaticamente para este trabalho acadêmico.

## Alterações propostas

1. Copiar somente as fontes revisadas para `/opt/edutrack/releases/` e manter segredos em `/opt/edutrack/secrets/` com permissões restritas.
2. Criar projeto Docker **edutrack** com frontend Node, API Python e SQL Server 2022 Express. Não executar `down` nem alterar o projeto do CRM.
3. Criar um banco **EduTrackIA vazio na VPS**, aplicar o schema completo e criar login de aplicação restrito. Contas e dados do SQL Server do computador não serão copiados automaticamente.
4. Emitir certificado RSA pelo Certbot existente e configurar um novo arquivo Nginx exclusivo para esse hostname. Validar configuração antes de recarregar Nginx. A recarga é compartilhada com os demais sites; rollback remove somente o arquivo novo e mantém o anterior intacto.
5. Configurar TLS também para SQL Server; instalar certificado e chave com acesso somente ao processo SQL. Renovação exige cópia protegida e recarga somente do container SQL do EduTrack. Não habilitar `TrustServerCertificate` em produção.
6. Configurar SendGrid na VPS somente após autorização para transferir a credencial existente ou gerar outra restrita a envio. Segredos não serão exibidos ou publicados.
7. Ativar gravações e e-mail após conferência de `/ready`. Manter a conversa generativa sem chave, conforme solicitado. O planejador por regras continua disponível.
8. Conferir login/cadastro, e-mail, recuperação, CRUD, relatório e responsividade na URL pública. Testes que enviem e-mails ou criem contas serão limitados ao endereço e dados autorizados.

## Revisão e limitações

Os arquivos em `entrega/deploy/hostinger/` são modelos preparados, não uma implantação executada nem uma compilação Linux validada. Imagens oficiais devem ser resolvidas e fixadas por digest na implantação. A inicialização SQL, o usuário restrito, os certificados e o backup ainda precisam ser configurados; não basta executar `docker compose up`.

Os limites de containers deixam espaço para o CRM, mas a carga deve ser medida após publicação. A API mantém um único worker e limitações em memória; expansão futura precisa de fila e limitador compartilhados. APIs e banco não serão expostos diretamente à internet.

O uso de SQL Server e Microsoft ODBC Driver requer aceitação dos respectivos termos. `ACCEPT_MICROSOFT_EULA` não tem valor padrão; confirmar com o responsável antes de construir/executar as imagens. Referências: [SQL Server](https://learn.microsoft.com/pt-br/sql/linux/configure/environment-variables?view=sql-server-ver17), [ODBC Driver Linux](https://learn.microsoft.com/pt-br/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server).

## Reversão

Guardar a configuração Nginx original antes da nova instalação; nenhuma configuração existente será sobrescrita. Em falha, desabilitar somente o novo site, validar Nginx e recarregar. Parar somente o projeto `edutrack`, preservando seu volume SQL para diagnóstico/backup. Excluir volume ou dados requer confirmação separada. O site Sites anterior permanece disponível durante a implantação.

## Aprovação recebida

O AGENTS.md do usuário exige confirmação antes de modificar VPS, Docker, banco, DNS, certificados e configurações críticas. O responsável aprovou este destino e estas alterações, incluindo os termos Microsoft e a configuração de e-mail. Novas alterações fora desse escopo exigem nova análise e aprovação.
