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
# Punto de entrada principal del programa.
# Coordina los módulos sin contener lógica de negocio.

from src.modules.news import get_macro_news
from src.modules.prices import PORTFOLIO, get_portfolio_prices
from src.modules.report import (
    display_candidate_signals,  # <- Descomentado
    display_finnhub_news,
    display_macro_news,
    display_portfolio,
    display_upcoming_earnings,
)
from src.modules.scanner import get_candidate_signals, get_full_portfolio_analysis


def main():
    """Función principal que ejecuta el reporte completo."""

    # --- PRECIOS ---
    print("Obteniendo precios del mercado...")
    portfolio_data: list[dict] = get_portfolio_prices()
    display_portfolio(portfolio_data)

    # --- NOTICIAS MACRO ---
    print("Obteniendo noticias macro del día...")
    macro_news = get_macro_news()
    display_macro_news(macro_news)

    # --- ANÁLISIS FINNHUB ---
    print("Obteniendo análisis por empresa...")
    analysis = get_full_portfolio_analysis(PORTFOLIO)
    display_finnhub_news(analysis, portfolio_data)
    display_upcoming_earnings(analysis["upcoming_earnings"])

    # --- SEÑALES DE CANDIDATAS ---
    candidate_signals = get_candidate_signals()
    display_candidate_signals(candidate_signals)  # <- Descomentado


if __name__ == "__main__":
    main()
