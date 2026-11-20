"""Regra única de progresso; não acessa banco, rede ou configuração privada."""


def calculate_progress(completed: int, total: int) -> dict[str, int]:
    """Percentual inteiro, com metade para cima, compatível com o frontend."""
    if type(completed) is not int or type(total) is not int:
        raise ValueError("As quantidades devem ser números inteiros.")
    if completed < 0 or total < 0 or completed > total:
        raise ValueError("Use 0 <= concluídas <= total.")
    percentage = (200 * completed + total) // (2 * total) if total else 0
    return {"percentage": percentage}
