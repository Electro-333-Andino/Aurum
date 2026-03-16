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
