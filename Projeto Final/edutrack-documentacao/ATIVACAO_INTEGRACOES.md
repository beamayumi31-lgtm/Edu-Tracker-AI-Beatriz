# Ativação das integrações — 10 e 11/11/2026

Registro em andamento. Distingue a publicação do código da autorização real dos provedores. Em 11/11, a prévia real do Classroom foi validada no Chrome; importação real e chat com provedor externo continuam pendentes.

## Decisões confirmadas

- Usar a conta acadêmica `antonio.brites@aluno.impacta.edu.br` para o projeto Google.
- Público atualizado pelo responsável: pessoas a partir de 13 anos, incluindo adolescentes de 13 a 17. Essa decisão substitui a confirmação anterior de público exclusivamente adulto. Gemini permanece desativado; adaptar o chat para outro provedor depende de preparação e aprovação separadas.
- Criar o projeto Google na organização `faculdadeimpacta.com.br`, sujeito às suas políticas.
- Atualizar a VPS, após backup, com a migração aditiva 004, CRUD restrito nas novas tabelas e proteção dos logs de retorno OAuth; preservar CRM, DNS e certificados.

## Executado e verificado

- Projeto Google `EduTrack`, ID `edutrack-514322`, criado na organização da faculdade.
- API Google Classroom ativada; status `Ativado` confirmado no painel após o aceite autorizado dos termos.
- Identidade OAuth `EduTrack` criada após autorização específica e aceite da política de dados dos usuários dos serviços de API Google. Suporte e contato: conta acadêmica. Público Externo em modo de testes.
- Clientes OAuth Web `EduTrack - Web producao` e `EduTrack - Web localhost` criados, com os retornos exatos aprovados. Identificadores e segredos gravados somente em arquivos privados de `%LOCALAPPDATA%\EduTrack`; seus valores não constam nesta documentação.
- Os quatro escopos de identificação/e-mail, turmas e atividades do próprio aluno foram salvos. O console confirmou a gravação. Somente `antonio.brites@aluno.impacta.edu.br` foi adicionado como usuário de teste; tabela do Google confirmou **1 usuário de teste**. Isso não equivale a consentimento individual nem libera acesso para todos os alunos.
- Credencial de localhost preparada em `backend.env` privado, com backup e chave de criptografia preservada ou gerada. `EDUTRACK_CLASSROOM_ENABLED=false` permanece no ambiente local; não houve alteração no banco local.
- Projeto importado no AI Studio da mesma conta. A chave exclusiva `EduTrack - servidor` foi criada e revogada em seguida, com autorização, porque seu valor apareceu no retorno técnico do painel. Não foi instalada, usada, copiada para arquivos nem transferida à VPS. A chave preexistente de outro projeto foi preservada. Nenhuma chave nova foi emitida após a decisão de público 13+.
- Backup SQL nativo `EduTrackIA_20261110T222551Z.bak`, com checksum e `RESTORE VERIFYONLY` aprovados.
- Migração 004 aplicada: nove tabelas anteriores preservadas, quatro novas tabelas vazias, total de treze.
- Permissões verificadas pelo login da aplicação: SELECT, INSERT, UPDATE e DELETE nas quatro tabelas; sem CREATE TABLE.
- Hash SHA-256 da migração revisada: `3609ef6f48bc45abbeab7497f47831896d72283a8b0b6d2ca983be67634f86a7`.
- Release `/opt/edutrack/releases/edutrack-entrega-final-20261110-192434`, com 207 arquivos conferidos contra o manifesto. Build de API e frontend concluído na VPS.
- `/opt/edutrack/current` atualizado; containers `api` e `web` recriados e saudáveis. Container SQL e containers CRM não reiniciados.
- Nginx passou em `nginx -t` e foi recarregado com `access_log off` apenas no retorno `/integracoes/google/callback`. Os outros arquivos de sites permaneceram byte a byte iguais. Avisos de opções de protocolo repetidas nos virtual hosts existentes não impediram a validação; não foram alterados fora do escopo.
- Login, privacidade e retorno OAuth responderam HTTP 200 por HTTPS. CRM também respondeu HTTP 200.
- Contrato `edutrack-api/docs/openapi.json` regenerado com trinta caminhos, sem acesso ao SQL Server na geração.
- Suíte da API executada na imagem Linux publicada: **122 testes aprovados**, banco descartável e rede desativada. Houve um aviso de depreciação do transporte de testes Starlette/httpx. Esse resultado não comprova OAuth real nem chamadas a provedores de IA.

## Publicação OAuth concluída

- Release autorizada `/opt/edutrack/releases/edutrack-entrega-final-20261110-194748` publicada; **209 arquivos** conferidos por tamanho e SHA-256 contra o manifesto antes do build.
- API e frontend compilados na VPS. **129 testes aprovados** na nova imagem Linux, com rede desativada e banco de testes descartável, em 117,58 segundos; somente o aviso já conhecido Starlette/httpx.
- Credencial OAuth de produção transmitida por SSH sem aparecer em argumentos ou saídas. Arquivos privados da VPS com modo `600`; backup de `backend.env` preservado. A chave Fernet existente foi preservada ou gerada se ausente.
- `EDUTRACK_CLASSROOM_ENABLED=true`, `EDUTRACK_AI_AUDIENCE=includes_teens` e `EDUTRACK_GEMINI_ENABLED=false` verificados no ambiente do container em execução. Nenhum chat externo configurado. O readiness confirmou acesso ao banco e às quatro tabelas de integração.
- Somente `edutrack-api-1` e `edutrack-web-1` foram recriados; ambos saudáveis. SQL permaneceu com seis dias de execução e CRM com duas semanas. Esta publicação não executou migração nem alterou Nginx, DNS ou certificados.
- HTTPS: login, privacidade e retorno OAuth **200**; endpoint de status da integração sem sessão **401**, conforme esperado; CRM **200**. Conteúdo publicado do aviso sobre notas e meta `referrer=no-referrer` do callback também conferidos.
- Evidência técnica: `output/edutrack-ativacao-2026-11-10/verificacao-publicacao-oauth.json`. Capturas do painel Google e da privacidade publicada estão na mesma pasta, sem segredos de cliente.
- Revisão complementar feita no Claude Desktop, sem compartilhar arquivos privados, dados acadêmicos ou credenciais: [REVISAO_CLAUDE_2026-11-10.md](REVISAO_CLAUDE_2026-11-10.md).
- Na conclusão da publicação ainda não havia consentimento individual. Em teste posterior no Chrome, a tela passou a mostrar **Conta conectada** para a conta acadêmica autorizada. Não foi feita importação de registros reais.

## Conexão real e correção da primeira prévia

- Cadastro e confirmação por e-mail concluídos pelo titular. Uma mensagem SendGrid foi encontrada no Spam do Gmail e movida para a caixa de entrada; o problema observado era classificação da mensagem, não ausência de entrega.
- A conta Google acadêmica foi selecionada no consentimento. O titular autorizou identificação/e-mail e leitura de turmas/atividades, ciente de que a permissão Google também abrange notas. Ao retomar, o EduTrack já confirmou **Conta conectada**. Não foi inspecionado nem registrado o conteúdo de tokens.
- No teste inicial de 10/11, a busca de turmas terminou sem erro visível, mas a interface ocultava os seletores e a prévia quando não havia curso cadastrado. A leitura real foi validada após a correção publicada em 11/11, conforme a seção seguinte.
- Correção local preparada: seleção da turma e prévia independem de cursos locais; o curso de destino e a ação de importar permanecem bloqueados enquanto não existir destino válido. Nenhuma alteração na API, banco ou credenciais é necessária.
- QA local no Chrome: conta fictícia sem cursos, Google simulado e SQLite descartável. Duas turmas simuladas apareceram e a prévia exibiu duas atividades; selecionar atividades não habilitou a importação. Layout conferido em desktop e largura de 390 px, com o tamanho normal restaurado ao final.
- Validação da correção: **40 testes frontend**, TypeScript, ESLint do componente, Ruff das fixtures, **9 validações OpenSpec** e build Next de produção aprovados. Os **129 testes da API** são os da publicação anterior; não foram repetidos porque o código de produção da API não mudou.
- Evidências: `output/edutrack-ativacao-2026-11-10/qa-previa-sem-curso.png` e `qa-previa-sem-curso-mobile.png`. Essas imagens mostram dados **simulados**, não atividades reais do titular.
- A correção foi publicada em 11/11 após autorização específica do frontend. Ela não cria cursos nem importa disciplinas/tarefas por conta própria.

## Publicação da prévia e validação real — 11/11/2026

- Release autorizada `edutrack-entrega-final-20261110-202738` publicada na VPS. Os **210 arquivos** foram conferidos pelo manifesto; código de produção da API e arquivos de infraestrutura eram idênticos aos da release anterior.
- Build Next de produção concluído na VPS. Somente `edutrack-web-1` foi reconstruído e recriado, com healthcheck aprovado. Os identificadores dos containers da API, SQL e CRM permaneceram iguais aos registrados antes da publicação. Login EduTrack e CRM responderam **HTTP 200 por HTTPS**.
- Não houve migração, alteração de credenciais, Nginx, DNS ou certificados. A release `194748` foi preservada e a imagem anterior do frontend recebeu a tag `edutrack-web:rollback-20261110-previa`.
- Diagnóstico de leitura no servidor usou a conexão Google já autorizada, sem criar sessão de usuário, alterar a conexão ou gravar no banco: encontrou **6 turmas ativas** e **16 atividades** na turma consultada. O relatório registra apenas contagens, sem credenciais nem conteúdo acadêmico.
- Após o titular entrar novamente, o fluxo completo de **consulta** foi validado na sessão dele no Chrome, no site público: conta conectada, botão **Buscar turmas**, seis opções e prévia de **16 atividades de SQL Fundamentals** com seus prazos.
- A conta não tinha curso cadastrado. A prévia ficou disponível, enquanto o curso de destino e o botão de importação permaneceram bloqueados. Selecionar as 16 atividades manteve a importação desabilitada. A seleção foi desfeita ao final; nenhum curso, disciplina ou tarefa foi importado.
- Evidências locais: `output/edutrack-ativacao-2026-11-10/classroom-leitura-real-2026-11-11.json`, `verificacao-previa-publicada-2026-11-11.json` e `classroom-previa-real-publicada-2026-11-11.png`. A captura contém dados acadêmicos reais e deve permanecer fora de publicação pública no GitHub sem revisão específica.
- O teste confirma a leitura das turmas e a prévia dessa turma, não uma importação real nem o conteúdo de todas as turmas. OAuth continua em **modo de testes**, com somente a conta acadêmica previamente cadastrada. O acesso de outros alunos ainda exige preparação própria.
- Código completo permanece no workspace do VS Code. Esta atualização do registro é posterior ao pacote publicado; o ZIP aprovado foi preservado, sem substituir seu manifesto. A atualização das integrações no GitHub continua pendente.

## Preparação local após a decisão de público 13+

- `EDUTRACK_AI_AUDIENCE=includes_teens` passa a ser o padrão do código local e bloqueia chamadas Gemini, inclusive quando a flag, a chave e o modelo estão preenchidos e a requisição declara maioridade. Isso não verifica idade nem torna outro provedor automaticamente adequado a adolescentes.
- Suíte local completa final: **129 testes aprovados**; Ruff aprovado nos arquivos Python alterados; OpenSpec com **nove validações aprovadas**. Dois testes cobrem a incompatibilidade de público e a continuidade do planejador local; outros cinco cobrem a normalização restrita dos escopos. TypeScript e ESLint das telas modificadas também aprovados.
- Empacotamento reforçado para detectar também o formato de credencial iniciado por `AQ.`; verificado com valores sintéticos, sem reutilizar a chave revogada.
- [PUBLICO_13_MAIS.md](PUBLICO_13_MAIS.md) registra as adaptações ainda necessárias. As alterações de código posteriores à release `192434` foram publicadas na release `194748`; a atualização dessas integrações no GitHub permanece pendente.
- Ao preparar os escopos OAuth, o console Google converteu `classroom.coursework.me.readonly` para `classroom.student-submissions.me.readonly`. Código ajustado para aceitar somente essa equivalência explícita e o alias `email`, com cinco testes adicionais para sucesso e recusa de escopos indevidos. Os 23 testes específicos de Classroom passaram; Ruff aprovado. A conexão real e a leitura de atividades foram confirmadas posteriormente, esta última em 11/11.
- Avisos locais de Integrações e Privacidade esclarecem que a permissão Google também menciona notas, embora o EduTrack não consulte nem importe notas ou entregas.

## Reversão preparada

A release anterior permanece em `/opt/edutrack/releases/edutrack-entrega-final-20261103-221124`. As imagens anteriores foram preservadas como `edutrack-api:rollback-20261110` e `edutrack-web:rollback-20261110`. A configuração Nginx anterior está em `/opt/edutrack/backups/edutrack-nginx-before-classroom-20261110.conf`.

Para a publicação OAuth, a release imediatamente anterior `edutrack-entrega-final-20261110-192434` foi mantida; imagens preservadas como `edutrack-api:rollback-20261110-oauth` e `edutrack-web:rollback-20261110-oauth`. O backup privado de configuração é `/opt/edutrack/secrets/backend.env.before-oauth-20261110`. Não restaurar esse arquivo sem revisar conexões criadas após a ativação.

Uma reversão deve restaurar código/imagens/configuração após autorização, preservando as tabelas aditivas e os dados. Não executar `docker compose down -v` e não remover as chaves de criptografia de conexões existentes.

## Etapas ainda pendentes neste registro

- Preparar o acesso de outros alunos; OAuth ainda está em modo de testes e a validação real cobriu somente a conta acadêmica autorizada.
- Escolha de provedor compatível com adolescentes, definição de acesso/custos e implementação das proteções necessárias. A autorização anterior para Gemini gratuito não autoriza contratar outra API.
- Conferir o banco local antes de habilitar Classroom no localhost; a credencial está preparada, mas a flag permanece desligada.
- A importação real e a reimportação de SQL Fundamentals foram concluídas em 12/11, no curso Ciência da Computação, conforme registro ao final. Outras turmas não foram importadas. Pergunta real à Edu IA ainda depende de provedor compatível configurado.

Os testes simulados anteriores estão em [VALIDACAO_INTEGRACOES.md](VALIDACAO_INTEGRACOES.md). Eles não comprovam essas etapas externas. O guia de configuração permanece em [CLASSROOM_E_GEMINI.md](CLASSROOM_E_GEMINI.md).


## Nova importação completa — preparação local em 12/11/2026

A leitura real básica foi repetida no Chrome e confirmou seis turmas e dezesseis atividades de SQL Fundamentals. Nenhuma importação real foi realizada. O pedido ampliado inclui materiais, avisos, tópicos e links de anexos. A implementação local, sua validação e o plano de implantação estão em [IMPORTACAO_COMPLETA_CLASSROOM.md](IMPORTACAO_COMPLETA_CLASSROOM.md).

Migração 005, publicação da nova API/frontend e configuração dos três escopos adicionais foram autorizadas e concluídas em 12/11/2026. A renovação individual de consentimento, a prévia completa real e, após autorização específica, a importação e reimportação de SQL Fundamentals também foram confirmadas nesse dia, conforme os registros abaixo. A release pública anterior continua preservada.

## Importação completa publicada — 12/11/2026

- Release efetiva: `edutrack-entrega-final-20261112-171329`, com **227 arquivos** conferidos pelo manifesto. O pacote originalmente aprovado `165730` permanece intacto; foi substituído por correção restrita de compatibilidade SQL, documentada em [CORRECAO_SQL_CLASSROOM_2026-11-12.md](CORRECAO_SQL_CLASSROOM_2026-11-12.md).
- Backup SQL nativo com checksum e `RESTORE VERIFYONLY` concluídos; migração 005 aplicada, passando de 13 para 14 tabelas. A API recebeu CRUD somente em `conteudos_classroom`, sem permissão de criar tabelas. A tabela nova está vazia.
- API e frontend EduTrack recriados e saudáveis. Os IDs dos containers SQL e CRM e os hashes da configuração Nginx foram preservados. Login, privacidade, callback e CRM responderam HTTP 200; rotas privadas sem sessão responderam 401.
- `EDUTRACK_CLASSROOM_FULL_IMPORT_ENABLED=true` verificado no container. Gemini permanece desligado para o público 13+, sem outro chat externo configurado.
- Google Cloud: três escopos de leitura adicionais salvos (materiais, avisos e tópicos), totalizando sete com os existentes. OAuth continua Externo/Testando, somente com o usuário de teste já cadastrado; clientes preservados.
- Chrome autenticado: nova tela, modo completo, criação opcional de curso e aviso de atualização da autorização conferidos. A tela Google solicita o novo consentimento individual. Não foi executada importação real nesta publicação.
- Validação: 152 testes na imagem Linux inicial; após corrigir o tipo SQL, 47 testes relevantes passaram localmente e na imagem Linux final. O frontend não mudou nessa correção e seu build foi reaproveitado após comparação byte a byte. Os 41 testes frontend e dez validações OpenSpec anteriores permanecem registrados.
- Registro detalhado: [PUBLICACAO_CLASSROOM_COMPLETO_2026-11-12.md](PUBLICACAO_CLASSROOM_COMPLETO_2026-11-12.md). Evidências operacionais locais em `output/edutrack-classroom-completo-2026-11-12/`; capturas com conta real não foram incluídas no pacote público.
- As atualizações deste registro são posteriores ao empacotamento; os ZIPs e seus manifestos permanecem imutáveis. O código e a documentação canônicos foram atualizados no workspace do VS Code. Esta etapa não atualizou o GitHub.

### Consentimento renovado e prévia completa real

Após a confirmação explícita do titular para ampliar a leitura, o Chrome já estava no retorno OAuth com a mensagem **Conta conectada**. Não foi necessário clicar novamente em Permitir. Ao voltar a Integrações, o aviso de autorização adicional desapareceu e o modo de turma completa ficou disponível.

O teste autenticado no site público encontrou **seis turmas**. A prévia completa de **SQL Fundamentals · 202602 - CC 2A NOITE** apresentou **16 atividades, 24 materiais, 16 avisos e 43 links de anexos**, com títulos e prazos das atividades. Trata-se de consulta ao provedor real, distinta dos testes simulados anteriores. Não foram quantificados tópicos na interface, nem testadas integralmente as outras cinco turmas.

O campo de novo curso permaneceu vazio e **Importar turma completa** permaneceu desabilitado. Nenhum curso, disciplina, tarefa ou conteúdo foi importado por este teste. O próximo teste de gravação exige confirmar o destino e a turma; a publicação e o consentimento não substituem essa etapa.

Evidência local: `output/edutrack-classroom-completo-2026-11-12/previa-completa-real.png`. A captura contém informações acadêmicas reais e permanece fora dos pacotes públicos e do GitHub. A documentação e o OpenSpec foram atualizados localmente; não houve nova publicação de código, migração ou mudança de configuração nesta conferência.

### Importação e reimportação reais autorizadas

O titular solicitou criar **Ciência da Computação**, importar todo o conteúdo disponível de **SQL Fundamentals** e conferir ausência de duplicações. A operação foi executada pela interface pública no Chrome, usando a conexão individual já autorizada.

- Primeira execução: um curso, uma disciplina, 16 tarefas e 56 conteúdos (16 atividades originais, 24 materiais, 16 avisos), com 43 links de anexos. Os arquivos permanecem no serviço original.
- A disciplina foi aberta pelo atalho de sucesso. Curso correto, 16 tarefas pendentes e os filtros da biblioteca foram conferidos. Paginação: 30 itens na primeira página, 26 na segunda; filtros: 24 materiais, 16 avisos, 16 atividades originais.
- Segunda execução no curso existente: zero disciplinas, zero tarefas e zero conteúdos novos; 56 publicações atualizadas, 17 registros pessoais preservados (uma disciplina e 16 tarefas).
- SELECTs com o usuário restrito da API confirmaram um curso e uma disciplina dessa origem, 16 tarefas com prazo, 56 publicações e 43 links. Seis rótulos de tópicos distintos aparecem em 34 publicações. Não houve alteração manual de dados pelo SQL.
- Os hashes dos IDs, dos dados pessoais das tarefas e das publicações sem timestamp local permaneceram iguais antes/depois. Origens e vínculos de tarefas duplicados: zero.
- [Registro detalhado](IMPORTACAO_REAL_SQL_FUNDAMENTALS_2026-11-12.md). As evidências com dados reais permaneceram na pasta local `output/edutrack-classroom-completo-2026-11-12/`, fora do GitHub e dos ZIPs públicos.

Esta etapa não alterou código de produção, banco estrutural, Docker, Nginx, DNS ou certificados. A importação real de outras turmas e acesso de outros alunos não foram testados nesta validação.
