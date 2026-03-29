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

# calculations.py
from typing import Optional, Union

NumberLike = Union[int, float, str]


def to_float(value: Optional[NumberLike]) -> Optional[float]:
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
    total_deb = to_float(total_debt)
    free_casht_flow = to_float(free_cash_flow)

    if total_deb is None or free_casht_flow is None:
        return None

    if free_casht_flow <= 0:
        return None

    return total_deb / free_casht_flow
