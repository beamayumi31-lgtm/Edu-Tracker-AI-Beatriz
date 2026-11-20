# Revisão complementar — Claude Desktop

Em 12/11/2026, foi enviado ao Claude Desktop gratuito um resumo técnico da importação completa. Não foram enviados código privado, arquivos de configuração, credenciais, dados acadêmicos ou conteúdo de contas. A resposta foi lida visualmente no aplicativo. O Claude avaliou a arquitetura descrita; não executou testes nem inspecionou o repositório.

## Recomendações avaliadas

| Ponto levantado | Tratamento no EduTrack |
|---|---|
| Atomicidade, concorrência e timeouts | Consulta Google limitada a 45 s antes da gravação; BFF 65 s. UPDATE da versão da conexão e gravações na mesma transação, checagem de linhas, restrições únicas e rollback. Erros de Google/paginação impedem gravação parcial. Não usa MERGE. |
| Reimportação e exclusões | Vínculos com ID de origem sobrevivem à exclusão da tarefa/disciplina. Tarefas existentes sempre preservadas; cópias de leitura atualizáveis. Teste de exclusão e não recriação aprovado. Conteúdo removido remotamente não é apagado da cópia local nesta versão. |
| OAuth e expiração | Escopos efetivamente concedidos validados no callback. Conexão antiga não amplia acesso. PKCE, state com prazo e consumo atômico, tokens cifrados e erros sem segredos já implementados. O modo de testes Google e restrições institucionais continuam limitações de ativação. |
| Isolamento e paginação | Origem validada contra turmas acessíveis; biblioteca filtrada por titular com FK composta. Testes de acesso por outro aluno retornam 404. Ordenação por publicação e ID, com índice por titular/disciplina. |
| Conteúdo não confiável | Renderização textual React; sem HTML injetado, download ou busca automática de anexos. Validação http/https no backend, controles e destinos locais bloqueados, incluindo aliases IPv4. Links sem referrer e noopener. |

A biblioteca local pode ser lida depois de desconectar o Google, de acordo com a política de preservação de estudos. Por isso essa leitura não consulta novamente o Google: exige a titularidade da disciplina no EduTrack.

Antes da publicação continuam necessários backup, aplicação controlada da migração 005 e teste SQL Server real, incluindo a FK com cascade. A validação local de DDL é compilação do modelo e testes SQLite; **não equivale à execução da migração no SQL Server**. Não há cascatas de exclusão de usuário/curso neste modelo, mas a aplicação real deve ser verificada na ativação.

O fluxo síncrono é adequado às turmas dentro dos limites definidos. Turmas grandes ou conexões lentas podem exceder o prazo e falhar sem importação parcial; um trabalho assíncrono persistente é uma evolução futura, não parte desta entrega. A operação de banco não tem um prazo global próprio garantido; a repetição é protegida por deduplicação caso o cliente perca a resposta após o commit.

O Claude recomendou manter migração e publicação bloqueadas até aprovação. Esse limite já consta nas instruções do titular e foi mantido.
