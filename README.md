# Aurum: Investment Morning Brief

**Aurum** es una herramienta de línea de comandos simple pero potente, diseñada para proporcionar un resumen rápido de tu portafolio de inversiones. Obtiene los precios de las acciones en tiempo real desde Yahoo Finance y los muestra en una tabla limpia y fácil de leer directamente en tu terminal.

## Características

*   **Datos en Tiempo Real:** Obtiene los últimos precios de las acciones utilizando la librería `yfinance`.
*   **Reportes Claros y Concisos:** Muestra el rendimiento de tu portafolio en una tabla formateada con colores, gracias a la librería `rich`.
*   **Fácil de Usar:** Simplemente ejecuta el script para obtener tu informe de inversión diario.
*   **Personalizable:** Modifica fácilmente la lista `PORTFOLIO` en `src/modules/prices.py` para rastrear tus propias acciones.

## Cómo Empezar

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/Electro-333-Andino/Aurum.git
    cd Aurum
    ```

2.  **Instala las dependencias:**
    *(Nota: Se recomienda usar un entorno virtual)*

    Puedes instalar las dependencias usando `uv` (recomendado) o `pip3`.

    **Opción A: Usando `uv`**
    ```bash
    uv sync
    ```

    **Opción B: Usando `pip3`**
    ```bash
    pip3 install .
    ```

3.  **Ejecuta la aplicación:**
    ```bash
    python3 main.py
    ```
