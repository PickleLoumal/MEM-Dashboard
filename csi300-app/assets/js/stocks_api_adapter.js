/**
 * Stocks API Adapter for Django Backend
 * 连接到Django后端的股票数据API
 */

class StocksApiAdapter {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || this.detectBaseUrl();
    }

    detectBaseUrl() {
        // 自动检测API基础URL
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const port = window.location.port;
        
        // 如果是file://协议，默认使用localhost:8001
        if (protocol === 'file:') {
            console.warn('Detected file:// protocol. Using default http://localhost:8001');
            return 'http://localhost:8001';
        }
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            // 本地开发环境 - Django API运行在8001端口
            return `http://${hostname}:8001`;
        } else {
            // 生产环境
            return window.location.origin;
        }
    }

    /**
     * 获取股票列表
     * @param {string} market - 市场类型 ('CN', 'US', etc.)
     */
    async getStockList(market = 'CN') {
        try {
            const response = await fetch(`${this.baseUrl}/api/stocks/list/?market=${market}`);
            const data = await response.json();
            
            if (data.success) {
                return data.stocks;
            } else {
                console.error('Failed to fetch stock list:', data.error);
                return [];
            }
        } catch (error) {
            console.error('Error fetching stock list:', error);
            return [];
        }
    }

    /**
     * 获取分时数据（1分钟K线）
     * @param {string} symbol - 股票代码
     */
    async getIntradayData(symbol) {
        try {
            const response = await fetch(`${this.baseUrl}/api/stocks/intraday/?symbol=${symbol}`);
            const data = await response.json();
            
            return data;
        } catch (error) {
            console.error('Error fetching intraday data:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 获取历史数据（支持不同时间间隔的K线数据）
     * @param {string} symbol - 股票代码
     * @param {number} days - 天数
     * @param {string} interval - 数据间隔 ('1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo')
     * @param {string} period - Legacy period string kept for compatibility (ignored by AkShare backend)
     */
    async getHistoricalData(symbol, days = 30, interval = '1d', period = null) {
        try {
            let url = `${this.baseUrl}/api/stocks/historical/?symbol=${symbol}&days=${days}&interval=${interval}`;
            if (period) {
                url += `&period=${period}`;
            }
            
            console.log(`📡 API Call: ${url}`);
            const response = await fetch(url);
            const data = await response.json();
            
            return data;
        } catch (error) {
            console.error('Error fetching historical data:', error);
            return { success: false, error: error.message };
        }
    }

    async getTopPicks(limit = 5, direction = 'buy') {
        try {
            const response = await fetch(`${this.baseUrl}/api/stocks/top-picks/?limit=${limit}&direction=${direction}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching top picks:', error);
            return { success: false, error: error.message };
        }
    }

    async generateStockScore(symbol) {
        try {
            const response = await fetch(`${this.baseUrl}/api/stocks/score/generate/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol })
            });
            return await response.json();
        } catch (error) {
            console.error('Error generating stock score:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 将API数据转换为图表所需格式（历史数据）
     */
    transformHistoricalDataForChart(apiResponse) {
        if (!apiResponse.success || !apiResponse.data_points) {
            return [];
        }

        return apiResponse.data_points.map(point => {
            const transformed = {
                date: point.date,
                open: point.open,
                high: point.high,
                low: point.low,
                close: point.close,
                volume: point.volume
            };
            
            // 可选字段，可能不存在
            if (point.ma5 !== undefined) transformed.ma5 = point.ma5;
            if (point.ma10 !== undefined) transformed.ma10 = point.ma10;
            if (point.obv !== undefined) transformed.obv = point.obv;
            if (point.obv_ma5 !== undefined) transformed.obv_ma5 = point.obv_ma5;
            if (point.obv_ma10 !== undefined) transformed.obv_ma10 = point.obv_ma10;
            if (point.cmf !== undefined) transformed.cmf = point.cmf;
            
            return transformed;
        });
    }

    /**
     * 将API数据转换为图表所需格式（分时数据）
     */
    transformIntradayDataForChart(apiResponse) {
        if (!apiResponse.success || !apiResponse.data_points) {
            return [];
        }

        return apiResponse.data_points.map(point => ({
            time: point.time,
            open: point.open,
            high: point.high,
            low: point.low,
            close: point.close,
            volume: point.volume,
            vwap: point.vwap
        }));
    }
}

// 创建全局实例
window.stocksApiAdapter = new StocksApiAdapter();
