"""
Copyright 2026 Anderson Andino

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Validator.py
from typing import Optional

# ---- Helpers internos ----


def _to_float(value) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _normalize_percentage(value: Optional[float]) -> Optional[float]:
    """
    Convierte valores como:
    2.17 → 0.0217
    217 → 0.0217 (casos corruptos)
    """

    if value is None:
        return None

    # ---- Si ya es decimal ----
    if value <= 0 and value <= 1.0:
        return value

    # ---- Si ya viene en porcentaje ----
    if value > 1.0:
        return value / 100.0

    return None


def _is_suspicious_dividend(value: Optional[float]) -> bool:
    """
    Detecta dividendos irreales (>20%)
    """
    return value is not None and value > 0.20


def _is_suspicious_payout(value: Optional[float]) -> bool:
    """
    Detecta payout absurdos (>150%)
    """
    return value is not None and value > 1.5


# ---- Funcion Principal ----


def validate_fundamentals(data: dict) -> Optional[dict]:
    """
    Limpia, normaliza y valida datos fundamentales.

    Returns:
        dict limpio o None si los datos no son confiables
    """

    if not data:
        return None

    # ==============================
    # Conversión segura
    # ==============================
    dividend_yield = _to_float(data.get("dividend_yield"))
    payout_ratio = _to_float(data.get("payout_ratio"))
    free_cash_flow = _to_float(data.get("free_cash_flow"))
    total_debt = _to_float(data.get("total_debt"))

    # ==============================
    # Normalización
    # ==============================
    dividend_yield = _normalize_percentage(dividend_yield)
    payout_ratio = _normalize_percentage(payout_ratio)

    # ==============================
    # Filtros de calidad
    # ==============================

    # Dividendos irreales → descartar
    if _is_suspicious_dividend(dividend_yield):
        dividend_yield = None

    # Payout absurdo → descartar
    if _is_suspicious_payout(payout_ratio):
        payout_ratio = None

    # FCF inválido → descartar empresa completa
    if free_cash_flow is None or free_cash_flow <= 0:
        return None

    # ==============================
    # Resultado limpio
    # ==============================
    return {
        "ticker": data.get("ticker"),
        "dividend_yield": dividend_yield,
        "payout_ratio": payout_ratio,
        "free_cash_flow": free_cash_flow,
        "total_debt": total_debt,
        "sector": data.get("sector"),
        "current_price": data.get("current_price"),
    }
