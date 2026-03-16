# Copyright 2026 Anderson Andino
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Módulo responsable ÚNICAMENTE de mostrar datos en terminal.
# Usa la librería 'rich' para formato profesional con colores y tablas.

from datetime import datetime

from rich import box
from rich.console import Console
from rich.table import Table

# Console es el objeto principal de la libreria 'rich' para imprimir en terminal
console = Console()


def display_portfolio(portfolio_data: list) -> None:
    """
    Muestra la tabla del portafolio en terminal con colores.

    Args:
        portfolio_data: Lista de diccionarios retornada por get_portfolio_prices()
    """

    # Encabezado con fecha y hora actual
    now = datetime.now().strftime("%A %d %B %Y - %H:%M")
    console.print("[bold cyan]📊 INVESTMENT MORNING BRIEF[/bold cyan]")
    console.print(f"[dim]{now}[/dim]")

    # Creamos la tabla con rich
    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on dark_blue",
    )
    # Definimos las columnas
    table.add_column("Ticker", style="bold yellow", width=8)
    table.add_column("Empresa", style="white", width=30)
    table.add_column("Precio", style="bold white", width=12, justify="right")
    table.add_column("Cambio %", width=12, justify="right")
    table.add_column("Estado", width=12, justify="center")

    # Llenamos la tabla con los datos
    for stock in portfolio_data:
        change = stock["change_percent"]

        # Color y emoji según si sube o baja
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
