import json

import httpx
import pytest
from fastapi.testclient import TestClient

from edutrack.gemini import GeminiClient
from scripts.run_adult_ai_demo import build_demo, main


def login(client):
    result = client.post("/api/auth/login", json={"email": "avaliacao@example.com", "senha": "Demonstracao-local-2026"})
    assert result.status_code == 200
    return {"Authorization": "Bearer " + result.json()["access_token"]}


def test_demo_requires_explicit_private_adult_confirmation(tmp_path):
    with pytest.raises(ValueError):
        build_demo(tmp_path / "demo.db")
    with pytest.raises(SystemExit):
        main([])


def test_no_key_demo_ignores_host_secrets_and_keeps_local_plan(tmp_path, monkeypatch):
    for name in ["GEMINI_API_KEY", "OPENAI_API_KEY", "OPENAI_MODEL", "GEMINI_MODEL",
                 "SENDGRID_API_KEY", "EDUTRACK_DATABASE_URL", "EDUTRACK_GOOGLE_CLIENT_SECRET",
                 "EDUTRACK_INTEGRATION_ENCRYPTION_KEY", "EDUTRACK_JWT_SECRET"]:
        monkeypatch.setenv(name, "synthetic-host-sentinel-never-use")
    for name in ["EDUTRACK_GEMINI_ENABLED", "EDUTRACK_GEMINI_PAID_SERVICE",
                 "EDUTRACK_CLASSROOM_ENABLED", "EDUTRACK_CLASSROOM_FULL_IMPORT_ENABLED"]:
        monkeypatch.setenv(name, "true")
    monkeypatch.setenv("HTTPS_PROXY", "http://synthetic-proxy.invalid")
    app = build_demo(tmp_path / "demo.db", confirmed_private_adults=True)
    s = app.state.settings
    assert not s.ai_configured and not s.ai_context_allowed
    assert s.ai_audience == "adults_only" and s.ai_provider == "gemini"
    assert s.gemini_api_key is None and s.openai_api_key is None and s.sendgrid_api_key is None
    assert s.database_url is None and s.google_client_secret is None and s.integration_encryption_key is None
    assert not s.classroom_enabled and not s.classroom_full_import_enabled
    assert "sentinel" not in app.state.jwt_secret
    def unexpected(*args, **kwargs):
        raise AssertionError("Provider must not be created in no-key mode")
    monkeypatch.setattr("edutrack.ai_routes.GeminiClient", unexpected)
    with TestClient(app) as client:
        auth = login(client)
        assert client.get("/api/edu-ia/status", headers=auth).json()["configured"] is False
        r = client.post("/api/edu-ia/chat", headers=auth, json={"messages": [{"role": "user", "text": "SQL?"}], "enviar_dados_ia": True, "maior_de_idade": True})
        assert r.status_code == 503
        r = client.post("/api/edu-ia/study-plan", headers=auth, json={"data_inicio": "2026-11-17", "dias": 2, "minutos_por_dia": 60})
        assert r.status_code == 200 and r.json()["origem"] == "regras"
        assert r.json()["blocos"]


def test_demo_live_mode_mock_sends_only_message_and_requires_consent(tmp_path, monkeypatch):
    app = build_demo(tmp_path / "demo.db", confirmed_private_adults=True, api_key="synthetic-test-key")
    requests = []
    def handle(request):
        requests.append(request)
        assert request.url.host == "generativelanguage.googleapis.com"
        body = json.loads(request.content)
        assert "tools" not in body
        assert body["generationConfig"]["maxOutputTokens"] == 1600
        assert body["contents"] == [{"role": "user", "parts": [{"text": "Explique SQL"}]}]
        assert "tarefas" not in body and "cursos" not in body
        return httpx.Response(200, json={"candidates": [{"finishReason": "STOP", "content": {"role": "model", "parts": [{"text": "Resposta simulada"}]}}]})
    monkeypatch.setattr("edutrack.ai_routes.GeminiClient", lambda settings: GeminiClient(settings, httpx.MockTransport(handle)))
    with TestClient(app) as client:
        auth = login(client)
        body = {"messages": [{"role": "user", "text": "Explique SQL"}]}
        assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 422
        body["enviar_dados_ia"] = True
        assert client.post("/api/edu-ia/chat", headers=auth, json=body).status_code == 422
        assert not requests
        body["maior_de_idade"] = True
        result = client.post("/api/edu-ia/chat", headers=auth, json=body)
        assert result.status_code == 200 and result.json()["reply"] == "Resposta simulada"
        assert len(requests) == 1


def test_demo_jwt_is_ephemeral(tmp_path):
    one = build_demo(tmp_path / "one.db", confirmed_private_adults=True)
    two = build_demo(tmp_path / "two.db", confirmed_private_adults=True)
    assert one.state.jwt_secret != two.state.jwt_secret
    one.state.session_factory.kw["bind"].dispose()
    two.state.session_factory.kw["bind"].dispose()


def test_live_demo_rejects_inherited_network_overrides(tmp_path, monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://synthetic-proxy.invalid")
    with pytest.raises(ValueError, match="clean process"):
        build_demo(tmp_path / "demo.db", confirmed_private_adults=True, api_key="synthetic-test-key")
