"""Exporta documentação e SQL a partir do ORM, sem conectar a qualquer banco."""

from pathlib import Path

from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateIndex, CreateTable

from edutrack import integration_models  # noqa: F401 — registrar tabelas sem executar DDL
from edutrack.models import Base


def main():
    backend = Path(__file__).resolve().parents[1]
    docs = backend.parent / "edutrack-documentacao"
    docs.mkdir(exist_ok=True)
    dialect = mssql.dialect()
    tables = Base.metadata.sorted_tables
    lines = ["# Dicionário de dados — EduTrack", "", "Modelo alvo gerado do código, sem consultar valores de usuários. SQL Server; datas DATETIME2 seguem UTC.", "", f"O modelo alvo contém {len(tables)} tabelas. As tabelas Google dependem das migrações 004 e 005. A existência no modelo não comprova aplicação no banco; consulte ATIVACAO_INTEGRACOES.md para o estado de cada ambiente.", "", "CPF é validado e descartado. Senhas são armazenadas somente como hash Argon2; códigos de confirmação usam HMAC e tokens de recuperação usam SHA-256. Tokens Google e verificadores PKCE usam Fernet com vinculação ao usuário e chave independente do JWT.", ""]
    sql = ["-- Modelo completo para um banco EduTrackIA vazio, previamente criado pelo administrador.", "-- Não executar no banco existente; nele use somente migrações revisadas.", "USE [EduTrackIA];", "GO", "SET XACT_ABORT ON;", "IF EXISTS (SELECT 1 FROM sys.tables WHERE is_ms_shipped = 0)", "    THROW 50002, 'O banco deve estar vazio. Use migrações para um banco existente.', 1;", "BEGIN TRANSACTION;"]
    diagram = ["# Modelo de dados (DER)", "", "Cardinalidades e vínculos do modelo alvo. O diagrama não contém dados dos alunos.", "", "```mermaid", "erDiagram", "  usuarios ||--o{ cursos : possui", "  cursos ||--o{ disciplinas : organiza", "  disciplinas ||--o{ tarefas_academicas : contem", "  tarefas_academicas ||--o{ registros_tempo_tarefa : acumula", "  usuarios ||--o| verificacoes_email : verifica", "  usuarios o|--o{ convites_administrador : consome", "  usuarios ||--o{ recuperacoes_senha : solicita", "  usuarios ||--o{ relatorios_semanais : possui"]
    for table in tables:
        lines += [f"## {table.name}", "", "| Campo | Tipo SQL Server | Nulo | Chave / regra |", "|---|---|---|---|"]
        diagram.append(f"  {table.name} {{")
        for column in table.columns:
            flags = []
            if column.primary_key:
                flags.append("PK")
            if column.unique:
                flags.append("UNIQUE")
            for fk in column.foreign_keys:
                flags.append("FK → " + fk.target_fullname)
            if column.computed is not None:
                flags.append("Calculado: " + str(column.computed.sqltext.compile(dialect=dialect)))
            lines.append(f"| `{column.name}` | `{column.type.compile(dialect=dialect)}` | {'Sim' if column.nullable else 'Não'} | {'; '.join(flags) or '—'} |")
            key = " PK" if column.primary_key else " FK" if column.foreign_keys else ""
            diagram.append(f"    {column.type.compile(dialect=dialect).split('(')[0]} {column.name}{key}")
        diagram.append("  }")
        lines += ["", "Restrições: " + "; ".join(str(c.sqltext) for c in table.constraints if hasattr(c, "sqltext")) + ".", ""]
        sql.append(str(CreateTable(table).compile(dialect=dialect)).strip() + ";")
        sql += [str(CreateIndex(index).compile(dialect=dialect)) + ";" for index in table.indexes]
    diagram[13:13] = ["  usuarios ||--o| conexoes_google : conecta", "  usuarios ||--o{ autorizacoes_google : autoriza", "  usuarios ||--o{ vinculos_classroom_disciplinas : importa", "  usuarios ||--o{ vinculos_classroom_tarefas : importa", "  disciplinas o|--o{ vinculos_classroom_disciplinas : origem", "  tarefas_academicas o|--o{ vinculos_classroom_tarefas : origem", "  usuarios ||--o{ conteudos_classroom : possui", "  disciplinas ||--o{ conteudos_classroom : contem"]
    sql += ["COMMIT TRANSACTION;", "GO", ""]
    lines += ["## Integridade e uso", "", "Os vínculos compostos de disciplina/curso e tarefa/disciplina incluem usuario_id para impedir associações entre contas. Exclusões com dependências são recusadas pela API. O agente consulta somente dados da conta autenticada.", "", "`relatorios_semanais` é uma estrutura reservada para artefatos persistidos. Atualmente a tela calcula o relatório a partir das sessões e permite exportar CSV; ela não grava nessa tabela.", "", "Ver [DER](MODELO_DE_DADOS.md) e [recuperação de senha](RECUPERACAO_DE_SENHA.md)."]
    diagram += ["```", "", "Curso e disciplina também possuem FK para usuarios. As FK compostas de organização acadêmica preservam a titularidade. Uma confirmação de e-mail pertence a uma única conta; um convite pode estar pendente, sem conta vinculada.", ""]
    (docs / "DICIONARIO_DE_DADOS.md").write_text("\n".join(lines), encoding="utf-8")
    (docs / "MODELO_DE_DADOS.md").write_text("\n".join(diagram), encoding="utf-8")
    (backend / "migrations" / "000_schema_completo_banco_vazio.sql").write_text("\n\n".join(sql), encoding="utf-8")
    # Migrações históricas são imutáveis; somente o esquema de instalação vazia é regenerado.
    print(f"Documentação e SQL gerados para {len(tables)} tabelas. Nenhum banco foi acessado.")


if __name__ == "__main__":
    main()
