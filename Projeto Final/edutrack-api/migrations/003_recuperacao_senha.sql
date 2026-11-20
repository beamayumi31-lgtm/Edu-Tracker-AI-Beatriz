-- Impacto: acrescenta somente recuperacoes_senha e seu índice. Não altera contas nem senhas.
-- Aplicação manual após autorização. Não executado automaticamente pela API.
USE [EduTrackIA];
GO
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF OBJECT_ID(N'dbo.recuperacoes_senha', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.recuperacoes_senha (
        id UNIQUEIDENTIFIER NOT NULL CONSTRAINT PK_recuperacoes_senha PRIMARY KEY,
        usuario_id UNIQUEIDENTIFIER NOT NULL,
        token_hash VARCHAR(64) NOT NULL CONSTRAINT UQ_recuperacoes_senha_token UNIQUE,
        criado_em DATETIME2(3) NOT NULL,
        expira_em DATETIME2(3) NOT NULL,
        usado_em DATETIME2(3) NULL,
        CONSTRAINT FK_recuperacoes_senha_usuario FOREIGN KEY (usuario_id) REFERENCES dbo.usuarios(id),
        CONSTRAINT CK_recuperacoes_senha_prazo CHECK (expira_em > criado_em)
    );
    CREATE INDEX ix_recuperacoes_senha_usuario_id ON dbo.recuperacoes_senha(usuario_id);
END;
COMMIT;
GO
