"""
Copyright 2026 Anderson Andino

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-20.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Módulo responsable ÚNICAMENTE de noticias macroeconómicas desde Reuters.
import time
from datetime import datetime, timedelta, timezone

import feedparser
from deep_translator import GoogleTranslator

# --- INSTANCIA COMPARTIDA DEL TRADUCTOR ---
translator = GoogleTranslator(source="en", target="es")

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
        # Limitar el texto a 500 caracteres para evitar timeouts con deep-translator
        return translator.translate(text[:500])
    except Exception as e:
        print(f"[ERROR] Error al traducir texto: {e}")
        return text


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
    if not isinstance(title, str):
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

            title = str(entry.title) if entry.title else ""

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
            if not is_macro_relevant(title) or title in processed_titles:
                continue

            # Agregamos la noticia
            macro_news.append(
                {
                    "title": translate(title),
                    "original_title": title,
                    "published": relative_published_time,  # Usamos el tiempo relativo aquí
                    "source": "CNBC",
                }
            )
            processed_titles.add(title)

    except Exception as e:
        print(f"[ERROR] No se pudieron obtener noticias macro de CNBC: {e}")

    return macro_news
