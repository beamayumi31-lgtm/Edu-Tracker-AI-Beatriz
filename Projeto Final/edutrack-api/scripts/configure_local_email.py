"""Configuração privada de uso único por formulário de loopback, sem logs de segredos.

Execute diretamente e abra a URL exibida. Não publica nem modifica o banco.
Não sobrescreve uma configuração existente. Encerra após salvar ou em 10 minutos.
"""

import argparse
import html
import os
import re
import secrets
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace-revoked-key", action="store_true", help="Substituir somente após autorização e revogação da chave anterior.")
    args = parser.parse_args()
    destination = Path(os.environ["LOCALAPPDATA"]) / "EduTrack" / "backend.env"
    if destination.exists() and not args.replace_revoked_key:
        raise SystemExit("Já existe uma configuração privada; nenhum arquivo foi alterado.")
    existing = dotenv_values(destination) if destination.exists() else {}
    jwt_secret = existing.get("EDUTRACK_JWT_SECRET") or secrets.token_urlsafe(48)
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,}", jwt_secret):
        raise SystemExit("Segredo JWT existente requer revisão manual; nada foi alterado.")
    route = "/configurar/" + secrets.token_urlsafe(32)
    saved = False

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            # Nem a rota temporária nem o conteúdo do formulário entram em logs HTTP.
            pass

        def respond(self, status, content):
            body = content.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "strict-origin")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def allowed(self):
            return self.path == route and self.headers.get("Host") == authority

        def do_GET(self):
            if not self.allowed():
                return self.respond(404, "Não encontrado.")
            self.respond(200, "<!doctype html><html lang='pt-BR'><meta charset='utf-8'>"
                "<title>EduTrack — configuração privada local</title><h1>Configurar envio local</h1>"
                "<p>A chave será salva fora do projeto e do OneDrive. Não será exibida nesta página.</p>"
                "<p>Remetente: antoniombrites2716@gmail.com. A confirmação de e-mail será ativada.</p>"
                f"<form method='post' action='{html.escape(route)}' autocomplete='off'>"
                "<label>Chave SendGrid <input type='password' name='key' autocomplete='new-password' required></label>"
                "<button type='submit'>Salvar somente neste computador</button></form></html>")

        def do_POST(self):
            nonlocal saved
            if not self.allowed() or self.headers.get("Origin") != origin:
                return self.respond(403, "Origem não autorizada.")
            if self.headers.get("Content-Type") != "application/x-www-form-urlencoded":
                return self.respond(415, "Formato inválido.")
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 1024:
                    raise ValueError
                fields = parse_qs(self.rfile.read(length).decode("utf-8"), strict_parsing=True)
                key = fields.get("key", [""])[0].strip()
                if not re.fullmatch(r"SG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{32,}", key):
                    raise ValueError
            except (ValueError, UnicodeError):
                return self.respond(400, "Chave inválida; nada foi salvo.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            try:
                # A substituição exige uma opção explícita e preserva o segredo das sessões.
                mode = "w" if args.replace_revoked_key else "x"
                with destination.open(mode, encoding="utf-8") as output:
                    output.write("EDUTRACK_EMAIL_VERIFICATION_ENABLED=true\n")
                    output.write("SENDGRID_API_KEY=" + key + "\n")
                    output.write("EDUTRACK_EMAIL_FROM=antoniombrites2716@gmail.com\n")
                    output.write("EDUTRACK_EMAIL_FROM_NAME=EduTrack\n")
                    output.write("EDUTRACK_JWT_SECRET=" + jwt_secret + "\n")
            except FileExistsError:
                return self.respond(409, "Configuração já existente; nenhum segredo foi substituído.")
            saved = True
            self.respond(200, "<!doctype html><html lang='pt-BR'><meta charset='utf-8'>"
                "<title>EduTrack — configuração salva</title><h1>Configuração privada salva</h1>"
                "<p>A chave não foi exposta. Reinicie o backend local para ativar.</p></html>")

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        server.timeout = 1
        authority = f"127.0.0.1:{server.server_port}"
        origin = "http://" + authority
        print("Abra para configurar: " + origin + route, flush=True)
        deadline = time.monotonic() + 600
        while not saved and time.monotonic() < deadline:
            server.handle_request()
    print("Configuração salva; assistente encerrado." if saved else "Prazo encerrado; nada foi salvo.", flush=True)


if __name__ == "__main__":
    main()
