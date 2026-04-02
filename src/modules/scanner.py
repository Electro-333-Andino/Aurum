"""
Copyright 2026 Anderson Andino

Licensed under the Apache License, Version 20 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# scanner.py
from typing import Dict, Optional

from src.modules.fundamentals import get_clean_fundamentals

# ---------------- SCORING ----------------


def _calculate_score(fundamentals: Dict) -> int:
    score = 0

    dividend_yield = fundamentals.get("dividendYield", 0)
    payout_ratio = fundamentals.get("payoutRatio", 0)
    free_cash_flow = fundamentals.get("freeCashFlow", 0)
    debt_to_fcf = fundamentals.get("debtToFreeCashFlow", 0)

    # Dividendo > 2%
    if dividend_yield is not None and dividend_yield > 0.02:
        score += 2

    # Payout saludable < 75%
    if payout_ratio is not None and payout_ratio < 0.75:
        score += 2

    # FCF positivo — el más importante
    if free_cash_flow is not None and free_cash_flow > 0:
        score += 3

    # Deuda vs FCF
    if debt_to_fcf is not None:
        if debt_to_fcf < 3:
            score += 3  # deuda baja → excelente
        elif debt_to_fcf <= 6:
            score += 1  # deuda media → aceptable

    return score

    # Dividendo > 2%
    if dividend_yield is not None and dividend_yield > 0.02:
        score += 2

    # Payout saludable < 75%
    if payout_ratio is not None and payout_ratio < 0.75:
        score += 2

    # FCF positivo — el más importante
    if free_cash_flow is not None and free_cash_flow > 0:
        score += 3

    # Deuda vs FCF
    if debt_to_fcf is not None:
        if debt_to_fcf < 3:
            score += 3  # deuda baja → excelente
        elif debt_to_fcf <= 6:
            score += 1  # deuda media → aceptable

    return score

    # ---------------- SEÑAL ----------------


def _get_signal(score: int) -> str:
    if score >= 7:
        return "COMPRAR"
    elif score >= 4:
        return "ESPERAR"
    else:
        return "DESCARTAR"


# ---------------- MAIN ----------------


def scan_ticker(ticker: str) -> Optional[Dict]:
    """
    Analiza una empresa y devuelve su score y señal de inversión
    """

    # 1. Obtener fundamentales ya limpios y validados
    fundamentals = get_clean_fundamentals(ticker)

    # 2. Si no hay datos válidos, descartamos
    if fundamentals is None:
        return None

    # 3. Calcular score
    score = _calculate_score(fundamentals)

    # 4. Obtener señal
    signal = _get_signal(score)

    # 5. Devolver todo junto
    return {
        "ticker": ticker,
        "score": score,
        "signal": signal,
        "dividend_yield": fundamentals.get("dividend_yield"),
        "payout_ratio": fundamentals.get("payout_ratio"),
        "free_cash_flow": fundamentals.get("free_cash_flow"),
        "debt_to_fcf": fundamentals.get("debt_to_fcf"),
    }
