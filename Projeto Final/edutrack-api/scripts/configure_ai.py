"""Configuração interativa local. Não imprime segredos nem faz chamadas pagas."""

import getpass
import os
import re
from pathlib import Path

from dotenv import set_key


def main():
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise SystemExit("No Linux, configure o provedor, a chave e o modelo no arquivo privado do serviço.")
    print("A chave será salva fora do Git e do OneDrive. Nenhuma chamada à IA será realizada.")
    provider = input("Provedor (gemini/openai) [gemini]: ").strip().lower() or "gemini"
    if provider not in {"gemini", "openai"}:
        raise SystemExit("Provedor inválido; nenhuma configuração foi alterada.")
    model = input(f"Nome exato do modelo disponível no projeto {provider}: ").strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", model):
        raise SystemExit("Nome de modelo inválido; nenhuma configuração foi alterada.")
    key = getpass.getpass("Cole a chave de API (entrada oculta): ").strip()
    if len(key) < 30 or any(char.isspace() for char in key) or (provider == "openai" and not key.startswith("sk-")):
        raise SystemExit("Formato de chave inválido; nenhuma configuração foi alterada.")
    target = Path(local) / "EduTrack" / "backend.env"
    target.parent.mkdir(parents=True, exist_ok=True)
    set_key(str(target), provider.upper() + "_API_KEY", key)
    set_key(str(target), provider.upper() + "_MODEL", model)
    set_key(str(target), "EDUTRACK_AI_PROVIDER", provider)
    if provider == "gemini":
        set_key(str(target), "EDUTRACK_GEMINI_ENABLED", "false")
        set_key(str(target), "EDUTRACK_GEMINI_PAID_SERVICE", "false")
        print("Gemini preparado e DESATIVADO. Revise público adulto e termos antes de habilitar EDUTRACK_GEMINI_ENABLED.")
        print("Contexto acadêmico não será enviado automaticamente no modo gratuito.")
    print("Configuração salva. Reinicie a API. Ative o consentimento na Edu IA para conversar.")
    print("Chamadas podem consumir créditos. Use limites de gasto no painel do provedor.")


if __name__ == "__main__":
    main()
