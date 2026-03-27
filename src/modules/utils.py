# utils.py
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


def format_percentage(number: Optional[float], decimals: int = 2) -> str:
    """Formatea un porcentaje, ejemplo: 0.032 -> 3.2%"""
    if number is None:
        return "N/A"
    return f"{safe_round(number * 100, decimals)}%"


def normalize_percentage(value: Optional[float]) -> Optional[float]:
    """
    Normaliza porcentajes:
    - 2.17  → 0.0217
    - 0.0217 → 0.0217
    - "2.17" → 0.0217
    """
    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if value > 1:
        return value / 100

    return value


def is_positive(value: Optional[float]) -> bool:
    """Chequea si un valor financiero es positivo"""
    return value is not None and value > 0


def debt_to_fcf_ratio(
    total_debt: Optional[float], free_cash_flow: Optional[float]
) -> Optional[float]:
    """
    Calcula la relación Deuda/Flujo de Caja Libre.
    Devuelve None si alguno de los valores es None o FCF <= 0
    """
    if total_debt is None or free_cash_flow is None or free_cash_flow <= 0:
        return None
    return total_debt / free_cash_flow
