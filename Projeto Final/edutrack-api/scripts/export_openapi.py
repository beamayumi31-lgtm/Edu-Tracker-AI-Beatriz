"""Gera o contrato HTTP sem conectar ao SQL Server nem carregar segredos locais."""

import json
from pathlib import Path

from sqlalchemy import create_engine

from edutrack.config import Settings
from edutrack.main import create_app


def main():
    engine = create_engine("sqlite://")
    app = create_app(Settings(_env_file=None, environment="test"), engine)
    target = Path(__file__).resolve().parents[1] / "docs" / "openapi.json"
    target.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    engine.dispose()
    print(f"Contrato gerado: {len(app.openapi()['paths'])} caminhos. Nenhum banco acessado.")


if __name__ == "__main__":
    main()
