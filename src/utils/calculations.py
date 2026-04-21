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
from typing import Optional, Union, cast

import pandas as pd  # Add this import

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


# New functions for technical indicators


def calculate_sma(series: pd.Series, window: int) -> Optional[float]:
    if len(series) < window:
        return None

    result = cast(pd.Series, series.rolling(window=window).mean())

    last_value = result.iat[-1]

    if pd.isna(last_value):
        return None

    return float(last_value)


def calculate_rsi(series: pd.Series, period: int = 14) -> Optional[float]:
    if len(series) < period:
        return None

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = cast(pd.Series, gain.rolling(window=period).mean())
    avg_loss = cast(pd.Series, loss.rolling(window=period).mean())

    avg_gain_last = avg_gain.iat[-1]
    avg_loss_last = avg_loss.iat[-1]

    # Validación de NaN (CRÍTICO en datos reales)
    if pd.isna(avg_gain_last) or pd.isna(avg_loss_last):
        return None

    if avg_loss_last == 0:
        return 100.0

    rs = avg_gain_last / avg_loss_last
    rsi = 100 - (100 / (1 + rs))

    return float(rsi)


def calculate_drawdown_from_annual_high(series: pd.Series) -> Optional[float]:
    """
    Calcula el drawdown desde el máximo anual (52 semanas).
    Se asume que la serie contiene al menos 1 año de datos.
    """
    if series.empty:
        return None

    # Obtener el máximo de los últimos 52 semanas (aproximadamente 252 días de trading)
    # yfinance '1y' period gives 1 year of data, so max() on the whole series is fine.
    max_52w = series.max()
    current_price = series.iat[-1]

    if pd.isna(max_52w) or pd.isna(current_price):
        return None

    if max_52w == 0:  # Avoid division by zero
        return None

    return float((current_price - max_52w) / max_52w)
