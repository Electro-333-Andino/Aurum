import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# All module imports should come after sys.path.append
from src.config import CANDIDATES, ETF_TICKER, PORTFOLIO
from src.modules.etf_analyzer import ETFAnalyzer
from src.modules.fundamentals import get_clean_fundamentals
from src.modules.news import get_company_news, get_macro_news
from src.modules.prices import get_portfolio_prices, get_price_analysis
from src.modules.scanner import scan_ticker

# Add project root to sys.path for importing modules
# This is crucial for running the web_app.app correctly if main.py is the entry point
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))  # Ensure src and main are discoverable
app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# ETF_TICKER is now imported from src/config.py


@app.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "etf_ticker": ETF_TICKER},
    )


@app.get("/api/etf_analysis")
async def api_etf_analysis():
    analyzer = ETFAnalyzer(ETF_TICKER)
    result = analyzer.analyze_etf()
    if not result:
        return JSONResponse(
            status_code=404,
            content={"error": "No se pudieron obtener datos del ETF"},
        )
    return JSONResponse(content=result)


@app.get("/api/portfolio_prices")
async def api_portfolio_prices():
    results = get_portfolio_prices(PORTFOLIO)
    if not results:
        return JSONResponse(
            status_code=404,
            content={"error": "No se pudieron obtener precios del portafolio"},
        )
    return JSONResponse(content=results)


@app.get("/api/scanner_results")
async def api_scanner_results():
    scanner_results = []
    for ticker in CANDIDATES:
        result = scan_ticker(ticker)
        if result is not None:
            scanner_results.append(result)
    if not scanner_results:
        return JSONResponse(
            status_code=404,
            content={"error": "No se pudieron obtener resultados del scanner"},
        )
    return JSONResponse(content=scanner_results)


@app.get("/api/stock_analysis/{ticker}")
async def api_stock_analysis(ticker: str):
    price_analysis = get_price_analysis(ticker)
    fundamentals = get_clean_fundamentals(ticker)

    response_data = {}
    if price_analysis:
        response_data.update(price_analysis)
    if fundamentals:
        response_data.update(fundamentals)

    if not response_data:
        return JSONResponse(
            status_code=404,
            content={"error": f"No se pudieron obtener datos para {ticker}"},
        )
    return JSONResponse(content=response_data)


@app.get("/api/news/macro")
async def api_news_macro():
    macro_news = get_macro_news()
    if not macro_news:
        return JSONResponse(
            status_code=404,
            content={"error": "No se pudieron obtener noticias macro"},
        )
    return JSONResponse(content=macro_news)


@app.get("/api/news/company/{ticker}")
async def api_news_company(ticker: str):
    company_news = get_company_news(ticker)
    if not company_news:
        return JSONResponse(
            status_code=404,
            content={"error": f"No se pudieron obtener noticias para {ticker}"},
        )
    return JSONResponse(content=company_news)
