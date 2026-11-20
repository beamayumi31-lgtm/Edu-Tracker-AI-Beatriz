# Importação real de SQL Fundamentals — 12/11/2026

O titular autorizou explicitamente criar o curso **Ciência da Computação**, importar todo o conteúdo disponível de **SQL Fundamentals** e verificar se a repetição gerava duplicações. A execução ocorreu no site público da Hostinger, na sessão do titular no Chrome, usando o Google Classroom real. Esta evidência é distinta do QA com SQLite e dados simulados.

## Primeira importação

Foi escolhido o modo **Turma completa: atividades, materiais e avisos**, a turma **SQL Fundamentals · 202602 - CC 2A NOITE** e a criação do curso Ciência da Computação. A interface confirmou uma disciplina, 16 tarefas novas e 56 conteúdos adicionados.

| Resultado persistido | Quantidade |
|---|---:|
| Curso Ciência da Computação para o titular | 1 |
| Disciplina SQL Fundamentals nesse curso | 1 |
| Tarefas pessoais, todas com prazo | 16 |
| Atividades originais na biblioteca | 16 |
| Materiais | 24 |
| Avisos | 16 |
| Total de publicações na biblioteca | 56 |
| Links de anexos | 43 |
| Rótulos de tópicos distintos representados | 6 |
| Publicações vinculadas a esses tópicos | 34 |

As atividades originais são cópias de consulta na biblioteca; as 16 tarefas pessoais são os registros editáveis do aluno. Essa separação não representa duplicação de tarefas.

## Conferência da interface

O atalho de sucesso abriu a disciplina com o curso correto e 16 atividades pendentes. Os filtros da biblioteca retornaram 24 materiais, 16 avisos e 16 atividades originais. A opção Todos os conteúdos mostrou 30 itens na primeira página e 26 na segunda, totalizando 56. Não foram abertos nem baixados todos os anexos; a importação conserva links e permissões originais.

## Reimportação e persistência

A mesma turma foi importada novamente no **curso existente**, sem criar outro curso. A mensagem retornou:

- Zero disciplinas novas.
- Zero tarefas novas.
- Zero conteúdos adicionados; 56 conteúdos atualizados.
- 17 registros pessoais preservados: a disciplina e as 16 tarefas.

Uma verificação no SQL Server executou apenas SELECTs, com as credenciais restritas já configuradas da API e escopo na disciplina importada/titular. Não leu segredos nem alterou os registros manualmente. Contagens e hashes antes/depois foram comparados automaticamente:

| Conferência | Resultado |
|---|---|
| IDs de curso, disciplina, tarefas, conteúdos e vínculos | Iguais |
| Título, descrição, prazo, status, estimativa e conclusão das tarefas | Iguais |
| Publicações, anexos e tópicos, excluindo timestamp local da atualização | Iguais |
| Chaves de origem duplicadas na biblioteca | 0 |
| Vínculos de origem de tarefas duplicados | 0 |
| Vínculo entre cada tarefa e atividade original | Correspondência integral das 16 |
| Curso e disciplina de destino | Um de cada, sem duplicação |

Não foram feitas edições ou conclusões fictícias nas atividades reais. A comparação comprova a preservação do estado existente entre essas duas execuções; cenários de edição manual e concorrência continuam cobertos pelos testes automatizados separados.

## Evidências e limites

Pasta local: `output/edutrack-classroom-completo-2026-11-12/`.

- `importacao-real-primeira.json` e `importacao-real-repetida.json`: contagens e hashes; o segundo confirma comparação idêntica, sem duplicação.
- `verificar_importacao_real.py`: verificador somente de leitura, restrito à disciplina desta execução.
- `importacao-real-primeiro-resultado.png`, `materiais-reais-importados.png` e `importacao-real-repetida-resultado.png`: evidências de interface.
- `importacao-real-sem-duplicacao-resumo.png`: confirmação final da repetição, deixada aberta no Chrome.

As capturas contêm dados reais e não foram enviadas ao GitHub nem incluídas nos ZIPs públicos. Código de produção, migrações, containers, DNS, Nginx e certificados não foram modificados nesta etapa. Documentação e OpenSpec foram atualizados localmente.

O resultado se aplica à turma e conta testadas, no estado do Classroom nessa data. Outras turmas e outros alunos não foram importados. OAuth continua em modo de testes. A importação busca publicações acessíveis à conta e seus links; não baixa arquivos, importa notas/entregas/comentários nem sincroniza continuamente. Novas publicações exigem nova importação.
