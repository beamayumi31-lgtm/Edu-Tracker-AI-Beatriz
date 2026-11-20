"""Empacota fontes por lista permitida, sem alterar originais nem publicar arquivos."""

import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "work"
SKIP = {"__pycache__", "node_modules", ".git", ".venv", ".next", "dist", ".wrangler", ".pytest_cache", ".ruff_cache"}
# A inspeção por padrões é uma defesa adicional; segredos ficam fora da lista de arquivos.
PATTERNS = [
    r"SG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{30,}",
    r"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}",
    r"AIza[A-Za-z0-9_-]{35}",
    r"\bAQ\.[A-Za-z0-9_.=+/-]{30,}",
    r"GOCSPX-[A-Za-z0-9_-]{20,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
]


def files_under(source):
    paths = source.rglob("*") if source.is_dir() else [source]
    for path in paths:
        if not path.is_file() or any(part in SKIP or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.suffix in {".pyc", ".db", ".log", ".tsbuildinfo"} or (path.name.startswith(".env") and path.name != ".env.example"):
            continue
        if path.is_symlink():
            raise RuntimeError("Link simbólico fora do pacote: " + str(path))
        yield path


def main():
    target = ROOT / "output" / ("edutrack-entrega-final-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    target.mkdir(parents=True, exist_ok=False)
    frontend = ["app", "public", "scripts", "tests", "docs", "openspec", ".env.example", ".gitignore", ".openai/hosting.json", "package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "next.config.ts", "tsconfig.json", "eslint.config.mjs", "vite.config.ts", "README.md"]
    backend = ["edutrack", "scripts", "tests", "migrations", "docs", ".env.example", ".gitignore", "pyproject.toml", "requirements.lock.txt", "README.md"]
    selected = [(WORK / "edutrack-app-completo" / name) for name in frontend]
    selected += [(WORK / "edutrack-api" / name) for name in backend]
    selected += list((WORK / "edutrack-documentacao").glob("*.md"))
    selected.append(WORK / "edutrack-documentacao" / "evidencias" / "validacao-final")
    selected.append(WORK / "edutrack-documentacao" / "evidencias" / "integracoes-2026-11-09")
    selected.append(WORK / "edutrack-documentacao" / "evidencias" / "busca-turmas-2026-11-12")
    for source in selected:
        for path in files_under(source):
            destination = target / path.relative_to(WORK)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    delivery = WORK / "edutrack-documentacao" / "entrega"
    for path in files_under(delivery):
        destination = target / path.relative_to(delivery)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    for path in files_under(WORK / "edutrack-documentacao" / "evidencias" / "classroom-completo-2026-11-12"):
        destination = target / path.relative_to(WORK)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    findings = []
    manifest = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        if path.suffix not in {".png", ".webp", ".jpg", ".ico"}:
            content = data.decode("utf-8", errors="replace")
            if any(re.search(pattern, content) for pattern in PATTERNS):
                findings.append(str(path.relative_to(target)))
        manifest.append({"arquivo": path.relative_to(target).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if findings:
        raise RuntimeError("Possível segredo encontrado; ZIP não gerado. Revisar arquivos: " + ", ".join(findings))
    (target / "MANIFESTO.json").write_text(json.dumps({"arquivos": manifest, "verificacao": "Lista permitida, exclusão de segredos locais e busca de padrões de credenciais; não substitui revisão humana."}, ensure_ascii=False, indent=2), encoding="utf-8")
    archive = target.with_suffix(".zip")
    with ZipFile(archive, "w", ZIP_DEFLATED) as output:
        for path in target.rglob("*"):
            if path.is_file():
                output.write(path, target.name + "/" + path.relative_to(target).as_posix())
    print(json.dumps({"pasta": str(target), "zip": str(archive), "arquivos": len(manifest), "bytes_zip": archive.stat().st_size}, ensure_ascii=False))


if __name__ == "__main__":
    main()
