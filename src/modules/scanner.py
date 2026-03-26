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

# Importar la lista de candidatas y la función de datos fundamentales
from src.modules.prices import CANDIDATE_TICKERS, get_company_fundamentals

# Cargamos las variables del .env
load_dotenv()

# --- INSTANCIA DEL CLIENTE FINNHUB ---
# Se crea una sola vez y se reutiliza en todas las funciones
api_key = os.getenv("FINNHUB_API_KEY")

# Validamos que la key exista antes de continuar
if not api_key:
    raise ValueError("FINNHUB_API_KEY no está definida en el archivo .env")

client = finnhub.Client(api_key=api_key)

# Traductor compartido para eficiencia
translator = GoogleTranslator(source="en", target="es")

# Sectores permitidos para empresas de dividendo, según CONTEXT.md
ALLOWED_DIVIDEND_SECTORS = [
    "Healthcare",
    "Consumer Defensive",
    "Energy",
    "Financial Services",
]


def translate(text: str) -> str:
    """
    Traduce texto del inglés al español.
    Si falla retorna el texto original.

    Args:
        text: Texto en inglés.

    Returns:
        Texto traducido al español.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    try:
        # Limitamos el texto a 500 caracteres para evitar timeouts
        return translator.translate(text[:500])
    except Exception as e:
        print(f"[ERROR] Error al traducir texto: {e}")
        return text


def get_full_portfolio_analysis(tickers: list[str]) -> dict:
    """
    Obtiene noticias y earnings del portafolio desde Finnhub.

    Args:
        tickers: Lista de símbolos del portafolio.

    Returns:
        Diccionario con noticias por empresa y earnings próximos.
    """
    analysis = {}

    for ticker in tickers:
        # Solo noticias — sentimiento requiere plan de pago
        analysis[ticker] = {
            "news": get_company_news(ticker),
        }

    analysis["upcoming_earnings"] = get_upcoming_earnings(tickers)

    return analysis


def get_company_news(ticker: str, max_news: int = 3) -> list[dict]:
    """
    Obtiene noticias recientes de una empresa desde Finnhub.
    Si no hay noticias del día actual, muestra las del día anterior.
    Incluye resumen traducido al español.

    Args:
        ticker: Símbolo de la acción. Ejemplo: 'NVDA'
        max_news: Cantidad máxima de noticias. Por defecto 3.

    Returns:
        Lista de diccionarios con título, resumen, fuente y etiqueta de fecha.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Primero intentamos obtener noticias de hoy
        news = client.company_news(ticker, _from=today, to=today)
        date_label = "Hoy"

        # Si no hay noticias de hoy usamos las de ayer
        if not news:
            news = client.company_news(ticker, _from=yesterday, to=yesterday)
            date_label = "Ayer"

        # Si tampoco hay de ayer buscamos últimos 3 días
        if not news:
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            news = client.company_news(ticker, _from=three_days_ago, to=today)
            date_label = "Últimos 3 días"

        news_list = []

        for item in news[:max_news]:
            # Traducimos título y resumen
            title = translate(item.get("headline", ""))
            summary = translate(item.get("summary", ""))

            # Acortamos el resumen a 2 oraciones
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
                    "date_label": date_label,  # ← Indica si es de hoy, ayer o últimos 3 días
                }
            )

        return news_list

    except Exception as e:
        print(f"[ERROR] Finnhub no pudo obtener noticias de {ticker}: {e}")
        return []


def get_upcoming_earnings(tickers: list[str]) -> list[dict]:
    """
    Obtiene los próximos reportes de ganancias de las empresas del portafolio.
    Los earnings son eventos clave que mueven el precio de las acciones.

    Args:
        tickers: Lista de símbolos del portafolio.

    Returns:
        Lista de próximos earnings ordenados por fecha.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        in_30_days = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        # Pedimos calendario de earnings para los próximos 30 días
        calendar = client.earnings_calendar(
            _from=today, to=in_30_days, symbol="", international=False
        )

        earnings_list = calendar.get("earningsCalendar", [])

        # Filtramos solo las empresas de nuestro portafolio
        upcoming = []
        for earning in earnings_list:
            if earning.get("symbol") in tickers:
                upcoming.append(
                    {
                        "ticker": earning.get("symbol"),
                        "date": earning.get("date"),
                        "eps_estimate": earning.get("epsEstimate", "N/A"),
                    }
                )

        # Ordenamos por fecha más próxima
        upcoming.sort(key=lambda x: x["date"])

        return upcoming

    except Exception as e:
        print(f"[ERROR] No se pudo obtener calendario de earnings: {e}")
        return []


def get_candidate_signals() -> list[dict]:
    """
    Escanea las empresas candidatas y genera una señal (COMPRAR/ESPERAR/OBSERVAR)
    basada en los criterios del CONTEXT.md.

    Returns:
        Lista de diccionarios con el ticker, la señal y las razones.
    """
    signals = []
    print("\n[INFO] Escaneando empresas candidatas para señales...")

    for ticker in CANDIDATE_TICKERS:
        signal = "OBSERVAR"
        reasons = []
        positive_criteria_count = 0

        fundamentals = get_company_fundamentals(ticker)

        if not fundamentals:
            reasons.append("Datos fundamentales no disponibles.")
            signals.append({"ticker": ticker, "signal": signal, "reasons": reasons})
            continue

        # Criterio 1: Dividendo > 2% anual
        dividend_yield = fundamentals.get("dividend_yield")
        dividend_yield_percent = (
            round(dividend_yield * 100, 2) if dividend_yield is not None else None
        )
        if dividend_yield_percent is not None and dividend_yield_percent > 2.0:
            positive_criteria_count += 1
            reasons.append(f"Dividendo ({dividend_yield_percent}%) > 2% anual.")
        else:
            reasons.append(
                f"Dividendo ({dividend_yield_percent if dividend_yield_percent is not None else 'N/A'}%) <= 2% anual o no disponible."
            )

        # Criterio 2: Payout < 75%
        payout_ratio = fundamentals.get("payout_ratio")
        payout_ratio_percent = (
            round(payout_ratio * 100, 2) if payout_ratio is not None else None
        )
        if payout_ratio_percent is not None and payout_ratio_percent < 75.0:
            positive_criteria_count += 1
            reasons.append(f"Payout Ratio ({payout_ratio_percent}%) < 75%.")
        else:
            reasons.append(
                f"Payout Ratio ({payout_ratio_percent if payout_ratio_percent is not None else 'N/A'}%) >= 75% o no disponible."
            )

        # Criterio 3: Flujo de caja positivo
        if (
            fundamentals.get("free_cash_flow") is not None
            and fundamentals["free_cash_flow"] > 0
        ):
            positive_criteria_count += 1
            reasons.append(
                f"Flujo de Caja Libre ({fundamentals['free_cash_flow']:,}) positivo."
            )
        else:
            reasons.append(
                f"Flujo de Caja Libre ({fundamentals.get('free_cash_flow', 'N/A')}) no positivo o no disponible."
            )

        # Criterio 4: Deuda manejable (ratio Deuda Total / Flujo de Caja Libre < 5)
        total_debt = fundamentals.get("total_debt")
        fcf = fundamentals.get("free_cash_flow")
        is_debt_manageable = False

        if total_debt is None or total_debt == 0:
            is_debt_manageable = True
            reasons.append("Deuda total nula o cero (favorable).")
        elif fcf is not None and fcf > 0:  # Si hay FCF positivo, evaluamos el ratio
            if total_debt / fcf < 5:  # Umbral de 5 veces el FCF
                is_debt_manageable = True
                reasons.append(
                    f"Deuda Total ({total_debt:,}) es manejable frente a FCF ({fcf:,}) (ratio < 5)."
                )
            else:
                reasons.append(
                    f"Deuda Total ({total_debt:,}) es alta comparado con FCF ({fcf:,}) (ratio >= 5)."
                )
        else:  # Si FCF no es positivo o no está disponible, y hay deuda, no es manejable
            if total_debt is not None and total_debt > 0:
                reasons.append(
                    f"Flujo de Caja Libre ({fcf if fcf is not None else 'N/A'}) no es positivo o no disponible, y hay deuda ({total_debt:,})."
                )
            else:  # Este caso es si no hay FCF pero tampoco hay deuda, ya cubierto arriba.
                reasons.append("Evaluación de deuda no concluyente por falta de datos.")

        if is_debt_manageable:
            positive_criteria_count += 1

        # Criterio 5: Sector
        if fundamentals.get("sector") in ALLOWED_DIVIDEND_SECTORS:
            positive_criteria_count += 1
            reasons.append(f"Sector ({fundamentals['sector']}) permitido.")
        else:
            reasons.append(
                f"Sector ({fundamentals.get('sector', 'N/A')}) no está en la lista de sectores permitidos."
            )

        # Asignación de la señal
        if positive_criteria_count >= 4:
            signal = "COMPRAR"
        elif positive_criteria_count >= 2:
            signal = "ESPERAR"
        else:
            signal = "OBSERVAR"

        signals.append({"ticker": ticker, "signal": signal, "reasons": reasons})

    return signals
