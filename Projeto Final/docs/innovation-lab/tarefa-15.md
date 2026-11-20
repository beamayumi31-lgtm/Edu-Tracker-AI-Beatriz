# Tarefa 15 — Relatório PDF de progresso

EduTrack · Innovation Lab · Faculdade Impacta · 17/11/2026

**Situação:** Implementado e testado.

## Entrega e explicação

O botão na tela Relatórios solicita GET /api/reports/generate, que retorna um caminho fixo. O download em /api/reports/progress.pdf exige novamente autenticação. O frontend recebe os bytes pelo proxy de mesma origem e oferece o arquivo ao usuário.

ReportLab gera o documento em memória, com disciplina, concluídas, total e percentual acumulado. Entradas de texto são escapadas; não há carregamento de HTML/URLs fornecidos pelo aluno. O documento não inclui CPF, e-mail ou IDs.

Limites: até 500 disciplinas por PDF, 10 requisições por minuto por conta e limite de 3 MB no proxy. Excesso resulta em erro explícito. O PDF de evidência foi gerado pela API com 3 de 4 tarefas concluídas (75%) e teve sua página renderizada e inspecionada. O CSV semanal existente foi preservado.

## Fontes e evidências

- [edutrack-api/edutrack/progress_report.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/edutrack/progress_report.py)
- [edutrack-api/edutrack/academic_tools_routes.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/edutrack/academic_tools_routes.py)

Consulte também o índice, a matriz de adaptações e os arquivos em `evidencias/` deste pacote.
