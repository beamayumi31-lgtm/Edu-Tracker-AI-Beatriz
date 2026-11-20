"""Importação completa com provedor simulado e SQLite descartável, sem contas reais."""

from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from conftest import academic_data, register_and_login
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateTable
from test_classroom import PREFIX, FakeGoogle, connect, import_body
from test_classroom import google as google  # noqa: F401

from edutrack.classroom_content import attachments, normalize_content, safe_resource_url
from edutrack.google_classroom import CONTENT_SCOPES, SCOPES, GoogleClassroom
from edutrack.integration_models import ClassroomContent


class FullGoogle(FakeGoogle):
    def __init__(self):
        super().__init__()
        self.scopes = " ".join((*SCOPES, *CONTENT_SCOPES))
        self.fail_resource = None
        self.extra_activity = False
        self.material_title = "Slides de SQL"
        self.many_materials = False

    def handle(self, request):
        path = request.url.path
        if path.endswith("/topics"):
            self.calls.append(request)
            return httpx.Response(200, json={"topic": [{"topicId": "55", "name": "Unidade 1"}]})
        if path.endswith(("/courseWorkMaterials", "/announcements")):
            self.calls.append(request)
            if path.endswith(self.fail_resource or "impossivel"):
                return httpx.Response(403, json={"error": "segredo-nao-expor"})
            if path.endswith("/courseWorkMaterials"):
                rows = [{"id": "201", "title": self.material_title, "state": "PUBLISHED", "topicId": "55", "description": "Revisão de SQL",
                         "materials": [{"driveFile": {"driveFile": {"title": "Slides.pdf", "alternateLink": "https://drive.google.com/file/d/exemplo/view"}}}],
                         "creationTime": "2026-11-10T20:30:00Z", "alternateLink": "https://classroom.google.com/c/exemplo/m/material"}]
                if self.many_materials:
                    rows = [{**rows[0], "id": str(1000 + i)} for i in range(501)]
                elif request.url.params.get("pageToken") == "segunda":
                    rows = [{"id": "202", "title": "Vídeo da aula", "state": "PUBLISHED", "materials": [{"youtubeVideo": {"title": "Aula", "alternateLink": "https://www.youtube.com/watch?v=exemplo"}}]}]
                else:
                    return httpx.Response(200, json={"courseWorkMaterial": rows, "nextPageToken": "segunda"})
                return httpx.Response(200, json={"courseWorkMaterial": rows})
            return httpx.Response(200, json={"announcements": [
                {"id": "301", "text": "Revisão antes da prova", "state": "PUBLISHED", "materials": [{"link": {"title": "Exercícios", "url": "https://example.com/exercicios"}}]},
                {"id": "302", "text": "Aviso em rascunho", "state": "DRAFT"},
            ]})
        response = super().handle(request)
        if path == "/v1/courses/11/courseWork":
            data = response.json()
            data["courseWork"][0].update(topicId="55", materials=[{"form": {"title": "Questionário", "formUrl": "https://docs.google.com/forms/d/exemplo/viewform"}}])
            if self.extra_activity:
                data["courseWork"].append({"id": "104", "title": "Nova após a prévia", "state": "PUBLISHED"})
            return httpx.Response(200, json=data)
        return response


@pytest.fixture
def full_google(client, google):
    client.app.state.settings.classroom_full_import_enabled = True
    fake = FullGoogle()
    client.app.state.google_client_factory = lambda config: GoogleClassroom(config, httpx.MockTransport(fake.handle))
    return fake


def complete_body(client, auth, course_id=None):
    version = client.get(PREFIX + "/status", headers=auth).json()["conexao_versao"]
    destination = {"curso_id": course_id} if course_id else {"novo_curso": {"nome": "Curso importado"}}
    return {**destination, "conexao_versao": version, "turmas": [{"turma_id": "11", "modo": "completo"}]}


def content_path(discipline):
    return PREFIX + "/disciplines/" + discipline + "/content"


def test_complete_scopes_preview_and_atomic_course_import(client, auth, full_google):
    params = connect(client, auth)
    assert set(params["scope"][0].split()) == set((*SCOPES, *CONTENT_SCOPES))
    status = client.get(PREFIX + "/status", headers=auth).json()
    assert status["completo_configurado"] and status["completo_autorizado"]
    preview = client.post(PREFIX + "/preview", headers=auth, json={"turma_id": "11", "completo": True})
    assert preview.status_code == 200, preview.text
    assert len(preview.json()["atividades"]) == 2
    assert len(preview.json()["conteudos"]) == 5
    assert client.get("/api/courses", headers=auth).json()["total"] == 0
    full_google.extra_activity = True
    result = client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth))
    assert result.status_code == 200, result.text
    body = result.json()
    assert body["tarefas_criadas"] == 3 and body["conteudos_criados"] == 6
    assert client.get("/api/courses", headers=auth).json()["total"] == 1
    content = client.get(content_path(body["disciplinas_ids"][0]), headers=auth).json()
    assert content["total"] == 6
    slides = next(c for c in content["items"] if c["titulo"] == "Slides de SQL")
    assert slides["topico"] == "Unidade 1" and slides["publicado_em"] == "2026-11-10T20:30:00Z"
    assert slides["anexos"][0]["url"].startswith("https://drive.google.com/")
    assert not any("studentSubmissions" in str(c.url) or "drive.googleapis" in str(c.url) for c in full_google.calls)


@pytest.mark.parametrize("resource", ["/courseWorkMaterials", "/announcements"])
def test_partial_failure_never_creates_course_or_records(client, auth, full_google, resource):
    connect(client, auth)
    full_google.fail_resource = resource
    result = client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth))
    assert result.status_code == 409 and "segredo-nao-expor" not in result.text
    for path in ("courses", "disciplines", "tasks"):
        assert client.get("/api/" + path, headers=auth).json()["total"] == 0
    with client.app.state.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(ClassroomContent)) == 0


def test_complete_limits_do_not_save_partial_results(client, auth, full_google):
    connect(client, auth)
    full_google.many_materials = True
    result = client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth))
    assert result.status_code == 422
    assert client.get("/api/courses", headers=auth).json()["total"] == 0


def test_complete_reimport_preserves_personal_edits_and_updates_library(client, auth, full_google):
    connect(client, auth)
    first = client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth)).json()
    task = client.get("/api/tasks", headers=auth).json()["items"][0]
    edited = {key: task[key] for key in ("titulo", "disciplina_id", "descricao", "data_prevista", "status", "minutos_estimados")}
    edited.update(titulo="Minha revisão", status="concluida")
    assert client.put("/api/tasks/" + task["id"], headers=auth, json=edited).status_code == 200
    full_google.material_title = "Slides revisados"
    second = client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth, first["curso_id"]))
    assert second.status_code == 200, second.text
    assert second.json()["tarefas_criadas"] == 0 and second.json()["conteudos_criados"] == 0
    assert second.json()["conteudos_atualizados"] == 5
    kept = client.get("/api/tasks/" + task["id"], headers=auth).json()
    assert kept["titulo"] == "Minha revisão" and kept["status"] == "concluida"
    library = client.get(content_path(first["disciplinas_ids"][0]), headers=auth).json()
    assert library["total"] == 5 and any(c["titulo"] == "Slides revisados" for c in library["items"])


def test_content_ownership_filter_pagination_and_disconnect(client, auth, full_google):
    connect(client, auth)
    result = client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth)).json()
    path = content_path(result["disciplinas_ids"][0])
    other = register_and_login(client, 2)
    assert client.get(path).status_code == 401
    assert client.get(path, headers=other).status_code == 404
    first = client.get(path + "?tipo=material&limit=1", headers=auth).json()
    second = client.get(path + "?tipo=material&limit=1&offset=1", headers=auth).json()
    assert first["total"] == 2 and second["total"] == 2
    assert len(first["items"]) == 1 and first["items"][0]["id"] != second["items"][0]["id"]
    assert client.delete(PREFIX + "/connection", headers=auth).status_code == 200
    assert client.get(path, headers=auth).json()["total"] == 5


def test_old_consent_does_not_grant_full_access(client, auth, google):
    connect(client, auth)
    client.app.state.settings.classroom_full_import_enabled = True
    result = client.post(PREFIX + "/preview", headers=auth, json={"turma_id": "11", "completo": True})
    assert result.status_code == 409
    assert client.get(PREFIX + "/status", headers=auth).json()["completo_autorizado"] is False
    assert client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth)).status_code == 409
    assert client.get("/api/courses", headers=auth).json()["total"] == 0


def test_missing_full_consent_is_rejected(client, auth, full_google):
    full_google.scopes = " ".join(SCOPES)
    response = client.post(PREFIX + "/start", headers=auth, json={}).json()
    state = parse_qs(urlsplit(response["authorization_url"]).query)["state"][0]
    assert client.post(PREFIX + "/callback", headers=auth, json={"state": state, "code": "ficticio"}).status_code == 422
    assert client.get(PREFIX + "/status", headers=auth).json()["connected"] is False


def test_all_activities_without_full_scope_and_reject_ambiguous_input(client, auth, google):
    course, _, _ = academic_data(client, auth)
    connect(client, auth)
    body = import_body(client, auth, course["id"], [])
    body["turmas"][0]["modo"] = "todas_atividades"
    result = client.post(PREFIX + "/import", headers=auth, json=body)
    assert result.status_code == 200 and result.json()["tarefas_criadas"] == 2
    body["turmas"][0]["atividades"] = ["101"]
    assert client.post(PREFIX + "/import", headers=auth, json=body).status_code == 422
    body["turmas"][0]["atividades"] = []
    body["novo_curso"] = {"nome": "Destino ambíguo"}
    assert client.post(PREFIX + "/import", headers=auth, json=body).status_code == 422


@pytest.mark.parametrize("url", ["javascript:alert(1)", "data:text/html,test", "file:///etc/passwd", "https://user:pass@example.com", "http://127.0.0.1/private", "http://localhost/private", "https://example.com\n.evil.test", "https://example.com\\@evil.test"])
def test_unsafe_attachment_links_are_not_clickable(url):
    assert safe_resource_url(url) is None
    item = attachments({"materials": [{"link": {"title": "Referência", "url": url}}]})[0]
    assert item["titulo"] == "Referência" and item["url"] is None


def test_content_schema_compiles_for_sql_server():
    ddl = str(CreateTable(ClassroomContent.__table__).compile(dialect=mssql.dialect()))
    assert "NVARCHAR(max)" in ddl and "ON DELETE CASCADE" in ddl
    assert "UNIQUE (usuario_id, google_sub, turma_id, tipo, origem_id)" in ddl


@pytest.mark.parametrize("url", ["http://127.1/file", "http://0177.0.0.1/file", "http://0x7f.0.0.1/file"])
def test_browser_ip_aliases_are_not_exposed(url):
    assert safe_resource_url(url) is None


def test_malformed_topic_is_rejected():
    with pytest.raises(HTTPException) as error:
        normalize_content({"id": "1", "topicId": []}, "material", {})
    assert error.value.status_code == 502


def test_removing_discipline_clears_library_without_resurrection(client, auth, full_google):
    connect(client, auth)
    first = client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth)).json()
    discipline_id = first["disciplinas_ids"][0]
    assert client.delete("/api/disciplines/" + discipline_id, headers=auth).status_code == 409
    for task in client.get("/api/tasks", headers=auth).json()["items"]:
        assert client.delete("/api/tasks/" + task["id"], headers=auth).status_code == 204
    assert client.delete("/api/disciplines/" + discipline_id, headers=auth).status_code == 204
    with client.app.state.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(ClassroomContent)) == 0
    assert client.post(PREFIX + "/import", headers=auth, json=complete_body(client, auth, first["curso_id"])).status_code == 409
