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
from typing import Dict, Optional

import yfinance as yf

from src.utils.calculations import (
    debt_to_fcf_ratio,
    normalize_percentage,
    to_float,
)

# ---------------- VALIDADORES INTERNOS ----------------


def _is_valid_dividend(dividend_yield: Optional[float]) -> bool:
    return dividend_yield is not None and 0 < dividend_yield <= 0.10


def _is_valid_payout(payout_ratio: Optional[float]) -> bool:
    return payout_ratio is not None and payout_ratio <= 1


def _is_valid_fcf(free_cash_flow: Optional[float]) -> bool:
    return free_cash_flow is not None and free_cash_flow > 0


def _is_valid_debt_ratio(debt_to_fcf: Optional[float]) -> bool:
    return debt_to_fcf is not None and debt_to_fcf < 5


# ---------------- HELPERS ----------------


def _safe_get(info: dict, key: str) -> Optional[float]:
    return to_float(info.get(key))


# ---------------- MAIN ----------------


def get_clean_fundamentals(ticker: str) -> Optional[Dict]:
    """
    Obtiene, limpia y valida datos fundamentales de una empresa
    """

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return None

        # -------- RAW --------
        dividend_yield = _safe_get(info, "dividendYield")
        payout_ratio = _safe_get(info, "payoutRatio")
        free_cash_flow = _safe_get(info, "freeCashflow")
        total_debt = _safe_get(info, "totalDebt")
        market_cap = _safe_get(info, "marketCap")

        # -------- NORMALIZACIÓN --------
        dividend_yield = normalize_percentage(dividend_yield)
        payout_ratio = normalize_percentage(payout_ratio)

        # -------- VALIDACIÓN BASE --------

        if not _is_valid_dividend(dividend_yield):
            return None

        if not _is_valid_payout(payout_ratio):
            return None

        if not _is_valid_fcf(free_cash_flow):
            return None

        # -------- MÉTRICAS DERIVADAS --------
        debt_fcf = debt_to_fcf_ratio(total_debt, free_cash_flow)

        if not _is_valid_debt_ratio(debt_fcf):
            return None

        # -------- OUTPUT FINAL --------
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
