import json
from collections import defaultdict
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
from conftest import academic_data, register_and_login
from fastapi import HTTPException

from edutrack.agent import run_agent
from edutrack.config import Settings
from edutrack.planning import build_plan
from edutrack.schemas import ChatMessage, PlanInput


def test_plan_uses_own_tasks_and_respects_budget(client, auth):
    _, _, task = academic_data(client, auth)
    options = {"data_inicio": "2030-01-01", "dias": 3, "minutos_por_dia": 30}
    response = client.post("/api/edu-ia/study-plan", headers=auth, json=options)
    assert response.status_code == 200, response.text
    plan = response.json()
    assert plan["origem"] == "regras" and plan["somente_proposta"] is True
    assert sum(item["minutos"] for item in plan["blocos"]) == 90
    per_day = defaultdict(int)
    for item in plan["blocos"]:
        per_day[item["data"]] += item["minutos"]
        assert item["tarefa_id"] == task["id"]
        assert item["minutos"] <= 25
    assert max(per_day.values()) <= 30
    assert len(per_day) == 3
    assert any("após" in warning for warning in plan["alertas"])
    assert client.get("/api/tasks", headers=auth).json()["total"] == 1
    other = register_and_login(client, 2)
    empty = client.post("/api/edu-ia/study-plan", headers=other, json=options).json()
    assert empty["blocos"] == []


def test_ai_discloses_configuration_and_consent(client, auth):
    assert client.get("/api/edu-ia/status", headers=auth).json()["configured"] is False
    body = {"messages": [{"role": "user", "text": "Me ajude a estudar."}]}
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 422
    body["enviar_dados_ia"] = True
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 503
    body["usuario_id"] = str(uuid4())
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 422


def test_priority_capacity_and_empty_context():
    course_id, discipline_id, urgent_id, late_id = [str(uuid4()) for _ in range(4)]
    context = {
        "cursos": [{"id": course_id, "nome": "Curso"}],
        "disciplinas": [{"id": discipline_id, "curso_id": course_id, "nome": "Matéria"}],
        "tarefas": [
            {
                "id": late_id,
                "disciplina_id": discipline_id,
                "titulo": "Depois",
                "data_prevista": None,
                "minutos_estimados": 100,
            },
            {
                "id": urgent_id,
                "disciplina_id": discipline_id,
                "titulo": "Urgente",
                "data_prevista": "2030-01-01T18:00:00Z",
                "minutos_estimados": None,
            },
        ],
        "limite_atingido": False,
    }
    plan = build_plan(context, PlanInput(data_inicio=date(2030, 1, 1), dias=1, minutos_por_dia=30))
    assert str(plan.blocos[0].tarefa_id) == urgent_id
    assert len(plan.tarefas_nao_planejadas) == 2
    assert any("50 minutos" in message for message in plan.alertas)
    context["limite_atingido"] = True
    with pytest.raises(HTTPException):
        build_plan(context, PlanInput(data_inicio=date(2030, 1, 1)))


class FakeProvider:
    """Provedor simulado: não faz chamadas externas nem consome créditos."""

    def __init__(self, responses):
        self.queue = list(responses)
        self.calls = []
        self.responses = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.queue.pop(0)


def tool(name, arguments):
    return SimpleNamespace(
        output=[
            SimpleNamespace(
                type="function_call", name=name, arguments=json.dumps(arguments), call_id="call-1"
            )
        ],
        output_text="",
    )


def test_agent_function_tools_and_no_private_account_data(client, auth):
    academic_data(client, auth)
    context = client.get("/api/edu-ia/context", headers=auth).json()
    assert "aluno1@example.com" not in json.dumps(context)
    assert "senha_hash" not in json.dumps(context)
    fake = FakeProvider(
        [
            tool("consultar_contexto_academico", {}),
            tool(
                "propor_plano_estudo",
                {
                    "data_inicio": "2030-01-01",
                    "dias": 3,
                    "minutos_por_dia": 30,
                    "objetivo": "Revisar",
                },
            ),
            SimpleNamespace(
                output=[],
                output_text="Estude o modelo relacional em três dias e revise os conceitos.",
            ),
        ]
    )
    result = run_agent(
        client.app.state.settings,
        [ChatMessage(role="user", text="Monte meu plano")],
        context,
        client=fake,
    )
    assert result["plan"] is not None
    assert result["tools_used"] == ["consultar_contexto_academico", "propor_plano_estudo"]
    assert all(call["store"] is False for call in fake.calls)
    assert all(call["parallel_tool_calls"] is False for call in fake.calls)


@pytest.mark.parametrize(
    "name,args",
    [
        ("consultar_contexto_academico", {"usuario_id": "outra-conta"}),
        ("executar_sql", {"query": "DELETE FROM usuarios"}),
        (
            "propor_plano_estudo",
            {"data_inicio": "2030-01-01", "dias": 999, "minutos_por_dia": 30, "objetivo": "teste"},
        ),
    ],
)
def test_agent_rejects_unapproved_tools_and_arguments(name, args):
    fake = FakeProvider([tool(name, args)])
    with pytest.raises(HTTPException) as raised:
        run_agent(
            Settings(_env_file=None),
            [ChatMessage(role="user", text="oi")],
            {"limite_atingido": False},
            client=fake,
        )
    assert raised.value.status_code == 502


def test_agent_bounds_calls():
    fake = FakeProvider([tool("consultar_contexto_academico", {})] * 4)
    with pytest.raises(HTTPException) as raised:
        run_agent(
            Settings(_env_file=None),
            [ChatMessage(role="user", text="oi")],
            {"limite_atingido": False},
            client=fake,
        )
    assert raised.value.status_code == 502
    assert len(fake.calls) == 4
