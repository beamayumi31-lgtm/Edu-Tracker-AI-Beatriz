"""Cliente Google de leitura, com destinos fixos, limites e erros sem credenciais."""

import base64
import hashlib
import json
import re
import time
from datetime import datetime
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

SCOPES = (
    "openid", "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
)
CONTENT_SCOPES = (
    "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
    "https://www.googleapis.com/auth/classroom.announcements.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
)


def requested_scopes(settings):
    return (*SCOPES, *CONTENT_SCOPES) if settings.classroom_full_import_enabled else SCOPES

# O console Google normaliza o escopo de atividades para este nome alternativo.
# Somente equivalências explícitas de leitura do próprio aluno são aceitas.
SCOPE_ALIASES = {
    "email": "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly":
        "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
}
ID_PATTERN = r"^[a-zA-Z0-9_-]{1,128}$"


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()


def seal(settings, user_id, value):
    payload = json.dumps({"user": str(user_id), "value": value}).encode()
    return Fernet(settings.integration_encryption_key.get_secret_value().encode()).encrypt(payload).decode()


def unseal(settings, user_id, value):
    try:
        payload = json.loads(Fernet(settings.integration_encryption_key.get_secret_value().encode()).decrypt(value.encode()))
        if payload["user"] != str(user_id):
            raise ValueError()
        return payload["value"]
    except (InvalidToken, ValueError, KeyError, TypeError):
        raise HTTPException(503, "Não foi possível abrir a conexão protegida. Reconecte sua conta Google.") from None


def authorization_url(settings, state, verifier):
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": settings.google_client_id, "redirect_uri": settings.google_redirect_uri,
        "response_type": "code", "scope": " ".join(requested_scopes(settings)), "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256",
        "access_type": "offline", "prompt": "consent select_account",
    })


def external_id(value):
    if not isinstance(value, str) or not re.fullmatch(ID_PATTERN, value):
        raise HTTPException(502, "O Classroom retornou um identificador inválido.")
    return value


def due_datetime(item):
    """O contrato Google define data e hora em UTC; um objeto vazio representa meia-noite."""
    if "dueDate" not in item and "dueTime" not in item:
        return None
    try:
        date, hour = item["dueDate"], item["dueTime"]
        return datetime(date["year"], date["month"], date["day"], hour.get("hours", 0), hour.get("minutes", 0), hour.get("seconds", 0))
    except (KeyError, TypeError, ValueError):
        raise HTTPException(502, "O Classroom retornou um prazo inválido. Nenhum registro foi importado.") from None


class GoogleClassroom:
    def __init__(self, settings, transport=None):
        self.settings = settings
        self.http = httpx.Client(timeout=12, follow_redirects=False, transport=transport)
        self.deadline = time.monotonic() + 45

    def close(self):
        self.http.close()

    def request(self, method, url, **kwargs):
        if time.monotonic() > self.deadline:
            raise HTTPException(504, "A consulta demorou demais. Selecione menos turmas e tente novamente.")
        try:
            response = self.http.request(method, url, **kwargs)
            if response.status_code == 429:
                raise HTTPException(429, "Limite temporário do Google. Aguarde um minuto e tente novamente.")
            if response.status_code in (400, 401, 403):
                raise HTTPException(409, "A autorização Google expirou, foi negada ou está incompleta. Reconecte a conta e confira as permissões da instituição.")
            response.raise_for_status()
            if len(response.content) > 4_000_000:
                raise ValueError()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError()
            return data
        except (httpx.HTTPError, ValueError):
            raise HTTPException(502, "Não foi possível consultar o Google. Tente novamente mais tarde.") from None

    def token(self, **data):
        result = self.request("POST", "https://oauth2.googleapis.com/token", data={
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret.get_secret_value(), **data,
        })
        token = result.get("access_token")
        if not isinstance(token, str) or not token or len(token) > 16000:
            raise HTTPException(502, "Resposta de autorização Google inválida.")
        return result

    def exchange(self, code, verifier):
        tokens = self.token(grant_type="authorization_code", code=code, code_verifier=verifier, redirect_uri=self.settings.google_redirect_uri)
        scope = tokens.get("scope", "")
        granted = {SCOPE_ALIASES.get(item, item) for item in scope.split()} if isinstance(scope, str) else set()
        if not set(requested_scopes(self.settings)).issubset(granted):
            self.revoke(tokens.get("refresh_token") or tokens["access_token"])
            raise HTTPException(422, "Autorize as permissões de leitura solicitadas para a turma e seus conteúdos.")
        self.full_content_authorized = set(CONTENT_SCOPES).issubset(granted)
        if not isinstance(tokens.get("refresh_token"), str) or not tokens["refresh_token"] or len(tokens["refresh_token"]) > 16000:
            raise HTTPException(409, "O Google não forneceu acesso renovável. Remova a permissão anterior no Google e conecte novamente.")
        identity = self.request("GET", "https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": "Bearer " + tokens["access_token"]})
        if not identity.get("email_verified") or not isinstance(identity.get("email"), str) or len(identity["email"]) > 255:
            raise HTTPException(422, "Use uma conta Google com e-mail confirmado.")
        return external_id(identity.get("sub")), identity["email"], tokens["refresh_token"]

    def access(self, refresh):
        return self.token(grant_type="refresh_token", refresh_token=refresh)["access_token"]

    def revoke(self, refresh):
        try:
            response = self.http.post("https://oauth2.googleapis.com/revoke", data={"token": refresh})
            return response.status_code in (200, 400)
        except httpx.HTTPError:
            return False

    def pages(self, path, key, access, params, limit):
        rows, seen = [], set()
        for _ in range(20):
            result = self.request("GET", "https://classroom.googleapis.com/v1/" + path,
                                  headers={"Authorization": "Bearer " + access}, params={"pageSize": 100, **params})
            batch = result.get(key, [])
            if not isinstance(batch, list) or any(not isinstance(item, dict) for item in batch):
                raise HTTPException(502, "Resposta inesperada do Classroom.")
            rows.extend(batch)
            if len(rows) > limit:
                raise HTTPException(422, "A consulta excede o limite seguro. Nenhum dado parcial foi importado.")
            token = result.get("nextPageToken")
            if not token:
                return rows
            if not isinstance(token, str) or len(token) > 4000 or token in seen:
                break
            seen.add(token)
            params = {**params, "pageToken": token}
        raise HTTPException(502, "Não foi possível concluir a paginação do Classroom.")

    def courses(self, access):
        rows = self.pages("courses", "courses", access, {"studentId": "me", "courseStates": "ACTIVE"}, 200)
        return [{"id": external_id(c.get("id")), "nome": str(c.get("name") or "Turma")[:150], "secao": str(c.get("section") or "")[:150]} for c in rows if c.get("courseState") == "ACTIVE"]

    def coursework_rows(self, access, course_id):
        rows = self.pages(f"courses/{external_id(course_id)}/courseWork", "courseWork", access, {"courseWorkStates": "PUBLISHED"}, 500)
        return [item for item in rows if item.get("state") == "PUBLISHED"]

    @staticmethod
    def task_items(rows):
        result = []
        for item in rows:
            if item.get("state") != "PUBLISHED":
                continue
            due = due_datetime(item)
            result.append({"id": external_id(item.get("id")), "titulo": str(item.get("title") or "Atividade")[:200],
                           "descricao": str(item.get("description") or "")[:30000], "data_prevista": due.isoformat() + "Z" if due else None})
        return result

    def coursework(self, access, course_id):
        return self.task_items(self.coursework_rows(access, course_id))

    def full_course(self, access, course_id):
        """Consulta a turma escolhida inteira antes de permitir qualquer gravação."""
        from edutrack.classroom_content import content_text, normalize_content

        base = f"courses/{external_id(course_id)}"
        topics = {external_id(t.get("topicId")): content_text(t.get("name"), 200)
                  for t in self.pages(base + "/topics", "topic", access, {}, 500)}
        tasks = self.coursework_rows(access, course_id)
        materials = self.pages(base + "/courseWorkMaterials", "courseWorkMaterial", access, {"courseWorkMaterialStates": "PUBLISHED"}, 500)
        notices = self.pages(base + "/announcements", "announcements", access, {"announcementStates": "PUBLISHED"}, 500)
        contents = [normalize_content(item, kind, topics) for kind, rows in (("atividade", tasks), ("material", materials), ("aviso", notices))
                    for item in rows if item.get("state") == "PUBLISHED"]
        return self.task_items(tasks), contents
