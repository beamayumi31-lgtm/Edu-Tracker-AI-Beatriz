"""Executar: python scripts/calculate_progress.py --completed 3 --total 4."""

import argparse
import json
import sys
from pathlib import Path

# Permite execução direta sem instalar o pacote e reutiliza a regra da API.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from edutrack.progress import calculate_progress  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Calcula o progresso sem acessar banco ou rede.")
    parser.add_argument("--completed", required=True, type=int, help="Quantidade concluída")
    parser.add_argument("--total", required=True, type=int, help="Total, sem tarefas canceladas")
    args = parser.parse_args()
    try:
        result = calculate_progress(args.completed, args.total)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
