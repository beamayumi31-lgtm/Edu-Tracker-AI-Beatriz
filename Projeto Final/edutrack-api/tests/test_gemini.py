import json

import httpx
import pytest
from conftest import academic_data
from fastapi import HTTPException
from pydantic import SecretStr

from edutrack.agent import run_agent
from edutrack.config import Settings
from edutrack.gemini import GeminiClient
from edutrack.schemas import ChatMessage


def settings():
    return Settings(_env_file=None, ai_provider="gemini", ai_audience="adults_only", gemini_enabled=True, GEMINI_API_KEY="chave-ficticia-testes", GEMINI_MODEL="modelo-ficticio")


def reply(parts, **extra):
    return {"candidates": [{"content": {"role": "model", "parts": parts}, "finishReason": "STOP", **extra}]}


@pytest.mark.parametrize("key", ["chave-ficticia-testes", "AQ.synthetic_not_real.auth-key-123456789"])
def test_general_chat_has_no_tools_or_student_context_and_header_key(key):
    def handle(request):
        assert request.headers["x-goog-api-key"] == key
        assert not request.url.query
        body = json.loads(request.content)
        assert "tools" not in body and "cursos" not in body
        assert body["contents"][0]["parts"] == [{"text": "Explique SQL"}]
        return httpx.Response(200, json=reply([{"text": "SQL consulta dados."}]))
    config = settings()
    config.gemini_api_key = SecretStr(key)
    with_client = GeminiClient(config, httpx.MockTransport(handle))
    try:
        result = with_client.general_chat([ChatMessage(role="user", text="Explique SQL")])
        assert result == {"reply": "SQL consulta dados.", "tools_used": [], "plan": None}
    finally:
        with_client.close()


def test_gemini_function_roundtrip_preserves_signature():
    calls = []
    def handle(request):
        body = json.loads(request.content)
        calls.append(body)
        if len(calls) == 1:
            assert body["toolConfig"]["functionCallingConfig"]["allowedFunctionNames"] == ["consultar_contexto_academico"]
            return httpx.Response(200, json=reply([{"functionCall": {"name": "consultar_contexto_academico", "args": {}}, "thoughtSignature": "assinatura-opaca"}]))
        assert body["contents"][1]["parts"][0]["thoughtSignature"] == "assinatura-opaca"
        response = body["contents"][2]["parts"][0]["functionResponse"]
        assert response["name"] == "consultar_contexto_academico"
        assert response["response"]["result"]["tarefas"] == []
        return httpx.Response(200, json=reply([{"text": "Você ainda não cadastrou atividades."}]))
    client = GeminiClient(settings(), httpx.MockTransport(handle))
    try:
        result = run_agent(settings(), [ChatMessage(role="user", text="Me ajude")], {"limite_atingido": False, "tarefas": []}, client=client)
        assert result["tools_used"] == ["consultar_contexto_academico"]
        assert len(calls) == 2
    finally:
        client.close()


@pytest.mark.parametrize("status,payload,expected", [(429, {"key": "NUNCA-EXIBIR"}, 429), (403, {}, 502), (200, {}, 502), (200, reply([{"text": "bloqueada"}], finishReason="SAFETY"), 502), (200, reply(["malformado"]), 502), (200, reply([{"thought": True, "text": "interno"}]), 502)])
def test_provider_failures_sanitized(status, payload, expected):
    client = GeminiClient(settings(), httpx.MockTransport(lambda _: httpx.Response(status, json=payload)))
    try:
        with pytest.raises(HTTPException) as raised:
            client.general_chat([ChatMessage(role="user", text="oi")])
        assert raised.value.status_code == expected
        assert "NUNCA-EXIBIR" not in str(raised.value.detail)
        assert "chave-ficticia" not in str(raised.value.detail)
    finally:
        client.close()


def test_free_mode_route_never_loads_context_and_keeps_local_planner(client, auth, monkeypatch):
    academic_data(client, auth)
    config = client.app.state.settings
    config.ai_provider = "gemini"
    config.ai_audience = "adults_only"
    config.gemini_enabled = True
    config.gemini_api_key = SecretStr("chave-ficticia-testes")
    config.gemini_model = "modelo-ficticio"
    requests = []
    def handle(request):
        requests.append(request.content.decode())
        return httpx.Response(200, json=reply([{"text": "Uma chave primária identifica um registro."}]))
    monkeypatch.setattr("edutrack.ai_routes.GeminiClient", lambda s: GeminiClient(s, httpx.MockTransport(handle)))
    body = {"messages": [{"role": "user", "text": "Explique chave primária"}], "enviar_dados_ia": True, "maior_de_idade": True}
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 200
    assert "Modelo relacional" not in requests[0] and "aluno1@example.com" not in requests[0]
    body["enviar_dados_ia"] = False
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 422
    plan = {"data_inicio": "2030-01-01", "usar_ia": True, "enviar_dados_ia": True, "maior_de_idade": True}
    assert client.post("/api/edu-ia/study-plan", headers=auth, json=plan).status_code == 422
    plan["usar_ia"] = False
    assert client.post("/api/edu-ia/study-plan", headers=auth, json=plan).status_code == 200
    assert len(requests) == 1


def test_gemini_disabled_or_missing_adult_confirmation_never_calls_provider(client, auth, monkeypatch):
    config = client.app.state.settings
    config.ai_provider = "gemini"
    config.ai_audience = "adults_only"
    config.gemini_api_key = SecretStr("chave-ficticia-testes")
    config.gemini_model = "modelo-ficticio"
    config.gemini_enabled = False
    def forbidden(*args):
        raise AssertionError("O provedor não deve ser chamado")
    monkeypatch.setattr("edutrack.ai_routes.GeminiClient", forbidden)
    body = {"messages": [{"role": "user", "text": "Oi"}], "enviar_dados_ia": True}
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 503
    config.gemini_enabled = True
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 422


def test_teen_audience_blocks_gemini_even_with_adult_declaration(client, auth, monkeypatch):
    config = client.app.state.settings
    config.ai_provider = "gemini"
    config.ai_audience = "includes_teens"
    config.gemini_enabled = True
    config.gemini_api_key = SecretStr("chave-ficticia-testes")
    config.gemini_model = "modelo-ficticio"
    config.gemini_paid_service = True

    def forbidden(*args, **kwargs):
        raise AssertionError("Público adolescente não pode chamar Gemini")

    monkeypatch.setattr("edutrack.ai_routes.GeminiClient", forbidden)
    monkeypatch.setattr("edutrack.ai_routes.run_agent", forbidden)
    body = {"messages": [{"role": "user", "text": "Explique SQL"}], "enviar_dados_ia": True, "maior_de_idade": True}
    assert client.get("/api/edu-ia/status", headers=auth).json()["configured"] is False
    assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 503
    plan = {"data_inicio": "2030-01-01", "usar_ia": True, "enviar_dados_ia": True, "maior_de_idade": True}
    assert client.post("/api/edu-ia/study-plan", headers=auth, json=plan).status_code == 503
    plan["usar_ia"] = False
    assert client.post("/api/edu-ia/study-plan", headers=auth, json=plan).status_code == 200


def test_default_audience_cannot_activate_gemini():
    config = Settings(_env_file=None, ai_provider="gemini", gemini_enabled=True, GEMINI_API_KEY="ficticia", GEMINI_MODEL="modelo-ficticio")
    assert config.ai_audience == "includes_teens"
    assert config.ai_configured is False


def test_settings_require_explicit_model_and_oauth_credentials():
    assert not Settings(_env_file=None, ai_provider="gemini", GEMINI_API_KEY="ficticia", GEMINI_MODEL=None).ai_configured
    with pytest.raises(ValueError):
        Settings(_env_file=None, GEMINI_MODEL="../segredo")
    with pytest.raises(ValueError):
        Settings(_env_file=None, classroom_enabled=True, google_client_id=None)
