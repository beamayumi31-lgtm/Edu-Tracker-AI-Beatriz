"""Normalização dos conteúdos Google. Não baixa nem executa anexos externos."""

import re
from datetime import datetime, timezone
from ipaddress import ip_address
from urllib.parse import urlsplit

from fastapi import HTTPException


def safe_resource_url(value):
    """Só apresenta links web, sem credenciais, controles ou destinos locais."""
    if not isinstance(value, str) or len(value) > 4096 or any(ord(c) < 33 for c in value) or "\\" in value:
        return None
    try:
        parts = urlsplit(value)
        host = (parts.hostname or "").lower().rstrip(".")
        if parts.scheme not in {"https", "http"} or not host or parts.username or parts.password:
            return None
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal")) or "." not in host:
            return None
        # Navegadores aceitam IPv4 abreviado, octal ou hexadecimal; não expor esses aliases.
        if re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+))*", host):
            try:
                if not ip_address(host).is_global:
                    return None
            except ValueError:
                return None
        try:
            if not ip_address(host).is_global:
                return None
        except ValueError:
            pass
        return value
    except ValueError:
        return None


def content_text(value, limit):
    if value is None:
        return ""
    if not isinstance(value, str) or len(value) > limit:
        raise HTTPException(502, "O Classroom retornou conteúdo fora do formato esperado. Nada foi importado.")
    return value


def published_at(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(502, "O Classroom retornou uma data de publicação inválida.") from None


def attachments(item):
    materials = item.get("materials", [])
    if not isinstance(materials, list) or len(materials) > 20 or any(not isinstance(m, dict) for m in materials):
        raise HTTPException(502, "O Classroom retornou uma lista de anexos inválida.")
    result = []
    kinds = {"driveFile": "Arquivo", "youtubeVideo": "Vídeo", "link": "Link", "form": "Formulário", "gem": "Gemini Gem", "notebook": "NotebookLM"}
    for material in materials:
        key = next((key for key in kinds if key in material), None)
        data = material.get(key, {})
        if key == "driveFile" and isinstance(data, dict):
            data = data.get("driveFile", {})
        if not isinstance(data, dict):
            raise HTTPException(502, "O Classroom retornou um anexo inválido.")
        # Campos de acesso conforme o tipo; não usa thumbnails nem busca URLs no servidor.
        url_key = "formUrl" if key == "form" else "alternateLink" if key in {"driveFile", "youtubeVideo"} else "url"
        result.append({"tipo": kinds.get(key, "Anexo"), "titulo": content_text(data.get("title"), 3000) or kinds.get(key, "Anexo"),
                       "url": safe_resource_url(data.get(url_key))})
    return result


def normalize_content(item, kind, topics):
    # Importação tardia evita ciclo com o adaptador, que usa os normalizadores.
    from edutrack.google_classroom import external_id

    topic_id = external_id(item["topicId"]) if item.get("topicId") is not None else None
    description = content_text(item.get("text" if kind == "aviso" else "description"), 30000)
    title = (description.splitlines()[0][:200] if description else "Aviso da turma") if kind == "aviso" else content_text(item.get("title"), 3000) or "Conteúdo da turma"
    return {"origem_id": external_id(item.get("id")), "tipo": kind, "titulo": title, "descricao": description,
            "topico": topics.get(topic_id, ""), "url": safe_resource_url(item.get("alternateLink")),
            "anexos": attachments(item), "publicado_em": published_at(item.get("creationTime"))}
