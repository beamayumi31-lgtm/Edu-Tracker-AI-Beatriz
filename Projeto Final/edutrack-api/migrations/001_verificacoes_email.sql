-- Executar somente depois de autorização explícita, em localhost\SQLEXPRESS / EduTrackIA.
-- Migração aditiva: nenhuma tabela ou registro existente é apagado/reescrito.
SET XACT_ABORT ON;
IF DB_NAME() <> N'EduTrackIA'
    THROW 50001, 'Execute exclusivamente no banco EduTrackIA.', 1;
BEGIN TRANSACTION;
IF OBJECT_ID(N'dbo.verificacoes_email', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.verificacoes_email (
        usuario_id UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
        codigo_hash VARCHAR(64) NULL,
        expira_em DATETIME2(3) NULL,
        confirmado_em DATETIME2(3) NULL,
        enviado_em DATETIME2(3) NULL,
        janela_em DATETIME2(3) NULL,
        envios INT NOT NULL CONSTRAINT DF_verificacoes_email_envios DEFAULT 0,
        tentativas INT NOT NULL CONSTRAINT DF_verificacoes_email_tentativas DEFAULT 0,
        versao INT NOT NULL CONSTRAINT DF_verificacoes_email_versao DEFAULT 0,
        CONSTRAINT FK_verificacoes_email_usuario FOREIGN KEY (usuario_id) REFERENCES dbo.usuarios(id),
        CONSTRAINT CK_verificacoes_email_contadores CHECK (envios >= 0 AND tentativas >= 0 AND versao >= 0)
    );
END;
COMMIT TRANSACTION;
