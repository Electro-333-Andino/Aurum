# Aurum 🪙

**Aurum** es un motor de análisis financiero de alto rendimiento diseñado para la terminal. Este sistema permite realizar un escaneo profundo de activos bajo un enfoque de **inversión sostenible y técnica**, priorizando la seguridad del software y el rigor de los datos financieros.

---

## 🚀 Propósito del Proyecto

El objetivo de Aurum es transformar datos financieros crudos en señales de inversión accionables. A diferencia de las herramientas comerciales, Aurum permite un control total sobre las métricas de **sostenibilidad de dividendos** y el filtrado de **ETFs de acumulación**, operando bajo una arquitectura limpia y modular en Python.

## ✨ Características Principales

* **Análisis Fundamental:** Evaluación de ratios de deuda, flujo de caja libre (Free Cash Flow) y cobertura de dividendos.
* **Estrategia de ETFs:** Filtros específicos para identificar fondos de acumulación eficientes.
* **Indicadores Técnicos:** Cálculo nativo de RSI, Medias Móviles (SMA/EMA) y otros indicadores de momentum.
* **Desempeño Moderno:** Ejecución optimizada utilizando las últimas capacidades de Python 3.12.
* **Seguridad de Suministro:** Configurado para prevenir ataques de cadena de suministro mediante la gestión estricta de dependencias.

## 🛠️ Stack Tecnológico

* **Lenguaje:** [Python 3.12+](https://www.python.org/)
* **Gestor de Paquetes:** [uv](https://github.com/astral-sh/uv) (Rápido, seguro y determinista).
* **Entorno de Ejecución:** Optimizado para Linux (probado en Linux Mint).
* **Editor Recomendado:** [Zed](https://zed.dev/) (Configurado para máxima productividad).

## 📦 Instalación

Asegúrate de tener instalado el gestor de paquetes \`uv\`.

1. **Clonar el repositorio:**
```bash
git clone https://github.com/Electro-333-Andino/Aurum.git
cd Aurum
```

2. **Sincronizar el entorno y dependencias:**
```bash
uv sync
```

3. **Configurar variables de entorno:**
Crea un archivo \`.env\` en la raíz del proyecto para tus credenciales de API:
```bash
FINNHUB_API_KEY=tu_clave_aqui
```

## 📈 Uso del Motor

Para ejecutar el motor de análisis desde la raíz del proyecto:

```bash
uv run python main.py
```

## 🛡️ Seguridad

Este proyecto implementa políticas de seguridad proactivas en el desarrollo:
* **Aislamiento:** Uso de entornos virtuales deterministas.
* **Restricción de Scripts:** Desactivación de scripts de post-instalación en paquetes para evitar ejecución de código arbitrario.
* **Validación de Dependencias:** Bloqueo de versiones mediante \`uv.lock\`.

## 🗺️ Roadmap

- [x] Implementación de caché de datos locales para optimizar llamadas a APIs.
- [x] Integración de la librería \`Rich\` para una interfaz de terminal visualmente mejorada.
- [x] Generación de reportes automatizados en formato Markdown.

---

**Desarrollado con precisión técnica y enfoque en seguridad financiera.**
