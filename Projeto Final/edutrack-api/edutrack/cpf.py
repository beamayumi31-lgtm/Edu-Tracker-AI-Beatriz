"""Validação matemática; não consulta situação cadastral nem titularidade."""

import re


def valid_cpf(value: str) -> bool:
    if not re.fullmatch(r"(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})", value.strip()):
        return False
    digits = re.sub(r"[^0-9]", "", value)
    if len(set(digits)) == 1:
        return False
    for size in (9, 10):
        total = sum(int(digits[index]) * (size + 1 - index) for index in range(size))
        calculated = (total * 10) % 11
        if (0 if calculated == 10 else calculated) != int(digits[size]):
            return False
    return True
