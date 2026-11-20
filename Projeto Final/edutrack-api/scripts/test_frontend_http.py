"""Teste HTTP do frontend -> proxy -> API -> SQL Server, com dados fictícios removidos.

Só executa com --executar, com ambos os servidores locais já iniciados.
Não altera tabelas, não chama IA externa e não manipula o navegador do usuário.
"""
import argparse
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_sqlserver_integration import DATABASE, SERVER, cleanup, snapshot

from edutrack.config import Settings
from edutrack.database import make_engine
from edutrack.models import Course

ORIGIN = "http://localhost:3002"
BASE = ORIGIN + "/api/backend/"


def run(engine, identities):
    count = 0

    def check(condition, label):
        nonlocal count
        if not condition:
            raise AssertionError(label)
        count += 1
        print("OK:", label)

    def call(client, method, path, status=200, **kwargs):
        response = client.request(method, BASE + path, **kwargs)
        check(response.status_code == status, f"{method} {path}: {response.status_code}/{status}")
        if status == 204:
            return None
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        # O runtime do frontend pode bloquear CSRF antes da rota e responder texto.
        if status >= 400:
            return None
        raise AssertionError("A resposta de sucesso deveria ser JSON: " + path)

    with httpx.Client(headers={"Origin": ORIGIN}, timeout=45) as a, httpx.Client(
        headers={"Origin": ORIGIN}, timeout=45
    ) as b:
        check(a.get(ORIGIN + "/login").status_code == 200, "Página de login servida")
        if call(a, "GET", "auth/options")["email_verification_required"]:
            raise RuntimeError("Este teste legado de CRUD não envia e-mails. Use a suíte isolada para testar a confirmação; não desative a proteção de contas reais.")
        call(a, "GET", "courses", 401)
        users = []
        for client, (email, name) in zip([a, b], identities.items(), strict=True):
            password = secrets.token_urlsafe(30)
            created = call(client, "POST", "auth/register", 201, json={"nome": name, "email": email, "senha": password, "cpf": "00000000191"})
            response = client.post(BASE + "auth/login", json={"email": email, "senha": password})
            check(response.status_code == 200, "Login via frontend")
            check("access_token" not in response.json(), "JWT não exposto ao JavaScript")
            cookie = response.headers.get("set-cookie", "").lower()
            check("httponly" in cookie and "samesite=strict" in cookie, "Cookie protegido")
            user = response.json()["user"]
            check(user["id"] == created["id"], "Identidade confirmada")
            client.headers["X-EduTrack-User"] = user["id"]
            users.append(user)
        course = call(a, "POST", "courses", 201, json={"nome": "QA Integração — Curso", "instituicao": "Teste descartável"})
        with Session(engine) as db:
            check(db.scalar(select(Course.nome).where(Course.nome == course["nome"])) == course["nome"], "Gravação confirmada em conexão SQL independente")
        call(b, "GET", "courses/" + course["id"], 404)
        check(call(b, "GET", "courses")["total"] == 0, "Outra conta não vê o curso")
        call(a, "PUT", "courses/" + course["id"], json={"nome": "QA Integração — Editado", "data_inicio": "2026-10-01", "data_fim": "2026-12-01"})
        discipline = call(a, "POST", "disciplines", 201, json={"nome": "SQL", "curso_id": course["id"], "professor": "Fictício", "carga_horaria": 40})
        call(a, "DELETE", "courses/" + course["id"], 409)
        task = call(a, "POST", "tasks", 201, json={"titulo": "Revisar joins", "disciplina_id": discipline["id"], "minutos_estimados": 45, "data_prevista": "2026-10-09T20:00:00-03:00"})
        check(task["data_prevista"].endswith("Z") or task["data_prevista"].endswith("+00:00"), "Prazo serializado com fuso UTC")
        call(a, "PUT", "tasks/" + task["id"], json={"titulo": task["titulo"], "disciplina_id": discipline["id"], "status": "concluida"})
        check(call(a, "GET", "tasks/" + task["id"])["status"] == "concluida", "Conclusão persistida")
        call(a, "PUT", "tasks/" + task["id"], json={"titulo": task["titulo"], "disciplina_id": discipline["id"], "status": "pendente", "minutos_estimados": 45})
        end = datetime.now(timezone.utc).replace(microsecond=123000) - timedelta(seconds=5)
        body = {"tarefa_id": task["id"], "iniciado_em": (end - timedelta(minutes=25)).isoformat(), "finalizado_em": end.isoformat()}
        key = str(uuid4())
        entry = call(a, "POST", "study-sessions", 201, json=body, headers={"Idempotency-Key": key})
        repeated = call(a, "POST", "study-sessions", 201, json=body, headers={"Idempotency-Key": key})
        check(entry == repeated and entry["duracao_minutos"] == 25, "Sessão idempotente no SQL Server real")
        check(call(a, "GET", "study-sessions")["total"] == 1, "Repetição não duplica tempo")
        check(call(b, "GET", "study-sessions")["total"] == 0, "Histórico separado por aluno")
        call(a, "DELETE", "tasks/" + task["id"], 409)
        plan = call(a, "POST", "edu-ia/study-plan", json={"data_inicio": "2026-10-05", "dias": 7, "minutos_por_dia": 60})
        check(bool(plan["blocos"]) and plan["origem"] == "regras", "Plano criado sem provedor externo")
        check({block["tarefa_id"] for block in plan["blocos"]} == {task["id"]}, "Plano usa somente tarefas da conta")
        call(a, "POST", "courses", 403, json={"nome": "Não criar"}, headers={"Origin": "https://externo.example"})
        call(b, "POST", "courses", 409, json={"nome": "Não criar"}, headers={"X-EduTrack-User": users[0]["id"]})
        user = users[0]
        updated_name = user["nome"] + " Editado"
        call(a, "PUT", "me", json={"nome": updated_name})
        identities[user["email"]] = updated_name
        check(call(a, "GET", "me")["nome"] == updated_name, "Edição de perfil persistida")
        disposable = call(a, "POST", "courses", 201, json={"nome": "QA — exclusão sem vínculos"})
        call(a, "DELETE", "courses/" + disposable["id"], 204)
        call(a, "GET", "courses/" + disposable["id"], 404)
        # Verifica exclusão de tarefa e disciplina sem histórico.
        removable_d = call(a, "POST", "disciplines", 201, json={"nome": "QA — remover", "curso_id": course["id"]})
        removable_t = call(a, "POST", "tasks", 201, json={"titulo": "QA — remover", "disciplina_id": removable_d["id"]})
        call(a, "DELETE", "tasks/" + removable_t["id"], 204)
        call(a, "DELETE", "disciplines/" + removable_d["id"], 204)
        call(a, "POST", "auth/logout", json={})
        call(a, "GET", "courses", 401)
        check(a.get(ORIGIN + "/api/edu-ia").status_code == 410, "Proxy anônimo antigo desativado")
    print(f"HTTP: {count} verificações aprovadas.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--executar", action="store_true")
    args = parser.parse_args()
    if not args.executar:
        raise SystemExit("Use --executar somente com autorização para dados fictícios e limpeza.")
    settings = Settings(_env_file=None, sql_server=SERVER, sql_database=DATABASE, trust_server_certificate=True)
    if settings.sql_server != SERVER or settings.sql_database != DATABASE or settings.database_url:
        raise SystemExit("Destino diferente do banco local autorizado.")
    engine = make_engine(settings)
    before = snapshot(engine)
    run_id = uuid4().hex
    identities = {f"edutrack.qa.http.{run_id}.{i}@example.com": f"QA EduTrack HTTP {run_id} {i}" for i in [1, 2]}
    try:
        run(engine, identities)
    finally:
        try:
            removed = cleanup(engine, identities)
            print("Limpeza restrita aos registros fictícios:", removed)
            if before != snapshot(engine):
                raise RuntimeError("Dados ou estrutura diferem do estado inicial. Confira antes de continuar.")
            print("Dados e estrutura restaurados integralmente; nenhuma migração executada.")
        finally:
            engine.dispose()


if __name__ == "__main__":
    main()
