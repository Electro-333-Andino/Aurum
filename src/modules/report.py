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


# report.py
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

    if not signals:
        console.print("[dim]  Sin señales de candidatas disponibles[/dim]\n")
        return

    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold white on dark_magenta",
        row_styles=["", "dim"],
        padding=(0, 1),
    )

    table.add_column("Ticker", style="bold yellow", width=8)
    table.add_column("Señal", width=10, justify="center")
    table.add_column("Razones", ratio=1)

    def format_reasons(reasons_list: list[str]) -> str:
        formatted = []

        for r in reasons_list:
            # Clasificación simple por contenido
            if any(x in r for x in [">", "positivo", "permitido", "manejable"]):
                formatted.append(f"[green]• {r}[/green]")
            elif any(x in r for x in ["no", "<=", "alta", ">= 75"]):
                formatted.append(f"[red]• {r}[/red]")
            else:
                formatted.append(f"[yellow]• {r}[/yellow]")

        return "\n".join(formatted)

    for candidate in signals:
        ticker = candidate["ticker"]
        signal = candidate["signal"]
        reasons = format_reasons(candidate["reasons"])

        signal_style = ""
        if signal == "COMPRAR":
            signal_style = "[bold green]"
        elif signal == "ESPERAR":
            signal_style = "[bold yellow]"
        elif signal == "OBSERVAR":
            signal_style = "[bold magenta]"

        table.add_row(
            ticker,
            f"{signal_style}{signal}[/]",
            reasons,
        )

    console.print(table)


def display_etf_analysis(etf_data: dict | None) -> None:
    """
    Muestra el análisis técnico y señal DCA para CSPX.L

    Args:
        etf_data: Diccionario retornado por analyze_etf()
    """
    console.print("\n[bold cyan]ANÁLISIS ETF — CSPX.L[/bold cyan]")
    console.print("[dim]iShares Core S&P 500 UCITS ETF (Acc)[/dim]\n")

    if not etf_data:
        console.print("[dim]  Sin datos disponibles para CSPX.L[/dim]\n")
        return

    # -------- SEÑAL PRINCIPAL --------
    signal = etf_data.get("signal", "N/A")
    score = etf_data.get("score", 0)

    if signal == "COMPRAR FUERTE":
        signal_style = "[bold green]"
    elif signal == "COMPRAR":
        signal_style = "[bold cyan]"
    elif signal == "DCA NORMAL":
        signal_style = "[bold yellow]"
    else:
        signal_style = "[bold red]"

    console.print(
        f"  Señal:  {signal_style}{signal}[/]  [dim](score: {score}/11)[/dim]\n"
    )

    # -------- TABLA DE INDICADORES --------
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold white",
    )

    table.add_column("Indicador", style="white", width=20)
    table.add_column("Valor", width=15, justify="right")
    table.add_column("Estado", width=20, justify="center")

    current_price = etf_data.get("current_price")
    sma_50 = etf_data.get("sma_50")
    sma_200 = etf_data.get("sma_200")
    rsi = etf_data.get("rsi")
    drawdown = etf_data.get("drawdown")
    bullish_trend = etf_data.get("bullish_trend")

    # Precio actual
    table.add_row(
        "Precio actual",
        f"${current_price:.2f}" if current_price else "N/A",
        "",
    )

    # SMA 50
    sma50_status = (
        "[green]Por debajo ▼[/green]"
        if current_price and sma_50 and current_price < sma_50
        else "[dim]Por encima ▲[/dim]"
    )
    table.add_row(
        "SMA 50",
        f"${sma_50:.2f}" if sma_50 else "N/A",
        sma50_status,
    )

    # SMA 200
    sma200_status = (
        "[green]Zona acumulación[/green]"
        if current_price and sma_200 and current_price < sma_200
        else "[dim]Por encima ▲[/dim]"
    )
    table.add_row(
        "SMA 200",
        f"${sma_200:.2f}" if sma_200 else "N/A",
        sma200_status,
    )

    # RSI
    rsi_status = (
        "[green]Sobreventa[/green]"
        if rsi and rsi < 40
        else "[yellow]Neutral[/yellow]"
        if rsi and rsi < 70
        else "[red]Sobrecompra[/red]"
    )
    table.add_row(
        "RSI",
        f"{rsi:.1f}" if rsi else "N/A",
        rsi_status,
    )

    # Drawdown
    dd_pct = f"{drawdown * 100:.1f}%" if drawdown else "N/A"
    dd_status = (
        "[green]Caída fuerte[/green]"
        if drawdown and drawdown < -0.10
        else "[dim]Caída leve[/dim]"
    )
    table.add_row(
        "Drawdown",
        dd_pct,
        dd_status,
    )

    # Tendencia
    trend_status = (
        "[green]Alcista ▲[/green]" if bullish_trend else "[red]Bajista ▼[/red]"
    )
    table.add_row(
        "Tendencia",
        "",
        trend_status,
    )

    console.print(table)
    console.print("[dim]─────────────────────────────────────────[/dim]")


def display_scanner_results(results: list[dict]) -> None:
    """
    Muestra los resultados del scanner de empresas candidatas a dividendos.

    Args:
        results: Lista de diccionarios retornada por scan_ticker()
    """
    console.print("\n[bold cyan]SCANNER DE DIVIDENDOS[/bold cyan]")
    console.print("[dim]Empresas evaluadas por FCF, payout y deuda[/dim]\n")

    if not results:
        console.print("[dim]  Sin resultados disponibles[/dim]\n")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on dark_blue",
        padding=(0, 1),
    )

    table.add_column("Ticker", style="bold yellow", width=8)
    table.add_column("Señal", width=12, justify="center")
    table.add_column("Score", width=8, justify="center")
    table.add_column("Dividendo", width=12, justify="right")
    table.add_column("Payout", width=10, justify="right")
    table.add_column("Deuda/FCF", width=12, justify="right")

    for result in results:
        signal = result.get("signal", "N/A")
        score = result.get("score", 0)
        dividend = result.get("dividend_yield")
        payout = result.get("payout_ratio")
        debt_fcf = result.get("debt_to_fcf")

        # Color de la señal
        if signal == "COMPRAR":
            signal_str = "[bold green]COMPRAR[/bold green]"
        elif signal == "ESPERAR":
            signal_str = "[bold yellow]ESPERAR[/bold yellow]"
        else:
            signal_str = "[bold red]DESCARTAR[/bold red]"

        # Color del score
        if score >= 7:
            score_str = f"[green]{score}/11[/green]"
        elif score >= 4:
            score_str = f"[yellow]{score}/11[/yellow]"
        else:
            score_str = f"[red]{score}/11[/red]"

        # Formateo de métricas
        dividend_str = f"{dividend * 100:.2f}%" if dividend else "N/A"
        payout_str = f"{payout * 100:.2f}%" if payout else "N/A"
        debt_str = f"{debt_fcf:.2f}x" if debt_fcf else "N/A"

        table.add_row(
            result.get("ticker", "N/A"),
            signal_str,
            score_str,
            dividend_str,
            payout_str,
            debt_str,
        )

    console.print(table)
    console.print("[dim]─────────────────────────────────────────[/dim]")
