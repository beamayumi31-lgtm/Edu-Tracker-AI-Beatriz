-- Autorização concedida para o ambiente LOCAL. Não executar em produção.
-- Migração aditiva: preserva contas, senhas e dados acadêmicos; todos começam como alunos.
SET XACT_ABORT ON;
IF DB_NAME() <> N'EduTrackIA'
    THROW 50001, 'Execute exclusivamente no banco EduTrackIA.', 1;
BEGIN TRANSACTION;
IF COL_LENGTH(N'dbo.usuarios', N'role') IS NULL
    EXEC(N'ALTER TABLE dbo.usuarios ADD role VARCHAR(16) NOT NULL CONSTRAINT DF_usuarios_role DEFAULT ''student'' WITH VALUES');
IF OBJECT_ID(N'dbo.CK_usuarios_role', N'C') IS NULL
    EXEC(N'ALTER TABLE dbo.usuarios WITH CHECK ADD CONSTRAINT CK_usuarios_role CHECK (role IN (''student'', ''admin''))');
IF OBJECT_ID(N'dbo.convites_administrador', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.convites_administrador (
        email NVARCHAR(255) NOT NULL PRIMARY KEY,
        criado_em DATETIME2(3) NOT NULL,
        expira_em DATETIME2(3) NOT NULL,
        usado_em DATETIME2(3) NULL,
        usuario_id UNIQUEIDENTIFIER NULL,
        CONSTRAINT FK_convites_admin_usuario FOREIGN KEY (usuario_id) REFERENCES dbo.usuarios(id),
        CONSTRAINT CK_convites_admin_prazo CHECK (expira_em > criado_em),
        CONSTRAINT CK_convites_admin_consumo CHECK (
            (usado_em IS NULL AND usuario_id IS NULL) OR
            (usado_em IS NOT NULL AND usuario_id IS NOT NULL)
        )
    );
END;
COMMIT TRANSACTION;
