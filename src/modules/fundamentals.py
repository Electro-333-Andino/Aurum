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

# fundamentals.py
from typing import Dict, Optional, Union

import yfinance as yf

from src.utils.calculations import debt_to_fcf_ratio, normalize_percentage, to_float


def _safe_get(info: dict, key: str) -> Optional[float]:
    """Obtiene un valor numérico limpio desde yfinance"""
    return to_float(info.get(key))


def get_clean_fundamentals(ticker: str) -> Optional[Dict]:
    """
    Obtiene y limpia datos fundamentales de una empresa.
    """

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return None

        # ---------------- RAW ----------------
        dividend_yield = _safe_get(info, "dividendYield")
        payout_ratio = _safe_get(info, "payoutRatio")
        free_cash_flow = _safe_get(info, "freeCashflow")
        total_debt = _safe_get(info, "totalDebt")
        market_cap = _safe_get(info, "marketCap")

        # ---------------- NORMALIZACIÓN ----------------
        dividend_yield = normalize_percentage(dividend_yield)
        payout_ratio = normalize_percentage(payout_ratio)

        # ---------------- VALIDACIONES ----------------

        # Dividend yield válido
        if dividend_yield is None or dividend_yield <= 0:
            return None

        # Evitar yields absurdos (trampas)
        if dividend_yield > 0.10:
            return None

        # Payout ratio válido
        if payout_ratio is None or payout_ratio > 1:
            return None

        # Free cash flow debe ser positivo
        if free_cash_flow is None or free_cash_flow <= 0:
            return None

        # ---------------- MÉTRICAS DERIVADAS ----------------
        debt_fcf = debt_to_fcf_ratio(total_debt, free_cash_flow)

        # Si no podemos calcular deuda → descartamos
        if debt_fcf is None:
            return None

        # ---------------- OUTPUT LIMPIO ----------------
        return {
            "ticker": ticker,
            "dividend_yield": dividend_yield,
            "payout_ratio": payout_ratio,
            "free_cash_flow": free_cash_flow,
            "total_debt": total_debt,
            "debt_to_fcf": debt_fcf,
            "market_cap": market_cap,
        }

    except Exception as e:
        print(f"[ERROR fundamentals] {ticker}: {e}")
        return None
