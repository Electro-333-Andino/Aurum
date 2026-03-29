# calculations.py
from typing import Optional


def to_float(value: Optional[float]) -> Optional[float]:
    """Convierte un valor a float, devuelve None si no es posible"""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    if value is None:
        return False
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def debt_to_fcf_ratio(
    total_debt: Optional[float], free_cash_flow: Optional[float]
) -> Optional[float]:
    """
    Calcula la relación Deuda/Flujo de Caja Libre.
    Devuelve None si alguno de los valores es None o FCF <= 0
    """
    deb = to_float(total_debt)
    fcf = to_float(free_cash_flow)
    if deb is None or fcf is None:
        return None
