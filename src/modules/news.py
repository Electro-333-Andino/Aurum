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

# news.py
# Módulo responsable ÚNICAMENTE de noticias macroeconómicas desde Reuters.
import os
from datetime import datetime, timedelta, timezone

import feedparser
import finnhub
from dotenv import load_dotenv

# Ruta de importación para TranslatorService
from src.utils.translator import translator_service

load_dotenv()

# --- FUENTES RSS MACRO DE CNBC (según CONTEXT.md) ---
# Se utiliza solo CNBC para noticias macro, ya que Reuters cambió sus URLs.
MACRO_FEED_URL = "https://www.cnbc.com/id/100003114/device/rss/rss.html"

# --- PALABRAS CLAVE MACRO ---
# Solo mostramos noticias que impactan decisiones de inversión
MACRO_KEYWORDS = [
    "fed",
    "federal reserve",
    "interest rate",
    "inflation",
    "cpi",
    "gdp",
    "unemployment",
    "powell",
    "fomc",
    "rate hike",
    "rate cut",
    "oil",
    "crude",
    "recession",
    "treasury",
    "yields",
    "market",
    "s&p",
    "nasdaq",
    "dow",
    "earnings",
    "economy",
    "tariff",
    "trade",
]


# Cliente Finnhub
def _get_finnhub_client():
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY no encontrada en .env")
    return finnhub.Client(api_key=api_key)


def get_last_business_day(start_date: datetime, days_back: int) -> datetime:
    """
    Calcula la fecha del último día hábil (lunes a viernes) hasta 'days_back' días.
    """
    current_date = start_date
    business_days_found = 0
    while business_days_found < days_back:
        current_date -= timedelta(days=1)
        # 0 = Lunes, 5 = Sábado, 6 = Domingo
        if current_date.weekday() < 5:  # Si no es sábado (5) ni domingo (6)
            business_days_found += 1
    return current_date


def parse_published_date(entry, now_ecuador: datetime) -> tuple[str, datetime]:
    """
    Convierte la fecha de publicación a formato legible y devuelve el objeto datetime.
    Usa UTC-5 (hora Ecuador) para el cálculo correcto.

    Args:
        entry: Entrada del feed RSS.
        now_ecuador: Objeto datetime del momento actual en zona horaria de Ecuador.

    Returns:
        Tupla de (String con tiempo relativo. Ejemplo: 'hace 2 horas', objeto datetime de la publicación).
    """
    try:
        # Convertimos la fecha del feed a datetime object en UTC
        if not hasattr(entry, "published_parsed") or not entry.published_parsed:
            return "Fecha desconocida", datetime.min.replace(tzinfo=timezone.utc)

        published_utc = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        # Convertimos a la zona horaria de Ecuador
        ecuador_tz = timezone(timedelta(hours=-5))
        published_ecuador = published_utc.astimezone(ecuador_tz)

        delta = now_ecuador - published_ecuador

        if delta.total_seconds() < 0:
            delta = timedelta(
                seconds=0
            )  # Evita "hace -X días" si la noticia es futura por error

        if delta.total_seconds() < 3600:  # Menos de una hora
            minutes = int(delta.total_seconds() / 60)
            return (
                f"hace {minutes} minuto{'s' if minutes != 1 else ''}",
                published_ecuador,
            )
        elif delta.total_seconds() < 86400:  # Menos de un día
            hours = int(delta.total_seconds() / 3600)
            return f"hace {hours} hora{'s' if hours != 1 else ''}", published_ecuador
        else:
            days = int(delta.total_seconds() / 86400)
            return f"hace {days} día{'s' if days != 1 else ''}", published_ecuador

    except Exception as e:
        print(f"[ERROR] Error al parsear fecha: {e}")
        return "fecha desconocida", datetime.min.replace(tzinfo=timezone.utc)


def is_macro_relevant(title: str | None) -> bool:
    """
    Verifica si una noticia es relevante para decisiones de inversión.

    Args:
        title: Título de la noticia en inglés. Puede ser None.

    Returns:
        True si contiene al menos una palabra clave macro.
    """
    # Si el título no es un string válido descartamos la noticia
    if not isinstance(title, str) or not title.strip():
        return False

    title_lower = title.lower()
    return any(keyword in title_lower for keyword in MACRO_KEYWORDS)


def get_macro_news(max_news: int = 8, max_business_days_back: int = 2) -> list[dict]:
    """
    Obtiene las noticias macroeconómicas más relevantes desde CNBC.
    Filtra noticias por palabras clave y un número máximo de días hábiles hacia atrás.

    Args:
        max_news: Cantidad máxima de noticias macro a retornar.
        max_business_days_back: Número máximo de días hábiles hacia atrás para buscar noticias.

    Returns:
        Lista de diccionarios con noticias macro traducidas.
    """
    macro_news = []
    processed_titles = set()

    try:
        feed = feedparser.parse(MACRO_FEED_URL)

        if not feed.entries:
            print("[WARNING] Feed vacio de CNBC.")
            return []

        ecuador_tz = timezone(timedelta(hours=-5))
        now_ecuador = datetime.now(tz=ecuador_tz)

        # Calculamos la fecha límite para las noticias (retrocediendo solo días hábiles)
        # Considera que `get_last_business_day` ya tiene la lógica para saltar fines de semana
        earliest_allowed_date = get_last_business_day(
            now_ecuador, max_business_days_back
        ).replace(hour=0, minute=0, second=0, microsecond=0)

        for entry in feed.entries:
            # Si ya tenemos suficientes noticias, salimos del loop
            if len(macro_news) >= max_news:
                break

            title = getattr(entry, "title", "") or ""

            normalized_title = title.strip().lower()

            # Parseamos la fecha de publicación y la convertimos a la zona horaria de Ecuador
            relative_published_time, published_datetime = parse_published_date(
                entry, now_ecuador
            )

            # Filtro por fecha: solo noticias dentro del rango de días hábiles permitidos
            # y que no hayan sido publicadas en un fin de semana (sábado=5, domingo=6)
            if (
                published_datetime < earliest_allowed_date
                or published_datetime.weekday() >= 5
            ):
                continue

            # Filtro por relevancia y duplicados
            if not is_macro_relevant(title) or normalized_title in processed_titles:
                continue

            # Agregamos la noticia
            macro_news.append(
                {
                    "title": translator_service.translate(title),
                    "original_title": title,
                    "published": relative_published_time,  # Usamos el tiempo relativo aquí
                    "source": getattr(entry, "source", {}).get("title", "CNBC"),
                }
            )
            processed_titles.add(normalized_title)

    except Exception as e:
        print(f"[ERROR] No se pudieron obtener noticias macro de CNBC: {e}")

    return macro_news


def get_company_news(ticker: str, max_news: int = 5) -> list[dict]:
    """
    Obtiene noticias recientes de una empresa específica via Finnhub.

    Args:
        ticker: Símbolo de la empresa. Ejemplo: "NVDA"
        max_news: Cantidad máxima de noticias a retornar.

    Returns:
        Lista de diccionarios con noticias traducidas.
    """
    try:
        client = _get_finnhub_client()

        # Rango de fechas — últimos 7 días
        today = datetime.now(tz=timezone.utc)
        week_ago = today - timedelta(days=7)

        date_from = week_ago.strftime("%Y-%m-%d")
        date_to = today.strftime("%Y-%m-%d")

        # Llamada a la API
        raw_news = client.company_news(ticker, _from=date_from, to=date_to)

        if not raw_news:
            return []

        news = []

        for item in raw_news[:max_news]:
            headline = item.get("headline", "")

            if not headline:
                continue

            # Traducir titular
            translated = translator_service.translate(headline)

            news.append(
                {
                    "ticker": ticker,
                    "title": translated,
                    "original_title": headline,
                    "source": item.get("source", ""),
                    "url": item.get("url", ""),
                }
            )

        return news

    except Exception as e:
        print(f"[ERROR news] company {ticker}: {e}")
        return []
