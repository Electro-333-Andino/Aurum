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
# Módulo responsable de obtener datos avanzados desde Finnhub.
# Incluye noticias con sentimiento, earnings y eventos de mercado
import os

import finnhub
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Cargamos las variables del .env
load_dotenv()

# --- INSTANCIA DEL CLIENTE FINNHUB ---
# Se crea una sola vez y se reutiliza en todas las funciones
api_key = os.getenv("FINNHUB_API_KEY")

# Validamos que la key exista antes de continuar
if not api_key:
    raise ValueError("FINNHUB_API_KEY no está definida en el archivo .env")

client = finnhub.Client(api_key=api_key)

# Traductor compartido
translator = GoogleTranslator(source="en", target="es")


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
    except Exception:
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
        from datetime import datetime, timedelta

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
        from datetime import datetime, timedelta

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