-- Migração 004: quatro tabelas aditivas para Classroom. Não executar sem aprovação.
-- Nenhum aluno, curso, disciplina ou tarefa é alterado. Não cria conexões externas.
USE [EduTrackIA];
GO
SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF OBJECT_ID(N'dbo.autorizacoes_google', N'U') IS NULL
BEGIN
CREATE TABLE autorizacoes_google (
	state_hash VARCHAR(64) NOT NULL,
	usuario_id UNIQUEIDENTIFIER NOT NULL,
	verifier_cifrado VARCHAR(max) NOT NULL,
	expira_em DATETIME2(3) NOT NULL,
	usado_em DATETIME2(3) NULL,
	PRIMARY KEY (state_hash),
	UNIQUE (usuario_id),
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);
END;
IF OBJECT_ID(N'dbo.conexoes_google', N'U') IS NULL
BEGIN
CREATE TABLE conexoes_google (
	usuario_id UNIQUEIDENTIFIER NOT NULL,
	google_sub VARCHAR(128) NOT NULL,
	email VARCHAR(255) NOT NULL,
	refresh_cifrado VARCHAR(max) NOT NULL,
	versao UNIQUEIDENTIFIER NOT NULL,
	criado_em DATETIME2(3) NOT NULL,
	atualizado_em DATETIME2(3) NOT NULL,
	PRIMARY KEY (usuario_id),
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);
END;
IF OBJECT_ID(N'dbo.vinculos_classroom_disciplinas', N'U') IS NULL
BEGIN
CREATE TABLE vinculos_classroom_disciplinas (
	usuario_id UNIQUEIDENTIFIER NOT NULL,
	google_sub VARCHAR(128) NOT NULL,
	turma_id VARCHAR(128) NOT NULL,
	disciplina_id UNIQUEIDENTIFIER NULL,
	id UNIQUEIDENTIFIER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT [UQ_classroom_disciplina_origem] UNIQUE (usuario_id, google_sub, turma_id),
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id),
	FOREIGN KEY(disciplina_id) REFERENCES disciplinas (id) ON DELETE SET NULL
);
END;
IF OBJECT_ID(N'dbo.vinculos_classroom_tarefas', N'U') IS NULL
BEGIN
CREATE TABLE vinculos_classroom_tarefas (
	usuario_id UNIQUEIDENTIFIER NOT NULL,
	google_sub VARCHAR(128) NOT NULL,
	turma_id VARCHAR(128) NOT NULL,
	atividade_id VARCHAR(128) NOT NULL,
	tarefa_id UNIQUEIDENTIFIER NULL,
	id UNIQUEIDENTIFIER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT [UQ_classroom_tarefa_origem] UNIQUE (usuario_id, google_sub, turma_id, atividade_id),
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id),
	FOREIGN KEY(tarefa_id) REFERENCES tarefas_academicas (id) ON DELETE SET NULL
);
END;
COMMIT TRANSACTION;
GO
