# Tarefa 14 — Busca avançada híbrida

EduTrack · Innovation Lab · Faculdade Impacta · 17/11/2026

**Situação:** Implementado e testado.

## Entrega e explicação

GET /api/search/disciplines aceita q, overdue, limit e offset. Com ambos os filtros, retorna nome parcial OU existência de tarefa pendente/em andamento atrasada. Tarefas concluídas e canceladas não tornam a disciplina atrasada. Sem filtros, lista somente as disciplinas da própria conta.

A consulta é parametrizada, escapa curingas literais e usa EXISTS para não duplicar disciplinas com várias tarefas atrasadas. Ordenação e paginação são estáveis; o cliente cancela requisições antigas e mostra carregamento, falha e resultados.

A interface fica em Disciplinas → Busca avançada. Foram testados OR, múltiplos resultados, isolamento, paginação, caracteres especiais e ausência de autenticação. A compilação para MSSQL foi conferida; isso não é execução no SQL Server real.

## Fontes e evidências

- [edutrack-api/edutrack/academic_search.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/edutrack/academic_search.py)
- [edutrack-app-completo/app/ui/DisciplineSearch.tsx](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-app-completo/app/ui/DisciplineSearch.tsx)

Consulte também o índice, a matriz de adaptações e os arquivos em `evidencias/` deste pacote.

## Revisão no GitHub

[PR final #2 — aberto para revisão do professor](https://github.com/antoniobrites/Faculdade-Impacta/pull/2). Código enviado na branch `codex/innovation-lab-16-tarefas`.
