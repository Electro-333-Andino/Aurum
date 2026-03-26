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

# Módulo responsable ÚNICAMENTE de mostrar datos en terminal.
# Usa la librería 'rich' para formato profesional con colores y tablas.

from datetime import datetime

from rich import box
from rich.console import Console
from rich.table import Table

# Console es el objeto principal de rich para imprimir en terminal
console = Console()


def display_portfolio(portfolio_data: list[dict]) -> None:
    """
    Muestra la tabla del portafolio en terminal con colores.

    Args:
        portfolio_data: Lista de diccionarios retornada por get_portfolio_prices()
    """
    # Encabezado con fecha y hora actual
    now = datetime.now().strftime("%A %d %B %Y - %H:%M")
    console.print("\n[bold cyan]INVESTMENT MORNING BRIEF — AURUM[/bold cyan]")
    console.print(f"[dim]{now}[/dim]\n")

    # Creamos la tabla con rich
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on dark_blue",
    )

    # Definimos las columnas
    table.add_column("Ticker", style="bold yellow", width=8)
    table.add_column("Empresa", style="white", width=35)
    table.add_column("Precio", style="bold white", width=12, justify="right")
    table.add_column("Cambio %", width=12, justify="right")
    table.add_column("Estado", width=12, justify="center")

    # Llenamos la tabla con los datos
    for stock in portfolio_data:
        change = stock["change_percent"]

        # Color según si sube o baja
        if change > 0:
            change_str = f"[green]+{change}%[/green]"
            status = "[green]▲ Subiendo[/green]"
        elif change < 0:
            change_str = f"[red]{change}%[/red]"
            status = "[red]▼ Bajando[/red]"
        else:
            change_str = f"[dim]{change}%[/dim]"
            status = "[dim]── Estable[/dim]"

        table.add_row(
            stock["ticker"],
            stock["name"],
            f"${stock['price']}",
            change_str,
            status,
        )

    console.print(table)


def display_macro_news(macro_news: list[dict]) -> None:
    """
    Muestra las noticias macroeconómicas del día en terminal.
    Estas noticias afectan al mercado completo y todas tus inversiones.

    Args:
        macro_news: Lista de noticias macro retornada por get_macro_news()
    """
    console.print("\n[bold cyan]RESUMEN MACRO DEL DIA[/bold cyan]")
    console.print("[dim]Fed, economia, petroleo y mercados globales[/dim]\n")

    if not macro_news:
        console.print("[dim]  Sin noticias macro disponibles[/dim]\n")
        return

    for news in macro_news:
        console.print(f"  [white]• {news['title']}[/white]", soft_wrap=True)
        console.print(f"    [dim]{news['source']} · {news['published']}[/dim]\n")

    console.print("[dim]─────────────────────────────────────────[/dim]")


def display_finnhub_news(analysis: dict, portfolio_data: list[dict]) -> None:
    """
    Muestra noticias por empresa desde Finnhub.

    Args:
        analysis: Diccionario retornado por get_full_portfolio_analysis()
        portfolio_data: Lista con datos del portafolio para obtener nombres.
    """
    # Mapa ticker → nombre completo
    names = {stock["ticker"]: stock["name"] for stock in portfolio_data}

    console.print("\n[bold cyan]NOTICIAS POR EMPRESA[/bold cyan]\n")

    for ticker, data in analysis.items():
        # Saltamos la clave de earnings que no es un ticker
        if ticker == "upcoming_earnings":
            continue

        name = names.get(ticker, ticker)
        news_list = data["news"]

        # Encabezado con ticker y nombre
        console.print(f"[bold yellow]{ticker}[/bold yellow] [dim]— {name}[/dim]")

        if not news_list:
            console.print("  [dim]Sin noticias disponibles[/dim]\n")
        else:
            for news in news_list:
                console.print(f"  [white]• {news['title']}[/white]", soft_wrap=True)
                if news.get("summary"):
                    console.print(f"    [dim]{news['summary']}[/dim]", soft_wrap=True)
                console.print(
                    f"    [dim]{news['source']} · {news['date_label']}[/dim]\n"
                )

        console.print("[dim]─────────────────────────────────────────[/dim]")


def display_upcoming_earnings(upcoming: list[dict]) -> None:
    """
    Muestra los próximos reportes de ganancias del portafolio.
    Los earnings son eventos clave — el precio puede moverse mucho ese día.

    Args:
        upcoming: Lista de earnings retornada por get_upcoming_earnings()
    """
    console.print("\n[bold cyan]PROXIMOS EARNINGS DE TU PORTAFOLIO[/bold cyan]\n")

    if not upcoming:
        console.print("[dim]  Sin earnings proximos en los siguientes 30 dias[/dim]\n")
        return

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold white",
    )

    table.add_column("Empresa", style="bold yellow", width=10)
    table.add_column("Fecha", style="white", width=15)
    table.add_column("EPS Estimado", style="cyan", width=15, justify="right")

    for earning in upcoming:
        table.add_row(
            earning["ticker"],
            earning["date"],
            str(earning["eps_estimate"]),
        )

    console.print(table)


def display_candidate_signals(signals: list[dict]) -> None:
    """
    Muestra las señales de las empresas candidatas en terminal.

    Args:
        signals: Lista de diccionarios con el ticker, la señal y las razones.
    """
    console.print("\n[bold cyan]SEÑALES PARA EMPRESAS CANDIDATAS[/bold cyan]")
    console.print("[dim]Basado en criterios de dividendos y fundamentales[/dim]\n")

    if not signals:
        console.print("[dim]  Sin señales de candidatas disponibles[/dim]\n")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on dark_magenta",
    )

    table.add_column("Ticker", style="bold yellow", width=10)
    table.add_column("Señal", width=12, justify="center")
    table.add_column("Razones", style="white", min_width=50)

    for candidate in signals:
        ticker = candidate["ticker"]
        signal = candidate["signal"]
        reasons = "\n".join(
            candidate["reasons"]
        )  # Unimos las razones con saltos de línea

        signal_style = ""
        if signal == "COMPRAR":
            signal_style = "[bold green]"
        elif signal == "ESPERAR":
            signal_style = "[bold yellow]"
        elif signal == "OBSERVAR":
            signal_style = "[bold red]"

        table.add_row(
            ticker,
            f"{signal_style}{signal}[/]",
            reasons,
        )

    console.print(table)
