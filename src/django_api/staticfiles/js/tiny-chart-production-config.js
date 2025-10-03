/**
 * 实际的TinyChart定义配置
 * 基于MEM Dashboard的实际需求
 */

// 扩展Chart定义，包含实际的经济指标
window.TINYCHART_DEFINITIONS = [
    // 债务占GDP比例Chart（替换现有的debtToGdpChart）
    {
        id: 'debt-to-gdp-tinychart',
        containerId: 'debtToGdpChart', // 使用现有的canvas ID
        title: 'Debt-to-GDP Ratio',
        dataSource: {
            type: 'fred',
            indicator: 'GFDEGDQ188S', // Federal Debt: Total Public Debt as Percent of GDP
            period: 'quarterly',
            count: 100, // 过去25年的季度数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'debt_trend', // 债务增加为红色，减少为绿色
        theme: 'minimal',
        config: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                y: { 
                    display: false,
                    min: 'auto',
                    max: 'auto'
                },
                x: { display: false }
            },
            elements: {
                point: { radius: 0 },
                line: { 
                    borderWidth: 1.5,
                    tension: 0.1 
                }
            }
        },
        onUpdate: (chart, data) => {
            // 更新主要指标显示
            const currentValue = data[data.length - 1];
            const previousValue = data[data.length - 2];
            const change = currentValue - previousValue;
            const changePercent = ((change / previousValue) * 100).toFixed(2);
            
            // 更新主要数值显示
            const mainValue = document.querySelector('.metric-row .metric-value');
            if (mainValue) {
                const quarter = Math.ceil((new Date().getMonth() + 1) / 3);
                const year = new Date().getFullYear();
                mainValue.innerHTML = `${currentValue.toFixed(2)}% <span class="text-gray-500 text-xs">(Q${quarter} ${year}, FRED)</span>`;
            }
            
            // 更新变化指标
            const changeIndicator = document.getElementById('debtChangeIndicator');
            if (changeIndicator) {
                changeIndicator.style.color = change > 0 ? '#ef4444' : '#22c55e';
                changeIndicator.textContent = change > 0 ? `+${changePercent}%` : `${changePercent}%`;
            }
            
            // 更新小部件显示
            const widgetValue = document.querySelector('[style*="font-size: 13px; font-weight: 700"]');
            if (widgetValue) {
                widgetValue.textContent = `${currentValue.toFixed(2)}%`;
            }
        }
    },

    // 失业率TinyChart
    {
        id: 'unemployment-rate',
        containerId: 'unemployment-chart-container',
        title: 'Unemployment Rate',
        dataSource: {
            type: 'fred',
            indicator: 'UNRATE',
            period: 'monthly',
            count: 60, // 5年月度数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'unemployment_trend',
        theme: 'minimal'
    },

    // 通胀率TinyChart
    {
        id: 'inflation-rate',
        containerId: 'inflation-chart-container',
        title: 'CPI Inflation Rate',
        dataSource: {
            type: 'fred',
            indicator: 'CPIAUCSL',
            period: 'monthly',
            count: 36, // 3年月度数据
            cache: true,
            transform: 'year_over_year_change' // 转换为同比变化率
        },
        chartType: 'line',
        colorStrategy: 'inflation_trend',
        theme: 'minimal'
    },

    // GDP增长率TinyChart
    {
        id: 'gdp-growth',
        containerId: 'gdp-growth-container',
        title: 'GDP Growth Rate',
        dataSource: {
            type: 'fred',
            indicator: 'GDPC1',
            period: 'quarterly',
            count: 40, // 10年季度数据
            cache: true,
            transform: 'quarter_over_quarter_change'
        },
        chartType: 'line',
        colorStrategy: 'growth_trend',
        theme: 'minimal'
    },

    // 10年期国债收益率TinyChart
    {
        id: 'treasury-10y',
        containerId: 'treasury-10y-container',
        title: '10-Year Treasury Yield',
        dataSource: {
            type: 'fred',
            indicator: 'GS10',
            period: 'daily',
            count: 252, // 1年工作日数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'interest_rate_trend',
        theme: 'minimal'
    },

    // 联邦基金利率TinyChart
    {
        id: 'fed-funds-rate',
        containerId: 'fed-funds-container',
        title: 'Federal Funds Rate',
        dataSource: {
            type: 'fred',
            indicator: 'FEDFUNDS',
            period: 'monthly',
            count: 60, // 5年月度数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'fed_rate_trend',
        theme: 'minimal'
    },

    // 美元指数TinyChart
    {
        id: 'dollar-index',
        containerId: 'dollar-index-container',
        title: 'US Dollar Index',
        dataSource: {
            type: 'fred',
            indicator: 'DTWEXBGS',
            period: 'daily',
            count: 252, // 1年工作日数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'currency_trend',
        theme: 'minimal'
    },

    // 标普500指数TinyChart
    {
        id: 'sp500-index',
        containerId: 'sp500-container',
        title: 'S&P 500 Index',
        dataSource: {
            type: 'fred',
            indicator: 'SP500',
            period: 'daily',
            count: 252, // 1年工作日数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'stock_trend',
        theme: 'minimal'
    },

    // 个人储蓄率TinyChart
    {
        id: 'personal-savings-rate',
        containerId: 'savings-rate-container',
        title: 'Personal Savings Rate',
        dataSource: {
            type: 'fred',
            indicator: 'PSAVERT',
            period: 'monthly',
            count: 60, // 5年月度数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'savings_trend',
        theme: 'minimal'
    },

    // 消费者信心指数TinyChart
    {
        id: 'consumer-confidence',
        containerId: 'confidence-container',
        title: 'Consumer Confidence Index',
        dataSource: {
            type: 'fred',
            indicator: 'CSCICP03USM665S',
            period: 'monthly',
            count: 36, // 3年月度数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'confidence_trend',
        theme: 'minimal'
    },

    // 工业生产指数TinyChart
    {
        id: 'industrial-production',
        containerId: 'industrial-production-container',
        title: 'Industrial Production Index',
        dataSource: {
            type: 'fred',
            indicator: 'INDPRO',
            period: 'monthly',
            count: 60, // 5年月度数据
            cache: true,
            transform: 'year_over_year_change'
        },
        chartType: 'line',
        colorStrategy: 'production_trend',
        theme: 'minimal'
    },

    // 房屋销售TinyChart
    {
        id: 'housing-sales',
        containerId: 'housing-sales-container',
        title: 'Existing Home Sales',
        dataSource: {
            type: 'fred',
            indicator: 'EXHOSLUSM495S',
            period: 'monthly',
            count: 48, // 4年月度数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'housing_trend',
        theme: 'minimal'
    },

    // 货币供应量M2 TinyChart
    {
        id: 'money-supply-m2',
        containerId: 'm2-supply-container',
        title: 'Money Supply M2',
        dataSource: {
            type: 'fred',
            indicator: 'M2SL',
            period: 'monthly',
            count: 60, // 5年月度数据
            cache: true,
            transform: 'year_over_year_change'
        },
        chartType: 'line',
        colorStrategy: 'money_supply_trend',
        theme: 'minimal'
    },

    // 能源价格TinyChart（WTI原油）
    {
        id: 'oil-prices',
        containerId: 'oil-prices-container',
        title: 'WTI Crude Oil Prices',
        dataSource: {
            type: 'fred',
            indicator: 'DCOILWTICO',
            period: 'daily',
            count: 252, // 1年工作日数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'commodity_trend',
        theme: 'minimal'
    },

    // 汇率指标：EUR/USD
    {
        id: 'eur-usd-rate',
        containerId: 'eur-usd-container',
        title: 'EUR/USD Exchange Rate',
        dataSource: {
            type: 'fred',
            indicator: 'DEXUSEU',
            period: 'daily',
            count: 252, // 1年工作日数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'currency_trend',
        theme: 'minimal'
    },

    // 贸易平衡TinyChart
    {
        id: 'trade-balance',
        containerId: 'trade-balance-container',
        title: 'Trade Balance',
        dataSource: {
            type: 'fred',
            indicator: 'BOPGSTB',
            period: 'monthly',
            count: 36, // 3年月度数据
            cache: true
        },
        chartType: 'line',
        colorStrategy: 'trade_trend',
        theme: 'minimal'
    }
];

// 为不同类型的经济指标定义专门的颜色策略
window.COLOR_STRATEGIES = {
    ...window.COLOR_STRATEGIES, // 保留现有策略
    
    // 债务趋势：增加为红色，减少为绿色
    'debt_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#ef4444' : '#22c55e';
    },
    
    // 失业率趋势：上升为红色，下降为绿色
    'unemployment_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#ef4444' : '#22c55e';
    },
    
    // 通胀趋势：高通胀为红色，低通胀为绿色，通缩为蓝色
    'inflation_trend': (data) => {
        const current = data[data.length - 1];
        if (current > 3) return '#ef4444'; // 高通胀
        if (current < 0) return '#3b82f6'; // 通缩
        return '#22c55e'; // 适度通胀
    },
    
    // GDP增长趋势：正增长为绿色，负增长为红色
    'growth_trend': (data) => {
        const current = data[data.length - 1];
        return current >= 0 ? '#22c55e' : '#ef4444';
    },
    
    // 利率趋势：上升为红色（紧缩），下降为绿色（宽松）
    'interest_rate_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#ef4444' : '#22c55e';
    },
    
    // 联邦利率趋势
    'fed_rate_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#ef4444' : '#22c55e';
    },
    
    // 货币趋势：美元走强为绿色，走弱为红色
    'currency_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#22c55e' : '#ef4444';
    },
    
    // 股市趋势：上涨为绿色，下跌为红色
    'stock_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#22c55e' : '#ef4444';
    },
    
    // 储蓄率趋势：上升为绿色，下降为红色
    'savings_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#22c55e' : '#ef4444';
    },
    
    // 信心指数趋势：上升为绿色，下降为红色
    'confidence_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#22c55e' : '#ef4444';
    },
    
    // 生产指数趋势：增长为绿色，下降为红色
    'production_trend': (data) => {
        const current = data[data.length - 1];
        return current >= 0 ? '#22c55e' : '#ef4444';
    },
    
    // 房地产趋势：销售增加为绿色，减少为红色
    'housing_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#22c55e' : '#ef4444';
    },
    
    // 货币供应量趋势：增长适度为绿色，过度增长为红色
    'money_supply_trend': (data) => {
        const current = data[data.length - 1];
        if (current > 10) return '#ef4444'; // 过度增长
        if (current < -5) return '#ef4444'; // 过度收缩
        return '#22c55e'; // 适度增长
    },
    
    // 商品趋势：价格上涨为红色，下跌为绿色
    'commodity_trend': (data) => {
        const current = data[data.length - 1];
        const previous = data[data.length - 2];
        return current > previous ? '#ef4444' : '#22c55e';
    },
    
    // 贸易趋势：顺差为绿色，逆差为红色
    'trade_trend': (data) => {
        const current = data[data.length - 1];
        return current >= 0 ? '#22c55e' : '#ef4444';
    }
};

// 更新全局配置以支持更多并发请求和更长的缓存时间
window.TINYCHART_CONFIG = {
    ...window.TINYCHART_CONFIG,
    
    api: {
        maxConcurrentRequests: 8, // 增加并发请求数
        requestTimeout: 15000, // 15秒超时
        retryAttempts: 3
    },
    
    cache: {
        timeout: 10 * 60 * 1000, // 10分钟缓存
        maxSize: 50 // 最大缓存50个数据集
    },
    
    rendering: {
        batchSize: 6, // 每批渲染6个图表
        batchDelay: 50, // 50ms延迟
        priorityCharts: ['debt-to-gdp-tinychart'] // 优先渲染的图表
    },
    
    monitoring: {
        enabled: true,
        collectInterval: 60000, // 1分钟收集一次指标
        enableConsoleOutput: true,
        memoryThreshold: 0.8 // 80%内存使用警告
    }
};

console.log('📊 Production TinyChart definitions loaded with', window.TINYCHART_DEFINITIONS.length, 'chart definitions');
