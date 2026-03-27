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

# Módulo responsable de obtener datos avanzados desde Finnhub.
# Incluye noticias con sentimiento, earnings y eventos de mercado.
# También incluye el scanner para empresas candidatas.

import os
from datetime import datetime, timedelta

import finnhub
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

from src.modules.prices import CANDIDATE_TICKERS, get_company_fundamentals

from .utils import (
    debt_to_fcf_ratio,
    format_large_number,
    format_number,
    format_percentage,
    is_positive,
    normalize_percentage,
    safe_round,
)

load_dotenv()

api_key = os.getenv("FINNHUB_API_KEY")
if not api_key:
    raise ValueError("FINNHUB_API_KEY no está definida en el archivo .env")

client = finnhub.Client(api_key=api_key)
translator = GoogleTranslator(source="en", target="es")

ETF_EQUIVALENTS = {"CSPX.L": "SPY"}

ALLOWED_DIVIDEND_SECTORS = [
    "Real Estate",
    "Healthcare",
    "Consumer Defensive",
    "Energy",
    "Financial Services",
]


# ------------------ FUNCIONES AUXILIARES ------------------


def translate(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    try:
        return translator.translate(text[:500])
    except Exception as e:
        print(f"[ERROR] Error al traducir texto: {e}")
        return text


def get_company_news(ticker: str, max_news: int = 3) -> list[dict]:
    try:
        api_ticker = ETF_EQUIVALENTS.get(ticker, ticker)
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        news = client.company_news(api_ticker, _from=today, to=today)
        date_label = "Hoy"
        if not news:
            news = client.company_news(api_ticker, _from=yesterday, to=yesterday)
            date_label = "Ayer"
        if not news:
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            news = client.company_news(api_ticker, _from=three_days_ago, to=today)
            date_label = "Últimos 3 días"

        news_list = []
        for item in news[:max_news]:
            title = translate(item.get("headline", ""))
            summary = translate(item.get("summary", ""))
            sentences = summary.split(".")
            short_summary = ". ".join(sentences[:2]).strip()
            if short_summary and not short_summary.endswith("."):
                short_summary += "."
            news_list.append(
                {
                    "title": title,
                    "summary": short_summary,
                    "source": item.get("source", "Finnhub"),
                    "url": item.get("url", ""),
                    "date_label": date_label,
                }
            )

        return news_list

    except Exception as e:
        print(f"[ERROR] Finnhub no pudo obtener noticias de {ticker}: {e}")
        return []


def get_upcoming_earnings(tickers: list[str]) -> list[dict]:
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        in_30_days = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        calendar = client.earnings_calendar(
            _from=today, to=in_30_days, symbol="", international=False
        )
        earnings_list = calendar.get("earningsCalendar", [])

        upcoming = []
        for earning in earnings_list:
            if earning.get("symbol") in tickers:
                upcoming.append(
                    {
                        "ticker": earning.get("symbol"),
                        "date": earning.get("date"),
                        "eps_estimate": earning.get("epsEstimate"),
                    }
                )
        upcoming.sort(key=lambda x: x["date"])
        return upcoming

    except Exception as e:
        print(f"[ERROR] No se pudo obtener calendario de earnings: {e}")
        return []


# ------------------ FUNCIONES PRINCIPALES ------------------


def get_full_portfolio_analysis(tickers: list[str]) -> dict:
    analysis = {}
    for ticker in tickers:
        analysis[ticker] = {"news": get_company_news(ticker)}

    analysis["upcoming_earnings"] = get_upcoming_earnings(tickers)

    # Aseguramos que todos los valores sean strings o formateados
    for ticker, data in analysis.items():
        if ticker != "upcoming_earnings":
            for news_item in data["news"]:
                news_item["title"] = str(news_item["title"])
                news_item["summary"] = str(news_item["summary"])

    for earning in analysis["upcoming_earnings"]:
        earning["eps_estimate"] = format_number(earning.get("eps_estimate"))

    return analysis


def get_candidate_signals() -> list[dict]:
    signals = []

    for ticker in CANDIDATE_TICKERS:
        signal = "OBSERVAR"
        reasons = []
        positive_criteria_count = 0

        fundamentals = get_company_fundamentals(ticker)
        if not fundamentals:
            reasons.append("Datos fundamentales no disponibles.")
            signals.append({"ticker": ticker, "signal": signal, "reasons": reasons})
            continue

        # Dividendo > 2%
        dividend_yield = fundamentals.get("dividend_yield")

        if isinstance(dividend_yield, (int, float)):
            new_dividend_yield = normalize_percentage(dividend_yield)

            if new_dividend_yield is not None:
                if new_dividend_yield > 0.02:
                    positive_criteria_count += 1
                    reasons.append(
                        f"Dividendo ({format_percentage(new_dividend_yield)}) > 2% anual."
                    )
                else:
                    reasons.append(
                        f"Dividendo ({format_percentage(new_dividend_yield)}) <= 2% anual o no disponible."
                    )
        else:
            reasons.append("Dividendo (N/A) <= 2% anual o no disponible.")

        # Payout Ratio < 75%
        payout_ratio = fundamentals.get("payout_ratio")

        if isinstance(payout_ratio, (int, float)):
            payout_ratio = normalize_percentage(payout_ratio)

            if payout_ratio is not None:
                if payout_ratio < 0.75:
                    positive_criteria_count += 1
                    reasons.append(
                        f"Payout Ratio ({format_percentage(payout_ratio)}) < 75%."
                    )
                else:
                    reasons.append(
                        f"Payout Ratio ({format_percentage(payout_ratio)}) >= 75% o no disponible."
                    )
        else:
            reasons.append("Payout Ratio (N/A) >= 75% o no disponible.")

        # Flujo de Caja Libre positivo
        fcf = fundamentals.get("free_cash_flow")
        if is_positive(fcf):
            positive_criteria_count += 1
            reasons.append(
                f"Flujo de Caja Libre ({format_large_number(fcf)}) positivo."
            )
        else:
            reasons.append(
                f"Flujo de Caja Libre ({format_large_number(fcf)}) no positivo o no disponible."
            )

        # Deuda manejable
        total_debt = fundamentals.get("total_debt")
        ratio = debt_to_fcf_ratio(total_debt, fcf)
        if ratio is not None and ratio < 5:
            positive_criteria_count += 1
            reasons.append(f"Deuda manejable (ratio Deuda/FCF = {safe_round(ratio)})")
        else:
            reasons.append(
                f"Deuda alta o no evaluable (ratio Deuda/FCF = {safe_round(ratio) if ratio is not None else 'N/A'})"
            )

        # Sector permitido
        sector = fundamentals.get("sector")
        if sector in ALLOWED_DIVIDEND_SECTORS:
            positive_criteria_count += 1
            reasons.append(f"Sector ({sector}) dividendos.")
        else:
            reasons.append(f"Sector ({sector if sector else 'N/A'}) no permitido.")

        # Asignación de señal
        if positive_criteria_count >= 4:
            signal = "COMPRAR"
        elif positive_criteria_count >= 2:
            signal = "ESPERAR"
        else:
            signal = "OBSERVAR"

        signals.append({"ticker": ticker, "signal": signal, "reasons": reasons})

    return signals
