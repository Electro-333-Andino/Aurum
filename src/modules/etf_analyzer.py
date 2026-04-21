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

# etf_analyzer.py
# Modulo responsable de analizar ETFs y generar señales de compra.

from typing import Dict, Optional, Union, cast

import pandas as pd
import yfinance as yf

from src.utils.calculations import (
    calculate_drawdown_from_annual_high,
    calculate_rsi,
    calculate_sma,
    to_float,
)


class ETFAnalyzer:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.history_period = "1y"  # Data for 1 year to calculate 52-week high

    def _fetch_historical_data(self) -> Optional[pd.Series]:
        """Fetches historical 'Close' price data for the ETF."""
        try:
            stock = yf.Ticker(self.ticker)
            hist = stock.history(period=self.history_period)

            if hist.empty or "Close" not in hist:
                return None

            close_prices = cast(pd.Series, hist["Close"])
            close_prices = close_prices.dropna()

            if close_prices.empty:
                return None

            return close_prices
        except Exception as e:
            print(f"[ERROR ETFAnalyzer] Error fetching data for {self.ticker}: {e}")
            return None

    def _calculate_etf_indicators(
        self, close_prices: pd.Series
    ) -> Dict[str, Optional[float]]:
        """Calculates SMA 50, SMA 200, RSI, and Drawdown from annual high."""
        current_price = to_float(close_prices.iat[-1])

        if current_price is None:
            return {
                "current_price": None,
                "sma_50": None,
                "sma_200": None,
                "rsi": None,
                "drawdown": None,
            }

        sma_50 = calculate_sma(close_prices, 50)
        sma_200 = calculate_sma(close_prices, 200)
        rsi = calculate_rsi(close_prices)
        drawdown = calculate_drawdown_from_annual_high(close_prices)

        return {
            "current_price": current_price,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi": rsi,
            "drawdown": drawdown,
        }

    def _generate_score_and_signal(
        self,
        current_price: float,
        sma_50: Optional[float],
        sma_200: Optional[float],
        rsi: Optional[float],
        drawdown: Optional[float],
    ) -> Dict[str, Union[int, str]]:
        """Generates a score and a buy signal based on ETF criteria."""
        score = 0
        signal = "ESPERAR"  # Default signal

        # Validate all indicators are present before scoring
        if any(v is None for v in [sma_50, sma_200, rsi, drawdown]):
            return {"score": 0, "signal": signal}

        # Factores del score
        # Precio < SMA 200 → +3
        if current_price < cast(float, sma_200):
            score += 3
        # Precio < SMA 50 → +2
        if current_price < cast(float, sma_50):
            score += 2
        # RSI < 40 → +2
        if cast(float, rsi) < 40:
            score += 2
        # Drawdown > 10% → +3 (drawdown is negative, so drawdown < -0.10)
        if cast(float, drawdown) < -0.10:
            score += 3
        # Tendencia alcista (Precio > SMA 200) → +1
        if current_price > cast(float, sma_200):
            score += 1

        # Sistema de señales ETF
        if score >= 7:
            signal = "COMPRAR FUERTE"
        elif 4 <= score <= 6:
            signal = "COMPRAR"
        elif 2 <= score <= 3:
            signal = "DCA NORMAL"
        else:  # score < 2
            signal = "ESPERAR"

        return {"score": score, "signal": signal}

    def analyze_etf(self) -> Optional[Dict]:
        """
        Main method to analyze the ETF and return the buy signal.
        """
        close_prices = self._fetch_historical_data()
        if close_prices is None:
            return None

        indicators = self._calculate_etf_indicators(close_prices)

        current_price = indicators["current_price"]
        sma_50 = indicators["sma_50"]
        sma_200 = indicators["sma_200"]
        rsi = indicators["rsi"]
        drawdown = indicators["drawdown"]

        if current_price is None:  # Should be caught by previous check, but defensive
            return None

        score_and_signal = self._generate_score_and_signal(
            current_price, sma_50, sma_200, rsi, drawdown
        )

        return {
            "ticker": self.ticker,
            "current_price": current_price,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi": rsi,
            "drawdown": drawdown,
            "score": score_and_signal["score"],
            "signal": score_and_signal["signal"],
        }


# Función auxiliar para uso del CLI
def analyze_etf_for_cli(ticker: str = "CSPX.L") -> Optional[Dict]:
    """
    Función auxiliar para el CLI que analiza el ETF.
    """
    analyzer = ETFAnalyzer(ticker)
    return analyzer.analyze_etf()
