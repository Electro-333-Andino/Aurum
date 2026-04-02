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
from src.modules.etf_analyzer import analyze_etf
from src.modules.news import get_company_news, get_macro_news
from src.modules.scanner import scan_ticker

# ---------------- CONFIGURACIÓN ----------------

# Portafolio actual
PORTFOLIO = ["VLO", "NVDA", "AMZN", "MSFT", "GOOGL", "META", "V", "BG", "O"]

# Candidatas a dividendos
CANDIDATES = [
    # Healthcare
    "JNJ",  # Johnson & Johnson
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


def run() -> None:
    """
    Ejecuta el briefing completo de Aurum
    """

    # 1. Noticias macro
    macro_news = get_macro_news()

    # 2. Noticias por empresa del portafolio
    company_news = []
    for ticker in PORTFOLIO:
        news = get_company_news(ticker)
        company_news.extend(news)

    # 3. Scanner de candidatas a dividendos
    scanner_results = []
    for ticker in CANDIDATES:
        result = scan_ticker(ticker)
        if result is not None:
            scanner_results.append(result)

    # 4. Análisis ETF
    etf_data = analyze_etf()

    # 5. Reporte en terminal
    report.display_scanner_results(scanner_results)

    if etf_data is not None:
        report.display_etf_analysis(etf_data)

    report.display_macro_news(macro_news)


# ---------------- ENTRADA ----------------

if __name__ == "__main__":
    run()
