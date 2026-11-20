"""Planejador verificável: a IA não decide titularidade, duração total ou datas de entrega."""

from datetime import datetime, timedelta

from fastapi import HTTPException

from edutrack.schemas import PlanBlock, PlanInput, StudyPlan


def build_plan(context: dict, options: PlanInput) -> StudyPlan:
    if context["limite_atingido"]:
        raise HTTPException(
            422,
            "Há mais de 200 registros em uma categoria. Reduza as pendências antes de gerar o plano.",
        )
    disciplines = {item["id"]: item for item in context["disciplinas"]}
    courses = {item["id"] for item in context["cursos"]}
    tasks = sorted(
        context["tarefas"], key=lambda item: (item["data_prevista"] or "9999", item["id"])
    )
    remaining = {
        task["id"]: max(
            15, task["minutos_estimados"] if task["minutos_estimados"] is not None else 50
        )
        for task in tasks
    }
    blocks = []
    warnings = []
    if any(task["minutos_estimados"] is None for task in tasks):
        warnings.append(
            "Atividades sem estimativa receberam 50 minutos; ajuste conforme sua necessidade."
        )
    if any(
        task["minutos_estimados"] is not None and task["minutos_estimados"] < 15 for task in tasks
    ):
        warnings.append(
            "Atividades com menos de 15 minutos receberam um bloco mínimo de 15 minutos."
        )
    for day_index in range(options.dias):
        day = options.data_inicio + timedelta(days=day_index)
        budget = options.minutos_por_dia
        for task in tasks:
            discipline = disciplines.get(task["disciplina_id"])
            if not discipline or discipline["curso_id"] not in courses:
                raise HTTPException(
                    409, "Contexto acadêmico incompleto. Confira os vínculos das atividades."
                )
            while budget and remaining[task["id"]]:
                minutes = min(25, budget, remaining[task["id"]])
                blocks.append(
                    PlanBlock(
                        data=day,
                        tarefa_id=task["id"],
                        disciplina_id=discipline["id"],
                        curso_id=discipline["curso_id"],
                        titulo=task["titulo"],
                        minutos=minutes,
                        orientacao="Revise o conteúdo, pratique e anote dúvidas. Faça uma pausa entre os blocos.",
                    )
                )
                remaining[task["id"]] -= minutes
                budget -= minutes
                if (
                    task["data_prevista"]
                    and day > datetime.fromisoformat(task["data_prevista"]).date()
                ):
                    warnings.append(
                        f"O plano prevê estudo de '{task['titulo']}' após a data de entrega registrada."
                    )
    unfinished = [key for key, minutes in remaining.items() if minutes > 0]
    if unfinished:
        warnings.append(
            "O tempo disponível não cobre todas as estimativas; aumente os dias ou a disponibilidade."
        )
    if not tasks:
        warnings.append(
            "Cadastre atividades pendentes vinculadas a disciplinas para gerar blocos de estudo."
        )
    warnings.append(
        "Datas de entrega são comparadas em UTC. Os minutos diários são de estudo, sem incluir pausas."
    )
    return StudyPlan(
        resumo=f"Proposta de {len(blocks)} blocos em até {options.dias} dias, priorizando os prazos cadastrados.",
        blocos=blocks,
        alertas=list(dict.fromkeys(warnings)),
        tarefas_nao_planejadas=unfinished,
    )
