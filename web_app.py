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

# web_app.py
# Motor web — sin lógica de negocio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.modules.etf_analyzer import ETFAnalyzer

app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )


@app.get("/api/analisis/cspxl")
async def get_cspxl_data():
    try:
        # Instanciamos con el ticker
        analyzer = ETFAnalyzer(ticker="CSPX.L")

        # Ejecutamos tu método principal
        resultado = analyzer.analyze_etf()

        if not resultado:
            return JSONResponse(
                status_code=404,
                content={"error": "No se pudieron obtener datos de Yahoo Finance"},
            )

        # Mapeo de colores metalizados según tu señal
        # Score >= 7: COMPRAR FUERTE, 4-6: COMPRAR, 2-3: DCA NORMAL, <2: ESPERAR
        colores = {
            "COMPRAR FUERTE": "#bf953f",  # Oro
            "COMPRAR": "#0074d9",  # Azul
            "DCA NORMAL": "#d1d1d1",  # Plata
            "ESPERAR": "#8b0000",  # Rojo
        }
        color_final = colores.get(resultado["signal"], "#d1d1d1")

        # Devolvemos exactamente lo que tu lógica calculó
        return {
            "ticker": resultado["ticker"],
            "precio": f"{resultado['current_price']:.2f}",
            "rsi": f"{resultado['rsi']:.2f}" if resultado["rsi"] else "N/A",
            "score": f"{resultado['score']}",  # El total máximo según tu lógica es 11
            "recomendacion": resultado["signal"],
            "color": color_final,
        }

    except Exception as e:
        print(f"[ERROR WEB] Error en endpoint CSPX.L: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
