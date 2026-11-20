# Tarefa 11 — Modelo de tarefas acadêmicas

EduTrack · Innovation Lab · Faculdade Impacta · 17/11/2026

**Situação:** Modelo existente auditado.

## Entrega e explicação

academic_tasks corresponde a tarefas_academicas: titulo, descricao, data_prevista, status e disciplina_id, com usuario_id e campos de auditoria adicionais. A FK composta mantém tarefa e disciplina no mesmo proprietário.

Estados permitidos: pendente, em_andamento, concluida e cancelada. Ao concluir, concluido_em deve estar preenchido. Minutos estimados não podem ser negativos. Canceladas não entram no denominador do progresso.

O fluxo de teste cria quatro atividades, conclui três, calcula 75%, produz o PDF e exclui apenas os registros fictícios. A evidência JSON registra retornos e contagens, sem JWT ou dados pessoais reais.

## Fontes e evidências

- [edutrack-api/edutrack/models.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/edutrack/models.py)
- [edutrack-api/scripts/evidence_innovation.py](https://github.com/antoniobrites/Faculdade-Impacta/blob/codex/innovation-lab-16-tarefas/2-semestre/Projeto%20Final/edutrack-api/scripts/evidence_innovation.py)

Consulte também o índice, a matriz de adaptações e os arquivos em `evidencias/` deste pacote.
