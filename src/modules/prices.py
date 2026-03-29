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

# prices.py
# Modulo responsables de obtener precios reales desde Yahoo Finance
from typing import Dict, Optional, cast

import pandas as pd
import yfinance as yf

from src.utils.calculations import to_float

# ---------------- INDICADORES ----------------


def _calculate_sma(series: pd.Series, window: int) -> Optional[float]:
    if len(series) < window:
        return None

    result = cast(pd.Series, series.rolling(window=window).mean())

    last_value = result.iat[-1]

    if pd.isna(last_value):
        return None

    return float(last_value)


def _calculate_rsi(series: pd.Series, period: int = 14) -> Optional[float]:
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


def _calculate_drawdown(series: pd.Series, window: int = 90) -> Optional[float]:
    if len(series) < window:
        return None

    recent = cast(pd.Series, series.iloc[-window:])

    max_price = recent.max()
    current_price = recent.iat[-1]

    # Validaciones robustas
    if pd.isna(max_price) or pd.isna(current_price):
        return None

    if max_price == 0:
        return None

    return float((current_price - max_price) / max_price)


# ---------------- SEÑALES ----------------


def _is_price_below_sma(price: float, sma: Optional[float]) -> bool:
    return sma is not None and price < sma


def _is_rsi_oversold(rsi: Optional[float]) -> bool:
    return rsi is not None and rsi < 40


def _is_in_drawdown(drawdown: Optional[float]) -> bool:
    return drawdown is not None and drawdown < -0.10


def _is_bullish_trend(sma_50: Optional[float], sma_200: Optional[float]) -> bool:
    return sma_50 is not None and sma_200 is not None and sma_50 > sma_200


# ---------------- MAIN ----------------


def get_price_analysis(ticker: str) -> Optional[Dict]:
    """
    Obtiene datos técnicos y detecta oportunidad de compra
    """

    try:
        stock = yf.Ticker(ticker)

        # 12 meses de datos diarios
        hist = stock.history(period="1y")

        if hist.empty or "Close" not in hist:
            return None

        close = cast(pd.Series, hist["Close"])

        # 🔹 Validación extra (NaN al final es común en yfinance)
        last_price = close.iat[-1]

        if pd.isna(last_price):
            return None

        current_price = to_float(last_price)

        if current_price is None:
            return None

        # -------- INDICADORES --------
        sma_50 = _calculate_sma(close, 50)
        sma_200 = _calculate_sma(close, 200)
        rsi = _calculate_rsi(close)
        drawdown = _calculate_drawdown(close)

        # Validación crítica (evita señales falsas)
        if any(v is None for v in [sma_50, sma_200, rsi, drawdown]):
            return None

        # -------- SEÑALES --------
        below_sma50 = _is_price_below_sma(current_price, sma_50)
        below_sma200 = _is_price_below_sma(current_price, sma_200)
        rsi_oversold = _is_rsi_oversold(rsi)
        in_drawdown = _is_in_drawdown(drawdown)
        bullish_trend = _is_bullish_trend(sma_50, sma_200)

        # -------- SCORE DE COMPRA --------
        score = 0

        score += 1 if below_sma50 else 0
        score += 2 if below_sma200 else 0  # mayor peso
        score += 2 if rsi_oversold else 0
        score += 1 if in_drawdown else 0
        score += 1 if bullish_trend else 0

        # -------- CLASIFICACIÓN --------
        if score >= 5:
            signal = "STRONG_BUY"
        elif score >= 3:
            signal = "BUY"
        else:
            signal = "HOLD"

        # -------- OUTPUT --------
        return {
            "ticker": ticker,
            "current_price": current_price,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi": rsi,
            "drawdown": drawdown,
            "score": score,
            "signal": signal,
            "bullish_trend": bullish_trend,
        }

    except Exception as e:
        print(f"[ERROR prices] {ticker}: {e}")
        return None
