// web/static/js/main.js

const API_BASE_URL = '/api';

document.addEventListener('DOMContentLoaded', () => {
    // --- View Switching Logic ---
    const navButtons = document.querySelectorAll('.main-nav .nav-button');
    const views = document.querySelectorAll('.view');
    const etfTicker = 'CSPX.L'; // From context

    function showView(viewId) {
        views.forEach(view => {
            if (view.id === viewId) {
                view.classList.remove('hidden');
                view.classList.add('active'); // Add active class if needed for specific styling
            } else {
                view.classList.add('hidden');
                view.classList.remove('active');
            }
        });
    }

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const viewType = button.dataset.view;
            showView(`${viewType}-view`);

            // Load data for the activated view
            if (viewType === 'portfolio') {
                loadPortfolioData();
            } else if (viewType === 'etf') {
                loadETFData();
            } else if (viewType === 'dividendos') {
                loadDividendosData();
            } else if (viewType === 'noticias') {
                // Default to macro news when news view is activated
                document.querySelector('.news-type-button[data-news-type="macro"]').click();
            }
        });
    });

    // --- News Type Switching Logic ---
    const newsTypeButtons = document.querySelectorAll('.news-type-button');
    const macroNewsList = document.getElementById('macro-news-list');
    const companyNewsList = document.getElementById('company-news-list');
    const companyNewsTickerInput = document.getElementById('company-news-ticker-input');
    const searchCompanyNewsButton = document.getElementById('search-company-news');

    newsTypeButtons.forEach(button => {
        button.addEventListener('click', () => {
            newsTypeButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const newsType = button.dataset.newsType;

            if (newsType === 'macro') {
                macroNewsList.classList.remove('hidden');
                companyNewsList.classList.add('hidden');
                companyNewsTickerInput.classList.add('hidden');
                searchCompanyNewsButton.classList.add('hidden');
                loadMacroNews();
            } else { // company news
                macroNewsList.classList.add('hidden');
                companyNewsList.classList.remove('hidden');
                companyNewsTickerInput.classList.remove('hidden');
                searchCompanyNewsButton.classList.remove('hidden');
                // Clear company news list and prompt user to search
                companyNewsList.innerHTML = `<p>Introduce un símbolo de empresa (ej: AAPL) y haz clic en "Buscar".</p>`;
            }
        });
    });

    searchCompanyNewsButton.addEventListener('click', () => {
        const ticker = companyNewsTickerInput.value.trim().toUpperCase();
        if (ticker) {
            loadCompanyNews(ticker);
        } else {
            alert('Por favor, introduce un símbolo de empresa válido para buscar noticias.');
        }
    });

    companyNewsTickerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchCompanyNewsButton.click();
        }
    });


    // --- Data Fetching & Rendering Functions ---

    // Helper to get signal class
    function getSignalClass(signal) {
        if (!signal) return 'grey';
        signal = signal.toUpperCase();
        if (signal.includes('COMPRAR FUERTE')) return 'gold';
        if (signal.includes('COMPRAR')) return 'blue';
        if (signal.includes('DCA NORMAL')) return 'orange';
        if (signal.includes('ESPERAR') || signal.includes('DESCARTAR')) return 'red';
        return 'grey';
    }


    async function loadPortfolioData() {
        const portfolioDataTable = document.getElementById('portfolio-data');
        portfolioDataTable.innerHTML = `<tr><td colspan="4">Cargando datos del portafolio...</td></tr>`;

        try {
            const response = await fetch(`${API_BASE_URL}/portfolio_prices`);
            const data = await response.json();

            if (response.status !== 200 || data.error) {
                portfolioDataTable.innerHTML = `<tr><td colspan="4" class="error-message">Error: ${data.error || 'No se pudieron cargar los datos del portafolio.'}</td></tr>`;
                return;
            }

            if (data.length === 0) {
                portfolioDataTable.innerHTML = `<tr><td colspan="4">No hay datos de portafolio disponibles.</td></tr>`;
                return;
            }

            portfolioDataTable.innerHTML = data.map(item => `
                <tr>
                    <td>${item.ticker}</td>
                    <td>${item.name}</td>
                    <td>$${item.price?.toFixed(2) || 'N/A'}</td>
                    <td class="${item.change_percent >= 0 ? 'text-green-400' : 'text-red-400'}">${item.change_percent?.toFixed(2) || 'N/A'}%</td>
                </tr>
            `).join('');

        } catch (error) {
            console.error('Error loading portfolio data:', error);
            portfolioDataTable.innerHTML = `<tr><td colspan="4" class="error-message">Error al cargar datos del portafolio.</td></tr>`;
        }
    }

    async function loadETFData() {
        const etfDataTable = document.getElementById('etf-data');
        const etfSignalP = document.getElementById('etf-signal');
        etfDataTable.innerHTML = `<tr><td>Cargando datos del ETF...</td><td></td></tr>`;
        etfSignalP.innerHTML = `Señal: Cargando...`;

        try {
            const response = await fetch(`${API_BASE_URL}/etf_analysis`);
            const data = await response.json();

            if (response.status !== 200 || data.error) {
                etfDataTable.innerHTML = `<tr><td colspan="2" class="error-message">Error: ${data.error || 'No se pudieron cargar los datos del ETF.'}</td></tr>`;
                etfSignalP.textContent = `Señal: Error.`;
                return;
            }

            etfDataTable.innerHTML = `
                <tr><td>Ticker</td><td>${data.ticker || 'N/A'}</td></tr>
                <tr><td>Precio Actual</td><td>$${data.current_price?.toFixed(2) || 'N/A'}</td></tr>
                <tr><td>SMA 50</td><td>$${data.sma_50?.toFixed(2) || 'N/A'}</td></tr>
                <tr><td>SMA 200</td><td>$${data.sma_200?.toFixed(2) || 'N/A'}</td></tr>
                <tr><td>RSI</td><td>${data.rsi?.toFixed(2) || 'N/A'}</td></tr>
                <tr><td>Drawdown (Anual)</td><td>${(data.drawdown * 100)?.toFixed(2) || 'N/A'}%</td></tr>
                <tr><td>Score</td><td>${data.score || 'N/A'}</td></tr>
            `;
            const signalClass = getSignalClass(data.signal);
            etfSignalP.innerHTML = `Señal: <span class="status-badge ${signalClass}">${data.signal || 'N/A'}</span>`;

        } catch (error) {
            console.error('Error loading ETF data:', error);
            etfDataTable.innerHTML = `<tr><td colspan="2" class="error-message">Error al cargar datos del ETF.</td></tr>`;
            etfSignalP.textContent = `Señal: Error.`;
        }
    }

    async function loadDividendosData() {
        const dividendosDataTable = document.getElementById('dividendos-data');
        dividendosDataTable.innerHTML = `<tr><td colspan="6">Cargando candidatas a dividendos...</td></tr>`;

        try {
            const response = await fetch(`${API_BASE_URL}/scanner_results`);
            const data = await response.json();

            if (response.status !== 200 || data.error) {
                dividendosDataTable.innerHTML = `<tr><td colspan="6" class="error-message">Error: ${data.error || 'No se pudieron cargar las candidatas a dividendos.'}</td></tr>`;
                return;
            }

            if (data.length === 0) {
                dividendosDataTable.innerHTML = `<tr><td colspan="6">No hay candidatas a dividendos disponibles.</td></tr>`;
                return;
            }

            dividendosDataTable.innerHTML = data.map(item => `
                <tr>
                    <td>${item.ticker}</td>
                    <td>${item.score || 'N/A'}</td>
                    <td><span class="status-badge ${getSignalClass(item.signal)}">${item.signal || 'N/A'}</span></td>
                    <td>${(item.dividend_yield * 100)?.toFixed(2) || 'N/A'}%</td>
                    <td>${(item.payout_ratio * 100)?.toFixed(2) || 'N/A'}%</td>
                    <td>${item.debt_to_fcf?.toFixed(2) || 'N/A'}</td>
                </tr>
            `).join('');

        } catch (error) {
            console.error('Error loading dividendos data:', error);
            dividendosDataTable.innerHTML = `<tr><td colspan="6" class="error-message">Error al cargar candidatas a dividendos.</td></tr>`;
        }
    }

    async function loadMacroNews() {
        const macroNewsListElement = document.getElementById('macro-news-list');
        macroNewsListElement.innerHTML = `<p>Cargando noticias macro...</p>`;

        try {
            const response = await fetch(`${API_BASE_URL}/news/macro`);
            const data = await response.json();

            if (response.status !== 200 || data.error) {
                macroNewsListElement.innerHTML = `<p class="error-message">Error: ${data.error || 'No se pudieron cargar las noticias macro.'}</p>`;
                return;
            }

            if (data.length === 0) {
                macroNewsListElement.innerHTML = `<p>No hay noticias macroeconómicas disponibles.</p>`;
                return;
            }

            macroNewsListElement.innerHTML = data.map(item => `
                <div class="news-card">
                    <h4>${item.title}</h4>
                    <p>${item.original_title}</p>
                    <p class="source-date">${item.source} - ${item.published}</p>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error loading macro news:', error);
            macroNewsListElement.innerHTML = `<p class="error-message">Error al cargar noticias macroeconómicas.</p>`;
        }
    }

    async function loadCompanyNews(ticker) {
        const companyNewsListElement = document.getElementById('company-news-list');
        companyNewsListElement.innerHTML = `<p>Cargando noticias para ${ticker}...</p>`;

        try {
            const response = await fetch(`${API_BASE_URL}/news/company/${ticker}`);
            const data = await response.json();

            if (response.status !== 200 || data.error) {
                companyNewsListElement.innerHTML = `<p class="error-message">Error: ${data.error || `No se pudieron cargar las noticias para ${ticker}.`}</p>`;
                return;
            }

            if (data.length === 0) {
                companyNewsListElement.innerHTML = `<p>No hay noticias para ${ticker} disponibles.</p>`;
                return;
            }

            companyNewsListElement.innerHTML = data.map(item => `
                <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="news-card">
                    <h4>${item.title}</h4>
                    <p>${item.original_title}</p>
                    <p class="source-date">${item.source}</p>
                </a>
            `).join('');

        } catch (error) {
            console.error(`Error loading company news for ${ticker}:`, error);
            companyNewsListElement.innerHTML = `<p class="error-message">Error al cargar noticias de la empresa para ${ticker}.</p>`;
        }
    }

    // --- Initial Load ---
    // Simulate click on the active nav button to load initial view data
    document.querySelector('.main-nav .nav-button.active').click();
});
