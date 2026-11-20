# Importação completa do Google Classroom

**Publicada, habilitada e validada com importação real em 12/11/2026**, na release `edutrack-entrega-final-20261112-171329`. Após autorização explícita do titular, o curso **Ciência da Computação** foi criado e recebeu a disciplina **SQL Fundamentals**, com 16 tarefas e 56 publicações (16 atividades originais, 24 materiais e 16 avisos), incluindo 43 links de anexos. A importação repetida não criou registros adicionais. Conferência SQL somente de leitura confirmou contagens, identificadores e dados das tarefas iguais antes e depois. A migração 005 foi aplicada com backup verificado; escopos adicionais e consentimento foram confirmados. Isso não libera automaticamente outras contas Google, pois OAuth continua em testes. Detalhes em [IMPORTACAO_REAL_SQL_FUNDAMENTALS_2026-11-12.md](IMPORTACAO_REAL_SQL_FUNDAMENTALS_2026-11-12.md).

## Experiência do aluno

Melhoria de usabilidade publicada em 12/11/2026, release `edutrack-entrega-final-20261112-180444`: cartões de turmas, preservação das escolhas e confirmação antes da lista. Testes locais aprovados; a nova busca foi conferida com Google real e exibiu seis turmas, incluindo a prévia completa de SQL Fundamentals e seu vínculo original. Consulte [CORRECAO_BUSCA_CLASSROOM_2026-11-12.md](CORRECAO_BUSCA_CLASSROOM_2026-11-12.md).

1. Em Integrações, conectar ou atualizar a autorização Google.
2. Buscar turmas e escolher a turma desejada.
3. Manter “Turma completa: atividades, materiais e avisos”.
4. Escolher um curso próprio ou informar o nome de um novo curso.
5. Conferir a prévia e clicar em “Importar turma completa”. A operação consulta novamente o Google e inclui novas atividades disponíveis, sem marcar cada uma.
6. Abrir a disciplina importada. As tarefas ficam no mural e na página Tarefas; publicações e links ficam em “Conteúdo da turma”, com filtros.

Uma turma do Classroom vira uma disciplina vinculada ao curso do EduTrack. Importar é uma ação pontual, que pode levar alguns segundos. Não há promessa de atualização instantânea nem sincronização automática em segundo plano. Para buscar novas publicações, importar novamente.

## Conteúdo e limites

| Origem | Destino no EduTrack |
|---|---|
| Atividades publicadas, descrições e prazos | Tarefas pessoais e cópia da publicação na disciplina |
| Materiais publicados | Biblioteca da disciplina |
| Avisos publicados | Biblioteca da disciplina |
| Tópicos | Identificação do tópico em cada publicação |
| Arquivos Drive, vídeos, formulários e outros links publicados | Título, tipo e endereço do anexo; abertura no serviço original |

São consultados somente os itens acessíveis à conta que consentiu. Não há cópia dos arquivos binários, notas, entregas, comentários, lista de alunos nem busca no Drive privado. Textos são exibidos como texto, nunca como HTML executável. Links inseguros ou locais ficam sem ação; links externos não são carregados antecipadamente e abrem sem referência à página de origem.

Limites: uma turma por importação completa; até 500 atividades, 500 materiais, 500 avisos e 500 tópicos, com até 20 páginas por recurso. Limite global de consulta Google de 45 segundos e timeout por chamada; ultrapassar limite ou falhar em alguma página impede gravação parcial. A página do aluno lê a biblioteca local em lotes de 30, com máximo de 100 por chamada.

Reimportar atualiza as cópias de leitura e adiciona itens novos. Títulos, prazos, descrições e conclusões das tarefas pessoais existentes são preservados, inclusive se o professor alterar a publicação original. Itens excluídos localmente não são recriados. Publicações que desaparecerem do Google continuam na cópia local; esta versão não elimina automaticamente conteúdo remoto removido. Desconectar preserva os estudos. Excluir a disciplina, após remover suas tarefas, também remove as cópias da biblioteca.

## Arquitetura e contrato

- `edutrack/google_classroom.py`: cliente Google de leitura, paginação, limites e validação de escopos.
- `edutrack/classroom_content.py`: normalização de publicações, datas e anexos.
- `edutrack/integration_routes.py`: autorização, prévia, importação transacional e leitura por titular.
- `app/ui/ConnectedIntegrations.tsx`: destino, prévia, importação e resultado.
- `app/ui/ClassroomLibrary.tsx`: biblioteca paginada e filtros na disciplina.

`POST /api/integrations/google/preview` recebe `turma_id` e `completo: true`. `POST /api/integrations/google/import` recebe `conexao_versao`, exatamente um entre `curso_id` e `novo_curso`, e uma turma com `modo: "completo"`. Também continuam disponíveis `todas_atividades` e `selecionadas`. `GET /api/integrations/google/disciplines/{discipline_id}/content` aceita `tipo`, `offset` e `limit` e exige sessão do titular. O BFF mantém cookies, proteção de origem, lista de rotas e parâmetros permitidos.

As consultas Google terminam antes de iniciar gravações. Curso opcional, disciplina, tarefas e conteúdos participam de uma única transação. A versão da conexão protege contra desconexão/troca concorrente; unicidade por usuário, conta Google, turma, tipo e ID impede duplicação. A FK composta de disciplina e titular impede conteúdo vinculado a outra conta.

## Banco e ativação

**Aplique a migração 005 antes de iniciar esta versão da API, mesmo com a nova flag desligada:** o ORM passa a selecionar `conexoes_google.conteudo_autorizado`. A migração é aditiva: cria a coluna com padrão falso e a tabela `conteudos_classroom`, índice e restrições. Modelo completo: 14 tabelas. Migrações antigas, especialmente 004, são preservadas e não são regeneradas pelo exportador.

Procedimento de ativação (etapas 1 a 7 concluídas na VPS para a conta autorizada, incluindo importação real e reimportação sem duplicações):

1. Conferir os containers e fazer backup SQL verificável do EduTrackIA.
2. Aplicar somente `005_conteudos_classroom.sql` e conceder ao usuário restrito da API CRUD somente na tabela nova. Não conceder DDL.
3. Publicar o pacote revisado e reconstruir/reiniciar somente API e frontend EduTrack; pode ocorrer breve indisponibilidade.
4. Manter credenciais e chave de criptografia existentes. Definir `EDUTRACK_CLASSROOM_FULL_IMPORT_ENABLED=true` no arquivo privado da VPS.
5. Configurar no Google Cloud os escopos adicionais `classroom.courseworkmaterials.readonly`, `classroom.announcements.readonly` e `classroom.topics.readonly`. Todos usam o prefixo `https://www.googleapis.com/auth/`.
6. Cada aluno renova o consentimento individual. A conexão antiga continua servindo à importação básica e não autoriza os conteúdos adicionais automaticamente.
7. Testar prévia real completa e, após confirmação do destino, importar a turma escolhida. Conferir contagens, prazos, biblioteca e repetição sem duplicações.

Preservar SQL em execução, CRM, Nginx, DNS e certificados. Gemini continua desligado para o público 13+. OAuth permanece em modo de testes; acesso de outros alunos ainda depende da configuração/validação do aplicativo Google e das políticas de cada instituição.

Reversão: conservar imagens, release anterior e configuração privada. Se necessário e autorizado, voltar apenas API/frontend e flag. Não remover a coluna/tabela nem dados importados; o código anterior tolera as estruturas aditivas. Não usar `docker compose down -v`.

## Validação

- Suíte completa inicial: 147 testes da API e 41 do frontend aprovados. Após reforço de validação de URLs/tópicos e teste de exclusão, os 23 testes específicos de importação completa passaram; a execução final está registrada em `evidencias/classroom-completo-2026-11-12/VALIDACAO.md`.
- Testes cobrem paginação, falha parcial, limites, novo curso, atividade posterior à prévia, escopos antigos, isolamento, biblioteca após desconexão, preservação de edições/conclusões, links inseguros e exclusão sem recriação.
- QA Chrome: SQLite descartável e Google simulado, sem uso do banco SQL real. Primeira importação criou um curso, uma disciplina, duas tarefas e cinco publicações (dois materiais, um aviso e duas atividades), com quatro links. Reimportação não duplicou registros. Filtros e atalho da disciplina verificados. Layout de celular em 390 px sem rolagem horizontal; temas claro e escuro conferidos.
- Capturas na pasta de evidências mostram somente dados fictícios. Uma descrição deliberadamente adversarial faz parte da fixture de segurança e é tratada como texto, não como instrução.

## Fontes técnicas

Consultadas em 12/11/2026: [atividades](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork/list), [materiais](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWorkMaterials/list), [avisos](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.announcements/list), [tópicos](https://developers.google.com/workspace/classroom/reference/rest/v1/courses.topics/list) e [tipos de anexos](https://developers.google.com/workspace/classroom/reference/rest/v1/Material).
