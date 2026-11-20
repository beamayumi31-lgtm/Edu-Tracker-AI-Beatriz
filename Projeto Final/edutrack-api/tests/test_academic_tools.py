"""Critérios das tarefas 12 a 16, sempre em SQLite descartável."""
import subprocess
import sys
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from uuid import UUID

import pytest
from conftest import academic_data, register_and_login
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.dialects import mssql

from edutrack.academic_search import discipline_search
from edutrack.models import Discipline, User, utc_now
from edutrack.progress import calculate_progress
from edutrack.progress_report import build_progress_pdf


def test_progress_cli_and_boundaries():
    assert calculate_progress(0, 0) == {"percentage": 0}
    assert calculate_progress(3, 4) == {"percentage": 75}
    assert calculate_progress(1, 8) == {"percentage": 13}
    for completed, total in ((-1, 2), (3, 2), (True, 2), (1.5, 2)):
        with pytest.raises(ValueError):
            calculate_progress(completed, total)
    script = Path(__file__).resolve().parents[1] / "scripts" / "calculate_progress.py"
    result = subprocess.run([sys.executable, str(script), "--completed", "3", "--total", "4"], capture_output=True, text=True)
    assert result.returncode == 0 and result.stdout.strip() == '{"percentage": 75}'
    assert subprocess.run([sys.executable, str(script), "--completed", "9", "--total", "4"], capture_output=True).returncode != 0


@pytest.mark.parametrize("path", ["search/disciplines", "reports/generate", "reports/progress.pdf"])
def test_private_tools_require_auth(client, path):
    assert client.get("/api/" + path).status_code == 401


def test_search_union_dates_pagination_and_isolation(client, auth):
    course, discipline, task = academic_data(client, auth)
    second = client.post("/api/disciplines", headers=auth, json={"nome": "Redes", "curso_id": course["id"]}).json()
    deadline = (utc_now() - timedelta(days=1)).isoformat() + "Z"
    for number in range(2):
        assert client.post("/api/tasks", headers=auth, json={"titulo": f"Atrasada {number}", "disciplina_id": second["id"], "data_prevista": deadline}).status_code == 201
    endpoint = "/api/search/disciplines"
    result = client.get(endpoint, headers=auth, params={"q": discipline["nome"], "overdue": True})
    assert result.status_code == 200
    assert {row["id"] for row in result.json()["items"]} == {discipline["id"], second["id"]}
    assert result.json()["total"] == 2
    assert client.get(endpoint, headers=auth, params={"overdue": True}).json()["total"] == 1
    assert client.get(endpoint, headers=auth, params={"q": "INEXISTENTE", "overdue": False}).json()["total"] == 0
    page1 = client.get(endpoint, headers=auth, params={"limit": 1}).json()
    page2 = client.get(endpoint, headers=auth, params={"limit": 1, "offset": 1}).json()
    assert page1["total"] == 2 and page1["items"][0]["id"] != page2["items"][0]["id"]
    other = register_and_login(client, 2)
    assert client.get(endpoint, headers=other, params={"q": discipline["nome"], "overdue": True}).json()["total"] == 0
    assert client.get(endpoint, headers=auth, params={"limit": 101}).status_code == 422
    assert client.get(endpoint, headers=auth, params={"q": "a" * 151}).status_code == 422


@pytest.mark.parametrize("status", ["concluida", "cancelada"])
def test_finished_tasks_not_overdue(client, auth, status):
    _, discipline, task = academic_data(client, auth)
    client.put(f"/api/tasks/{task['id']}", headers=auth, json={"titulo": "Encerrada", "disciplina_id": discipline["id"], "status": status, "data_prevista": "2020-01-01T00:00:00Z"})
    assert client.get("/api/search/disciplines?overdue=true", headers=auth).json()["total"] == 0


def test_search_literal_wildcards_and_mssql(client, auth):
    course, _, _ = academic_data(client, auth)
    name = "Desconto 50%_ [SQL] / básico"
    client.post("/api/disciplines", headers=auth, json={"nome": name, "curso_id": course["id"]})
    for term in ("%_", "[SQL]", "/"):
        rows = client.get("/api/search/disciplines", headers=auth, params={"q": term}).json()["items"]
        assert len(rows) == 1 and rows[0]["nome"] == name
    with client.app.state.session_factory() as db:
        user = db.scalar(select(User))
        query = discipline_search(user.id, "[SQL]", True, utc_now())
        compiled = query.compile(dialect=mssql.dialect())
        assert "EXISTS" in str(compiled) and " OR " in str(compiled)
        assert "%/[SQL]%" in compiled.params.values()


def test_pdf_e2e_progress_cancelled_and_private(client, auth, tmp_path):
    course, discipline, task = academic_data(client, auth)
    update = {"titulo": "Concluída", "disciplina_id": discipline["id"], "status": "concluida"}
    assert client.put(f"/api/tasks/{task['id']}", headers=auth, json=update).status_code == 200
    client.post("/api/tasks", headers=auth, json={"titulo": "Cancelada", "disciplina_id": discipline["id"], "status": "cancelada"})
    assert client.get("/api/dashboard", headers=auth).json()["progresso_percentual"] == 100
    link = client.get("/api/reports/generate", headers=auth).json()
    pdf = client.get(link["download_url"], headers=auth)
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-")
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.headers["cache-control"] == "no-store"
    assert "attachment" in pdf.headers["content-disposition"]
    text = "\n".join(page.extract_text() for page in PdfReader(BytesIO(pdf.content)).pages)
    assert discipline["nome"] in text and "100%" in text and "1 de 1" in text
    assert "example.com" not in text and discipline["id"] not in text
    other = register_and_login(client, 2)
    isolated = client.get(link["download_url"], headers=other)
    assert "Nenhuma disciplina cadastrada" in PdfReader(BytesIO(isolated.content)).pages[0].extract_text()
    assert discipline["nome"] not in PdfReader(BytesIO(isolated.content)).pages[0].extract_text()
    # O ciclo CRUD mantém a regra de exclusão: disciplina com tarefas responde 409.
    assert client.delete(f"/api/disciplines/{discipline['id']}", headers=auth).status_code == 409


def test_pdf_escapes_markup_and_paginates():
    rows = [{"name": '<img src="https://example.com/nao-acessar"/> & Banco de Dados ' + "longo " * 12,
             "total": 4, "completed": 3} for _ in range(80)]
    reader = PdfReader(BytesIO(build_progress_pdf(rows, utc_now())))
    assert len(reader.pages) > 1
    assert "75%" in reader.pages[0].extract_text()
    assert all("Página" in page.extract_text() for page in reader.pages)


def test_pdf_limit_is_explicit(client, auth):
    course, discipline, _ = academic_data(client, auth)
    with client.app.state.session_factory() as db:
        user = db.scalar(select(User))
        db.add_all([Discipline(usuario_id=user.id, curso_id=UUID(course["id"]), nome=f"Disciplina {i}") for i in range(500)])
        db.commit()
    result = client.get("/api/reports/progress.pdf", headers=auth)
    assert result.status_code == 422 and "nenhum relatório parcial" in result.text
