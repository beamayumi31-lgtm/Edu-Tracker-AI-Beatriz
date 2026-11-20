# Why

As tarefas 12, 14 e 15 de Innovation Lab exigem cálculo Python, busca avançada e PDF. O usuário confirmou em 17/11/2026 a manutenção de SQL Server/Python com documentação das adaptações. Preservaremos React e o contrato CRUD existente.

# What Changes

- Função compartilhada de progresso e CLI `scripts/calculate_progress.py`, com saída JSON `percentage`.
- Busca autenticada por nome da disciplina OU existência de tarefa atrasada, paginada e isolada por aluno.
- Geração em memória de PDF de progresso e download autenticado pela interface de relatórios.
- Testes, evidências fictícias e documentação individual das 16 tarefas.

# Impact

Backend FastAPI, proxy de mesma origem e relatórios. Sem migração ou alteração de banco real. Dependência ReportLab. A publicação em produção não faz parte desta mudança local. Fontes de dados: registros do aluno autenticado. Limite explícito de 500 disciplinas por PDF; excedentes não são silenciosamente omitidos.

Fora do escopo: migrar para Xano/FlutterFlow, notas de alunos, enviar trabalhos ao Classroom, chamar IA externa, mudar OAuth ou gerar evidências históricas fictícias.
