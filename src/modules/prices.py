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

# Modulos responsables de obtener precios reales desde Yahoo Finance

import yfinance as yf

# Lista de tickers Empresas actuales

PORTFOLIO = [
    "NVDA",  # Nvidia
    "GOOGL",  # Google
    "COST",  # Costco
    "AMZN",  # Amazon
    "MSFT",  # Microsoft
    "META",  # Meta
    "V",  # Visa
    "VLO",  # Valero Energy
    "BG",  # Bunge Global
    "O",  # Realty Income
    "JNJ",  # Johnson & Johnson
    "BIP",  # Brookfield Infraestructure Corp
]


def get_stop_price(ticker: str) -> dict | None:
    """
    Obtiene el precio actual y variación diaria de una acción.

    Args:
        ticker: Símbolo de la acción. Ejemplo: 'NVDA'

    Returns:
        Diccionario con precio, cambio porcentual y nombre de la empresa.
        Retorna None si ocurre un error.
    """
    try:
        # Descargamos la informacion del ticker desde Yahoo Finance
        stop = yf.Ticker(ticker)
        info = stop.info

        # Extraemos los datos que necesitamos
        # .get() es seguro: si el dato ne existe retorna el valor por defecto

        current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        previous_close = info.get("previousClose", 0)
        company_name = info.get("shortName", ticker)

        # Calculamos el cambio porcentual
        if previous_close and previous_close != 0:
            change_percent = ((current_price - previous_close) / previous_close) * 100

        # si no -> ponemos 0% para no romper el programa
        else:
            change_percent = 0.0

        return {
            "ticker": ticker,
            "name": company_name,
            "price": round(current_price, 2),
            "change_percent": round(change_percent, 2),
            "previous_close": round(previous_close, 2),
        }

    except Exception as e:
        print(f"[ERROR] No se pudo obtener precio de {ticker}: {e}")
        return None


def get_portfolio_prices() -> list[dict]:
    """
    Obtiene los precios de todas las empresas del portafolio.

    Returns:
        Lista de diccionarios con datos de cada empresa.
    """
    results = []
    for ticker in PORTFOLIO:
        data = get_stop_price(ticker)
        if data:  # Solo agregamos si la consulta fue exitosa
            results.append(data)

    return results
