-- Migração aditiva. Aplicar somente após backup e aprovação do responsável.
-- Preserva contas e dados acadêmicos; conexões atuais exigirão novo consentimento
-- somente para a importação completa. A importação básica continua disponível.
USE [EduTrackIA];
GO
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF COL_LENGTH(N'dbo.conexoes_google', N'conteudo_autorizado') IS NULL
BEGIN
    ALTER TABLE dbo.conexoes_google ADD conteudo_autorizado BIT NOT NULL
        CONSTRAINT DF_conexoes_google_conteudo DEFAULT (0) WITH VALUES;
END;
IF OBJECT_ID(N'dbo.conteudos_classroom', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.conteudos_classroom (
        id UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
        usuario_id UNIQUEIDENTIFIER NOT NULL REFERENCES dbo.usuarios(id),
        google_sub VARCHAR(128) NOT NULL,
        turma_id VARCHAR(128) NOT NULL,
        origem_id VARCHAR(128) NOT NULL,
        tipo VARCHAR(20) NOT NULL,
        disciplina_id UNIQUEIDENTIFIER NOT NULL,
        titulo NVARCHAR(3000) NOT NULL,
        descricao NVARCHAR(MAX) NOT NULL,
        topico NVARCHAR(200) NOT NULL,
        -- O limite de 4096 caracteres é validado na normalização da aplicação.
        url NVARCHAR(MAX) NULL,
        anexos_json NVARCHAR(MAX) NOT NULL,
        publicado_em DATETIME2(3) NULL,
        criado_em DATETIME2(3) NOT NULL,
        atualizado_em DATETIME2(3) NOT NULL,
        CONSTRAINT CK_classroom_conteudo_tipo CHECK (tipo IN ('atividade', 'material', 'aviso')),
        CONSTRAINT FK_classroom_conteudo_titular FOREIGN KEY (disciplina_id, usuario_id) REFERENCES dbo.disciplinas(id, usuario_id) ON DELETE CASCADE,
        CONSTRAINT UQ_classroom_conteudo_origem UNIQUE (usuario_id, google_sub, turma_id, tipo, origem_id)
    );
    CREATE INDEX IX_classroom_conteudo_disciplina ON dbo.conteudos_classroom(usuario_id, disciplina_id);
END;
COMMIT TRANSACTION;
GO
