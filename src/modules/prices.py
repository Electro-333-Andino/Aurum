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

from src.utils.calculations import calculate_rsi, calculate_sma, to_float

# ---------------- SEÑALES ----------------


def _is_price_below_sma(price: float, sma: Optional[float]) -> bool:
    return sma is not None and price < sma


def _is_rsi_oversold(rsi: Optional[float]) -> bool:
    return rsi is not None and rsi < 40


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

        # elimina filas NaN
        close = close.dropna()

        if close.empty:
            return None

        last_price = close.iat[-1]

        current_price = to_float(last_price)

        if current_price is None:
            return None

        # -------- INDICADORES --------
        sma_50 = calculate_sma(close, 50)
        sma_200 = calculate_sma(close, 200)
        rsi = calculate_rsi(close)

        # Validación crítica (evita señales falsas)
        if any(v is None for v in [sma_50, sma_200, rsi]):
            return None

        # -------- SEÑALES --------
        below_sma50 = _is_price_below_sma(current_price, sma_50)
        below_sma200 = _is_price_below_sma(current_price, sma_200)
        rsi_oversold = _is_rsi_oversold(rsi)
        bullish_trend = _is_bullish_trend(sma_50, sma_200)

        # -------- SCORE DE COMPRA --------
        score = 0

        score += 1 if below_sma50 else 0
        score += 2 if below_sma200 else 0  # mayor peso
        score += 2 if rsi_oversold else 0
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
            "score": score,
            "signal": signal,
            "bullish_trend": bullish_trend,
        }

    except Exception as e:
        print(f"[ERROR prices] {ticker}: {e}")
        return None


def get_portfolio_prices(tickers: list[str]) -> list[dict]:
    """
    Obtiene precio actual y cambio % del día para cada ticker del portafolio
    """
    results = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")

            if hist.empty or "Close" not in hist:
                continue

            close = cast(pd.Series, hist["Close"])
            close = close.dropna()

            if len(close) < 2:
                continue

            current_price = to_float(close.iat[-1])
            prev_price = to_float(close.iat[-2])

            if current_price is None or prev_price is None:
                continue

            if prev_price == 0:
                continue

            # Cambio porcentual del día
            change_percent = round((current_price - prev_price) / prev_price * 100, 2)

            # Nombre de la empresa
            info = stock.info
            name = info.get("shortName", ticker)

            results.append(
                {
                    "ticker": ticker,
                    "name": name,
                    "price": round(current_price, 2),
                    "change_percent": change_percent,
                }
            )

        except Exception as e:
            print(f"[ERROR prices] {ticker}: {e}")
            continue

    return results
