"""Reproduz tarefas 12-16 em banco descartável e salva evidências sem tokens."""

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.preview_app import build_preview  # noqa: E402


def main():
    destination = Path(sys.argv[1]).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    os.environ["EDUTRACK_QA_PREVIEW"] = "1"
    evidence = {"ambiente": "SQLite temporário; dados fictícios; nenhum serviço externo", "passos": []}
    with TemporaryDirectory(prefix="edutrack-evidencias-") as temp:
        app = build_preview(Path(temp) / "evidence.db", populate=False)
        with TestClient(app) as client:
            def record(method, path, body=None, expected=200):
                response = client.request(method, path, headers=auth, json=body)
                assert response.status_code == expected, (method, path, response.status_code)
                data = response.json() if response.content else None
                evidence["passos"].append({"metodo": method, "rota": path, "status": response.status_code, "resposta": data})
                return data

            login = client.post("/api/auth/login", json={"email": "avaliacao@example.com", "senha": "Demonstracao-local-2026"})
            assert login.status_code == 200
            auth = {"Authorization": "Bearer " + login.json()["access_token"]}
            evidence["passos"].append({"metodo": "POST", "rota": "/api/auth/login", "status": 200, "nota": "Credencial fictícia; token omitido."})
            course = record("POST", "/api/courses", {"nome": "Ciência da Computação - demonstração", "instituicao": "Ambiente fictício de avaliação"}, 201)
            discipline = record("POST", "/api/disciplines", {"nome": "Banco de Dados", "curso_id": course["id"], "professor": "Professor de demonstração", "carga_horaria": 80}, 201)
            record("PUT", "/api/disciplines/" + discipline["id"], {"nome": "Banco de Dados e SQL", "curso_id": course["id"], "professor": "Professor de demonstração", "carga_horaria": 80})
            tasks = []
            for i, title in enumerate(("Modelo relacional", "Normalização", "Consultas JOIN", "Revisão final")):
                task = record("POST", "/api/tasks", {"titulo": title, "disciplina_id": discipline["id"], "status": "concluida" if i < 3 else "pendente", "data_prevista": "2026-01-01T12:00:00Z"}, 201)
                tasks.append(task)
            record("GET", "/api/disciplines")
            record("GET", "/api/search/disciplines?q=Banco&overdue=true")
            summary = record("GET", "/api/dashboard")
            assert summary["progresso_percentual"] == 75
            link = record("GET", "/api/reports/generate")
            pdf = client.get(link["download_url"], headers=auth)
            assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-")
            (destination / "relatorio-progresso-demonstracao.pdf").write_bytes(pdf.content)
            evidence["passos"].append({"metodo": "GET", "rota": link["download_url"], "status": 200, "bytes": len(pdf.content), "arquivo": "relatorio-progresso-demonstracao.pdf"})
            for task in tasks:
                record("DELETE", "/api/tasks/" + task["id"], expected=204)
            record("DELETE", "/api/disciplines/" + discipline["id"], expected=204)
            record("DELETE", "/api/courses/" + course["id"], expected=204)
            assert record("GET", "/api/disciplines")["total"] == 0
            (destination / "openapi.json").write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2), encoding="utf-8")
    (destination / "crud-busca-progresso.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Login, criação, edição, consulta, busca OR, progresso 75%, PDF e exclusão: OK. Somente dados fictícios.")


if __name__ == "__main__":
    main()
