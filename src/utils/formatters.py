# formatters.py
from typing import Optional


def safe_round(number: Optional[float], decimals: int = 2) -> Optional[float]:
    """Redondea un número de forma segura, devuelve None si el valor es None"""
    if number is None:
        return None
    return round(number, decimals)


def format_number(number, decimals=2):
    """
    Formatea un número con separador de miles y decimales.
    Si no es un número válido, retorna "N/A".
    """
    try:
        return f"{float(number):,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def format_percentage(number: Optional[float], decimals: int = 2) -> str:
    """Formatea un porcentaje, ejemplo: 0.032 -> 3.2%"""
    if number is None:
        return "N/A"

    rounded = safe_round(number * 100, decimals)
    if rounded is None:
        return "N/A"

    return f"{rounded}%"


def format_large_number(number: Optional[float]) -> str:
    """
    Formatea números grandes en millones (M) o billones (B)
    """
    if number is None:
        return "N/A"

    try:
        number = float(number)
    except (TypeError, ValueError):
        return "N/A"

    if abs(number) >= 1_000_000_000:
        return f"{format_number(number / 1_000_000_000)} B"
    elif abs(number) >= 1_000_000:
        return f"{format_number(number / 1_000_000)} M"
    else:
        return format_number(number)
