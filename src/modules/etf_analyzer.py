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


# etf_analyzer.py
# Módulo responsable de generar señales DCA para CSPX.L

from typing import Dict, Optional

from src.modules.prices import get_price_analysis

# ETF principal
CSPX_TICKER = "CSPX.L"

# ---------------- SCORING ----------------


def _calculate_etf_score(analysis: Dict) -> int:
    score = 0

    current_price = analysis.get("current_price")
    sma_50 = analysis.get("sma_50")
    sma_200 = analysis.get("sma_200")
    rsi = analysis.get("rsi")
    drawdown = analysis.get("drawdown")
    bullish_trend = analysis.get("bullish_trend")

    # Precio por debajo de SMA 200 — zona de acumulación fuerte
    if current_price is not None and sma_200 is not None:
        if current_price < sma_200:
            score += 3

    # Precio por debajo de SMA 50 — corrección / pullback
    if current_price is not None and sma_50 is not None:
        if current_price < sma_50:
            score += 2

    # RSI en zona de sobreventa
    if rsi is not None and rsi < 40:
        score += 2

    # Drawdown mayor al 10%
    if drawdown is not None and drawdown < -0.10:
        score += 3

    # Tendencia alcista — SMA50 > SMA200
    if bullish_trend:
        score += 1

    return score


# ---------------- SEÑAL ----------------


def _get_etf_signal(score: int) -> str:
    if score >= 7:
        return "COMPRAR FUERTE"
    elif score >= 4:
        return "COMPRAR"
    elif score >= 2:
        return "DCA NORMAL"
    else:
        return "ESPERAR"


# ---------------- MAIN ----------------


def analyze_etf() -> Optional[Dict]:
    """
    Analiza CSPX.L y devuelve señal de compra para estrategia DCA
    """

    # 1. Obtener análisis técnico desde prices.py
    analysis = get_price_analysis(CSPX_TICKER)

    # 2. Si no hay datos válidos, salimos
    if analysis is None:
        print(f"[ERROR] No se pudieron obtener datos de {CSPX_TICKER}")
        return None

    # 3. Calcular score
    score = _calculate_etf_score(analysis)

    # 4. Obtener señal
    signal = _get_etf_signal(score)

    # 5. Devolver resultado completo
    return {
        "ticker": CSPX_TICKER,
        "current_price": analysis.get("current_price"),
        "sma_50": analysis.get("sma_50"),
        "sma_200": analysis.get("sma_200"),
        "rsi": analysis.get("rsi"),
        "drawdown": analysis.get("drawdown"),
        "bullish_trend": analysis.get("bullish_trend"),
        "score": score,
        "signal": signal,
    }
