# Publicação da importação completa — 12/11/2026

Destino: https://srv1834976.hstgr.cloud. Publicação, backup, migração 005 e três escopos adicionais foram aprovados pelo titular. Nenhuma turma real foi importada durante esta implantação.

## Resultado verificado

| Item | Evidência |
|---|---|
| Release em execução | `edutrack-entrega-final-20261112-171329` |
| Pacote | 227 arquivos; 3.590.976 bytes |
| SHA-256 do ZIP | `553269d3a8bf8b7731d72ed2236a11d10993c9bbd3a62dec9e30b79df30a4ce5` |
| Migração 005 | SHA-256 `107b86185326f0609389bf8c5d926704e094e709f68a9ea969899984bc3b54b2`; aplicada |
| Banco | 14 tabelas; `conteudos_classroom` vazia; coluna de consentimento criada com padrão falso |
| Login restrito da API | SELECT, INSERT, UPDATE e DELETE na tabela nova; CREATE TABLE negado |
| Saúde | API e frontend saudáveis; readiness 200 |
| HTTPS | Login, privacidade e callback 200 |
| Proteção de sessão | Status da integração e biblioteca sem sessão: 401 |
| Preservação | IDs SQL/CRM e hashes Nginx iguais aos anteriores; CRM 200 |
| Configuração | Classroom completo ativo; Gemini e chat externo desligados |
| Google Cloud | Sete escopos salvos; somente os três de leitura novos foram adicionados |
| Público OAuth | Externo/Testando; um usuário de teste existente, sem ampliação da lista |
| Chrome autenticado | Consentimento renovado; prévia completa real validada, sem importação |

## Backup e reversão

Backup usado antes da migração:
`/opt/edutrack/backups/sql/EduTrackIA_20261112T201542Z.bak`

Tamanho: 5.890.048 bytes. SHA-256: `6a8dee1384b43c473b37f5f08b5c03f5b91ef40a81ea776fc5d05a84a7bd6c77`.
Criado com checksum, conferido com `RESTORE VERIFYONLY` e protegido com modo 600. Isso verifica o arquivo de backup; não representa um ensaio de restauração em outro banco.

Release anterior `edutrack-entrega-final-20261110-202738` preservada. Imagens anteriores: `edutrack-api:rollback-20261112-classroom-completo` e `edutrack-web:rollback-20261112-classroom-completo`. Configuração anterior privada: `/opt/edutrack/secrets/backend.env.before-complete-20261112`. Não remover estruturas aditivas nem dados ao reverter código. Não usar `docker compose down -v`.

## Correção necessária e testes

A primeira tentativa recusou `NVARCHAR(4096)` e foi revertida sem alterar estudos. O pacote original `165730` não foi sobrescrito. A correção afeta somente o tipo SQL da coluna URL, esquema/dicionário, teste de regressão e documentação; frontend e infraestrutura são idênticos. A [análise da correção](CORRECAO_SQL_CLASSROOM_2026-11-12.md) explica a diferença entre compilar DDL e executá-lo no SQL Server.

- Imagem Linux inicial: **152 testes aprovados em 162,48 s**.
- Correção: **47 testes Classroom/limites SQL aprovados localmente em 13,14 s** e **na imagem Linux final em 59,63 s**; rede desativada e SQLite descartável.
- DDL corrigido executado no SQL Server em transação de diagnóstico revertida, antes da aplicação definitiva.
- Ruff aprovado. Frontend já validado com 41 testes, TypeScript, ESLint e build de produção; sem mudança nessa correção. OpenSpec anteriormente validado em dez itens.
- Único aviso dos testes: depreciação conhecida do transporte Starlette/httpx, sem falha.

## Etapas que esta publicação não comprova

O cadastro de escopos Google não substitui o consentimento do aluno. Após a autorização do titular, a renovação da conexão e a prévia completa real foram confirmadas em uma turma, conforme a seção seguinte. Em etapa posterior e explicitamente autorizada, a gravação e a reimportação sem duplicação também foram validadas: [importação real de SQL Fundamentals](IMPORTACAO_REAL_SQL_FUNDAMENTALS_2026-11-12.md). Os testes locais anteriores continuam identificados como simulados.

OAuth continua em testes, portanto a publicação do site não libera integração para todas as contas Google. O planejador local permanece disponível; não foi ativado Gemini para o público 13+ nem contratado outro provedor.

Evidências operacionais locais: `output/edutrack-classroom-completo-2026-11-12/verificacao-publicacao.json`, `google-escopos-salvos.png` e `integracao-completa-publicada.png`. Capturas com conta real permanecem fora do pacote público. Documentação e OpenSpec foram atualizados no workspace após a publicação; os manifestos publicados continuam intactos.

## Prévia completa real após consentimento

Em 12/11/2026, após aprovação explícita do titular, o retorno OAuth já confirmou a conexão. A tela Integrações mostrou a conta acadêmica conectada e deixou de solicitar autorização adicional. A consulta autenticada no Chrome encontrou seis turmas; foi escolhida SQL Fundamentals para a prévia no modo completo.

| Conteúdo informado pela prévia real | Quantidade |
|---|---:|
| Atividades publicadas | 16 |
| Materiais | 24 |
| Avisos | 16 |
| Links de anexos | 43 |

Os prazos e títulos das atividades foram exibidos. A interface não fornece contagem de tópicos; não foi atribuída uma quantidade a eles. O resultado comprova a leitura completa dessa turma, não das outras cinco nem a gravação acadêmica. Nenhuma importação foi acionada: o curso de destino ainda não foi definido e o botão permaneceu desabilitado.

Captura local: `output/edutrack-classroom-completo-2026-11-12/previa-completa-real.png`. Ela contém dados reais e não integra o pacote público. A prévia foi deixada aberta no Chrome para o titular conferir.

## Importação real posterior à publicação

Após solicitação explícita, o curso Ciência da Computação foi criado e recebeu SQL Fundamentals. A primeira execução criou uma disciplina, 16 tarefas e 56 publicações, contendo 43 links. A segunda não criou registros novos: atualizou as 56 publicações e preservou a disciplina e as 16 tarefas. Conferências no SQL, somente de leitura, confirmaram IDs e dados das tarefas iguais, seis tópicos distintos representados nas publicações e nenhuma origem duplicada. A tabela `conteudos_classroom`, vazia no momento da publicação, passou a ter os 56 registros dessa importação. Consulte [as evidências e limites do teste](IMPORTACAO_REAL_SQL_FUNDAMENTALS_2026-11-12.md).
