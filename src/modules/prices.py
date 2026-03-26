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
    "NVDA",  # Nvidia (Crecimiento)
    "GOOGL",  # Google (Crecimiento)
    "MSFT",  # Microsoft (Crecimiento)
    "AMZN",  # Amazon (Crecimiento)
    "META",  # Meta (Crecimiento)
    "COST",  # Costco (Crecimiento)
    "V",  # Visa (Crecimiento)
    "VLO",  # Valero Energy (Dividendos)
    "CSPX.L",  # iShares Core S&P 500 UCITS ETF (ETF)
]

# Lista de tickers Empresas candidatas para el scanner
CANDIDATE_TICKERS = [
    "O",  # Realty Income
    "JNJ",  # Johnson & Johnson
    "BG",  # Bunge Global
    "ABBV",  # AbbVie
    "PEP",  # PepsiCo
    "MDT",  # Medtronic
]


def get_stock_price(ticker: str) -> dict:
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
        stock = yf.Ticker(ticker)
        history = stock.history(period="2d")

        if history.empty:
            print(f"[WARNING] No se encontraron datos históricos para {ticker}")
            return {
                "ticke": ticker,
                "valid": False,
            }

        # Extraemos los datos que necesitamos
        # .get() es seguro: si el dato ne existe retorna el valor por defecto

        current_price = history["Close"].iloc[-1]  # Precio de cierre más reciente

        if len(history) > 1:
            previous_close = history["Close"].iloc[
                -2
            ]  # Precio de cierre del día anterior
        else:
            previous_close = current_price  # Si no hay datos anteriores, usamos el precio actual para evitar errores

        try:
            info = stock.info
        except Exception:
            info = {}

        company_name = info.get(
            "shortName", ticker
        )  # Nombre de la empresa o el ticker si no se encuentra

        # Calculamos el cambio porcentual
        if previous_close != 0:
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
            "valid": True,
        }

    except Exception as e:
        print(f"[ERROR] No se pudo obtener precio de {ticker}: {e}")
        return {
            "ticker": ticker,
            "valid": False,
        }


def get_portfolio_prices() -> list[dict]:
    """
    Obtiene los precios de todas las empresas del portafolio.

    Returns:
        Lista de diccionarios con datos de cada empresa.
    """
    results = []
    for ticker in PORTFOLIO:
        data = get_stock_price(ticker)
        if data.get("valid"):  # Solo agregamos si la consulta fue exitosa
            results.append(data)

    return results


def get_company_fundamentals(ticker: str) -> dict | None:
    """
    Obtiene datos fundamentales de una empresa desde Yahoo Finance.

    Args:
        ticker: Símbolo de la acción. Ejemplo: 'ABBV'

    Returns:
        Diccionario con dividend_yield, payout_ratio, free_cash_flow, total_debt, sector.
        Retorna None si ocurre un error o si los datos no están disponibles.
    """
    try:
        stock = yf.Ticker(ticker)

        try:
            info = stock.info
        except Exception:
            print(f"=[WARNING] info vacia para {ticker}")
            return None

        if not info:
            print(f"=[WARNING] info vacia para {ticker}")
            return None

        dividend_yield = info.get("dividendYield")
        payout_ratio = info.get("payoutRatio")
        free_cash_flow = info.get("freeCashflow")
        total_debt = info.get("totalDebt")
        sector = info.get("sector")

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")

        if current_price is None:
            current_price = 0.0

        return {
            "ticker": ticker,
            "dividend_yield": round(dividend_yield * 100, 2)
            if dividend_yield is not None
            else None,
            "payout_ratio": round(payout_ratio * 100, 2)
            if payout_ratio is not None
            else None,
            "free_cash_flow": free_cash_flow,
            "total_debt": total_debt,
            "sector": sector,
            "current_price": current_price,
        }

    except Exception as e:
        print(f"[ERROR] No se pudieron obtener datos fundamentales de {ticker}: {e}")
        return None
