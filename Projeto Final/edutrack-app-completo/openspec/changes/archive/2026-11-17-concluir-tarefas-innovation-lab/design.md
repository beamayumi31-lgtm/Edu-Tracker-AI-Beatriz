# Decisões

SQLAlchemy produz consultas parametrizadas compatíveis com SQL Server. `EXISTS` evita duplicar disciplinas com várias tarefas atrasadas. Atraso significa prazo anterior ao instante UTC da consulta e status pendente/em_andamento. Nome vazio não corresponde a tudo quando o filtro de atrasos está ativo. Nome e atraso combinam por OR; sem filtros, retorna todas as disciplinas do próprio aluno.

Progresso usa tarefas concluídas / tarefas não canceladas. A função trata total zero e arredonda ao inteiro mais próximo, com metade para cima, como Math.round do frontend. A mesma função alimenta dashboard e PDF.

`GET /api/reports/generate` retorna um caminho de download fixo. `GET /api/reports/progress.pdf` recalcula e entrega o documento com autenticação e Cache-Control no-store. Não há arquivo público, token na URL nem acesso remoto a imagens/HTML do aluno. ReportLab recebe somente texto escapado e dados agregados.

Testes usam SQLite descartável, sem .env, SendGrid, Gemini, Classroom ou banco SQL Server real. Isso valida lógica e contratos; não comprova execução nova em produção.
