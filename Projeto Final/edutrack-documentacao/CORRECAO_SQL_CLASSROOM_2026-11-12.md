# Compatibilidade SQL Server da importação completa

Na tentativa de implantação de 12/11/2026, o SQL Server recusou `NVARCHAR(4096)` na coluna `conteudos_classroom.url` (erro 2717). A migração foi revertida; a estrutura permaneceu com treze tabelas, sem a coluna nova e sem alteração nos estudos. O site continuou na release anterior.

A correção usa `NVARCHAR(MAX)` exclusivamente para esse campo no SQL Server. O normalizador da aplicação mantém o limite de 4.096 caracteres e a validação de URLs; outros dialetos continuam com o tipo anterior. A migração 005, ainda não aplicada, o esquema para instalação vazia, o modelo e o dicionário foram alinhados. A migração histórica 004 permanece idêntica.

Foi acrescentado um teste de regressão para limites nativos de `NCHAR` e `NVARCHAR` em todas as tabelas do modelo e em todas as migrações. Compilar DDL ou usar SQLite não detectava essa incompatibilidade. O DDL corrigido também foi executado com sucesso no SQL Server de destino dentro de uma transação de diagnóstico explicitamente revertida, sem importar dados.

O pacote original `edutrack-entrega-final-20261112-165730.zip` foi preservado para auditoria. Sua substituição técnica contém a mesma funcionalidade aprovada, com essa correção de compatibilidade, teste e documentação. A implantação efetiva e seus resultados devem ser consultados em [ATIVACAO_INTEGRACOES.md](ATIVACAO_INTEGRACOES.md).

Referência: [nchar e nvarchar — Microsoft Learn](https://learn.microsoft.com/en-us/sql/t-sql/data-types/nchar-and-nvarchar-transact-sql?view=sql-server-ver17).
