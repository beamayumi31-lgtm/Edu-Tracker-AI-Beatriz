# Integração autorizada com SQL Server — 05/10/2026

## Resultado

**83 verificações aprovadas** contra `localhost\SQLEXPRESS`, banco `EduTrackIA`, além de **45 testes isolados aprovados**. O responsável autorizou criar dados fictícios e removê-los ao final, sem alterar tabelas.

As rotas foram executadas pelo cliente ASGI do FastAPI, usando a aplicação e seu ORM com transações e commits no SQL Server real. Conexões independentes confirmaram que os registros e exclusões persistiram. Isso valida backend/banco; não é um teste ponta a ponta das telas do site.

## Cobertura

- Cadastro de duas contas fictícias, senha Argon2id, login, identidade da sessão, rejeição de duplicidade de e-mail e senha incorreta.
- Criação, consulta, edição e exclusão de cursos, disciplinas e tarefas.
- Preservação de Unicode, datas e conversão de horário para UTC.
- Conclusão e reabertura de tarefa, incluindo preenchimento/remoção de `concluido_em`.
- Paginação e listas por titularidade.
- Bloqueio de leitura, edição e exclusão de IDs de outro aluno; bloqueio de vínculos e transferências entre contas.
- FK composta real recusando uma disciplina com curso de outro titular; rollback confirmado sem registro residual.
- Gravação e consulta de sessão de estudo, duração calculada pelo banco e resumo acadêmico consistente.
- Contexto da Edu IA limitado à conta autenticada e geração de proposta de 90 minutos por regras, sem provedor externo.
- Proteção de dependências/histórico com resposta 409; exclusão efetiva de hierarquia descartável sem histórico.

## Correção encontrada

Na primeira rodada de gravação, o SQL Server recusou uma sessão porque a API tentava inserir `duracao_minutos`. A inspeção confirmou que a coluna existente é **calculada e persistida**, com esta expressão:

```sql
CASE WHEN finalizado_em IS NULL THEN NULL
     ELSE DATEDIFF(minute, iniciado_em, finalizado_em)
END
```

Ajustes feitos somente no código:

1. Mapear a coluna com `Computed`, respeitando o valor gerado pelo servidor. Esse é o mecanismo de [colunas calculadas do SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/defaults.html#computed-columns-generated-always-as).
2. Remover a atribuição manual da duração no endpoint.
3. Reproduzir a coluna gerada nos testes SQLite, sem executar DDL no SQL Server.
4. Adicionar testes de compilação do INSERT/DDL e do comportamento nas viradas de minuto.
5. Melhorar a verificação de esquema para detectar divergências de colunas calculadas.

Também foi ajustada a inspeção de CHECK constraints do roteiro: esse método de reflexão não está implementado no dialeto utilizado; a leitura agora consulta `sys.check_constraints` com parâmetro, sem alteração de restrições.

A rodada com falha removeu todos os registros fictícios no bloco de limpeza. Após a correção, a repetição completa passou.

## Limpeza e comparação

Na rodada final foram criadas duas contas, três cursos, duas disciplinas, duas tarefas e uma sessão, todos fictícios. Uma tarefa, uma disciplina e um curso foram excluídos pelas rotas de DELETE durante o teste. A limpeza final removeu os sete registros restantes, usando somente os IDs das contas exclusivas da execução.

| Tabela | Antes | Depois |
|---|---:|---:|
| usuarios | 0 | 0 |
| cursos | 0 | 0 |
| disciplinas | 0 | 0 |
| tarefas_academicas | 0 | 0 |
| registros_tempo_tarefa | 0 | 0 |
| relatorios_semanais | 0 | 0 |

A comparação incluiu assinaturas dos registros e metadados de colunas, PKs, FKs, índices e CHECK constraints. O estado final foi idêntico ao inicial. Não foi usada exclusão geral de tabelas, TRUNCATE ou migração. Somente dados fictícios foram excluídos; são reproduzíveis pelo roteiro, não mantidos como contas de demonstração.

## Estado após a execução

- Nenhuma conta de teste ou sessão de autenticação utilizável foi deixada no banco.
- Não foi alterado `.env`; a escrita padrão continua desabilitada.
- Nenhum servidor adicional permaneceu executando por causa deste roteiro.
- Frontend e publicação não foram alterados.
- Não houve chamada à IA externa. Chave/modelo e integração das telas continuam pendentes.
- Os testes não cobrem administração, CPF, verificação de contato, pagamentos ou relatórios persistidos, pois essas funcionalidades não foram implementadas nesta API.

O roteiro está em `scripts/test_sqlserver_integration.py`. Uma nova execução com `--executar` exige autorização para novas gravações e remoções fictícias no banco indicado.
