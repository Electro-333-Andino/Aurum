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
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Montamos la carpeta 'static' para los estilos CSS
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Configuramos la carpeta de plantillas HTML
templates = Jinja2Templates(directory="web/templates")


@app.get("/")
async def serve_home(request: Request):
    # La forma correcta y segura es pasar un diccionario al parámetro 'context'
    # 'request' DEBE ser parte de ese diccionario obligatoriamente
    return templates.TemplateResponse(
        request=request, name="index.html", context={"request": request}
    )
