# Validação e limites da evidência

Ambiente: Windows, Python 3.12, frontend React/Next e backend FastAPI. Testes de API utilizam banco descartável, sem banco de alunos.

- Backend: 200 passed, 16 skipped, 1 aviso de depreciação do transporte TestClient/httpx.
- Os 16 testes pulados exigem chmod/chown POSIX do instalador privado de chave; não são testes de SQL Server.
- Frontend: 49 testes aprovados, sem falhas.
- Ruff, ESLint e TypeScript executados; resultados de build e OpenSpec ficam nos logs específicos da entrega.
- CRUD real da API em base descartável: criação, leitura, edição e exclusão; progresso de 75%; busca e PDF verificados.
- Navegação no Chrome: Dashboard, Disciplinas, Tarefas e Relatórios; busca e download acionados na interface.
- PDF renderizado e inspecionado visualmente. Conteúdo fictício: Banco de Dados e SQL, 3/4 tarefas.
- Consultas e DDL tiveram verificações de compilação para MSSQL. Não se afirma execução em SQL Server real nesta rodada.
- Serviços externos (Google, IA e envio de e-mail) não foram exercitados com credenciais reais nesta entrega.

Logs e screenshots são evidências pontuais; não garantem ausência absoluta de defeitos. Publicação e avaliação pedagógica são etapas separadas.
