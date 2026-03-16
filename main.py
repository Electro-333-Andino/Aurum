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

# Punto de entrada principal del programa.
from src.modules.prices import get_portfolio_prices
from src.modules.report import display_portfolio


def main():
    """Función principal que ejecuta el reporte."""
    print("Obteniendo datos del mercado...")

    # Obtenemos los precios del portafolio
    portfolio_data: list[dict] = get_portfolio_prices()
    # Mostramos el reporte en terminal
    display_portfolio(portfolio_data)


# Esto asegura que main() solo se ejecute cuando corres el archivo
# directamente, no cuando otro archivo lo importa
if __name__ == "__main__":
    main()
