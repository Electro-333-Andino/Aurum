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

# main.py
# Coordinador principal — sin lógica de negocio

from src.modules import report
from src.modules.etf_analyzer import analyze_etf_for_cli  # Updated import for CLI
from src.modules.news import get_company_news, get_macro_news
from src.modules.prices import get_portfolio_prices
from src.modules.scanner import scan_ticker

# ---------------- CONFIGURACIÓN ----------------

# Portafolio actual
PORTFOLIO = ["VLO", "NVDA", "AMZN", "MSFT", "GOOGL", "META", "JNJ", "O"]

# Candidatas a dividendos
CANDIDATES = [
    # Healthcare
    "ABBV",  # AbbVie
    "MDT",  # Medtronic
    # Consumer Defensive
    "KO",  # Coca-Cola
    "PG",  # Procter & Gamble
    "CL",  # Colgate-Palmolive
    # Tecnología
    "TXN",  # Texas Instruments
    # Infraestructura energética
    "ENB",  # Enbridge
    # Financial Services
    "JPM",  # JPMorgan Chase
    "BLK",  # BlackRock
]


# ---------------- MAIN ----------------


def run_terminal_app() -> None:  # Renamed from run()
    # 1. Precios del portafolio
    portfolio_data = get_portfolio_prices(PORTFOLIO)

    # 2. Noticias macro
    macro_news = get_macro_news()

    # 3. Noticias por empresa
    company_news = []
    for ticker in PORTFOLIO:
        news = get_company_news(ticker)
        company_news.extend(news)

    # 4. Scanner de candidatas
    scanner_results = []
    for ticker in CANDIDATES:
        result = scan_ticker(ticker)
        if result is not None:
            scanner_results.append(result)

    # 5. Análisis ETF
    # Usa la nueva función auxiliar para el CLI
    etf_data = analyze_etf_for_cli()  # Changed to analyze_etf_for_cli()

    # 6. Reporte en terminal
    report.display_portfolio(portfolio_data)
    report.display_scanner_results(scanner_results)
    report.display_etf_analysis(etf_data)
    report.display_macro_news(macro_news)


# ---------------- ENTRADA ----------------

if __name__ == "__main__":
    run_terminal_app()  # Changed to run_terminal_app()
