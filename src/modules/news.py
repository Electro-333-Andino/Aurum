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
# Módulo responsable ÚNICAMENTE de noticias macroeconómicas desde Reuters.
import time
from datetime import datetime, timezone

import feedparser
from deep_translator import GoogleTranslator

# --- INSTANCIA COMPARTIDA DEL TRADUCTOR ---
translator = GoogleTranslator(source="en", target="es")

# --- FUENTES RSS MACRO DE REUTERS ---
MACRO_FEEDS = {
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
    "Investing.com": "https://www.investing.com/rss/news.rss",
}

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


def translate(text: str | None) -> str:
    """
    Traduce texto del inglés al español.
    Si falla o el texto no es válido retorna el texto original.

    Args:
        text: Texto en inglés. Puede ser None.

    Returns:
        Texto traducido al español.
    """
    # Si no es un string válido retornamos string vacío
    if not isinstance(text, str) or not text.strip():
        return ""

    try:
        return translator.translate(text)
    except Exception:
        return text


def parse_published_date(entry) -> str:
    """
    Convierte la fecha de publicación a formato legible.

    Args:
        entry: Entrada del feed RSS.

    Returns:
        String con tiempo relativo. Ejemplo: 'hace 2 horas'
    """
    try:
        published = datetime.fromtimestamp(
            time.mktime(entry.published_parsed), tz=timezone.utc
        )
        now = datetime.now(tz=timezone.utc)
        seconds = (now - published).total_seconds()

        # Si el tiempo es negativo o cero mostramos 'hace moments'
        if seconds <= 0:
            return "hace momentos"
        elif seconds < 3600:
            return f"hace {int(seconds / 60)} minutos"
        elif seconds < 86400:
            return f"hace {int(seconds / 3600)} horas"
        else:
            return f"hace {int(seconds / 86400)} días"

    except Exception:
        return "fecha desconocida"


def is_macro_relevant(title: str | None) -> bool:
    """
    Verifica si una noticia es relevante para decisiones de inversión.

    Args:
        title: Título de la noticia en inglés. Puede ser None.

    Returns:
        True si contiene al menos una palabra clave macro.
    """
    # Si el título no es un string válido descartamos la noticia
    if not isinstance(title, str):
        return False

    title_lower = title.lower()
    return any(keyword in title_lower for keyword in MACRO_KEYWORDS)


def get_macro_news(max_news: int = 8) -> list[dict]:
    """
    Obtiene las noticias macroeconómicas más relevantes del día desde Reuters.

    Args:
        max_news: Cantidad máxima de noticias macro a retornar.

    Returns:
        Lista de diccionarios con noticias macro traducidas.
    """
    macro_news = []

    for source_name, url in MACRO_FEEDS.items():
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                # Si ya tenemos suficientes noticias salimos del loop
                if len(macro_news) >= max_news:
                    break

                title = str(entry.title) if entry.title else ""

                if not is_macro_relevant(title):
                    continue

                existing = [n["original_title"] for n in macro_news]
                if entry.title in existing:
                    continue

                macro_news.append(
                    {
                        "title": translate(title),
                        "original_title": title,
                        "published": parse_published_date(entry),
                        "source": "CNBC",
                    }
                )

        except Exception as e:
            print(f"[ERROR] Feed macro {source_name}: {e}")

    return macro_news