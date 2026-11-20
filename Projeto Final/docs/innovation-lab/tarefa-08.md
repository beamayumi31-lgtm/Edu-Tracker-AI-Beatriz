# Tarefa 08 — Primeira proposta e modelo de disciplinas

EduTrack · Innovation Lab · Faculdade Impacta · 17/11/2026

**Situação:** Modelo existente auditado.

## Entrega e explicação

A entidade subjects do enunciado corresponde a disciplinas: id, nome, professor, carga_horaria e usuario_id. O EduTrack inclui curso_id, pois o mesmo aluno pode organizar graduação e cursos externos.

O modelo SQLAlchemy contém UUID, FK de usuário e FK composta (curso_id, usuario_id), impedindo associações entre proprietários diferentes. A carga horária é opcional e não negativa. A proposta auditar-modelo-academico registra a auditoria do esquema já existente, sem fingir sua criação em 17/11.

O ciclo CRUD foi executado em base temporária; SQL Server real não recebeu DDL. Arquivos de migração permanecem disponíveis para instalação autorizada.

## Fontes e evidências

- [edutrack-api/edutrack/models.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/edutrack/models.py)
- [edutrack-app-completo/openspec](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-app-completo/openspec)

Consulte também o índice, a matriz de adaptações e os arquivos em `evidencias/` deste pacote.
