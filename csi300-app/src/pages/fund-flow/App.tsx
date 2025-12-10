import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import {
  createChart,
  ColorType,
  IChartApi,
  CandlestickSeries,
  LineSeries,
  HistogramSeries,
  BaselineSeries,
  LineType,
} from 'lightweight-charts';
import { GlobalNav, GlobalNavProps } from '@shared/components/GlobalNav';
import { ApiService } from '@shared/api/generated';
import { convertToChartTime, formatNumber, formatLargeNumber, calculateMA } from './utils';

// ============ Observability / Logging ============
const LOG_PREFIX = '📊 [FundFlow]';

interface LogContext {
  component?: string;
  action?: string;
  symbol?: string;
  timeRange?: string;
  duration?: number;
  [key: string]: unknown;
}

const logger = {
  info: (message: string, context?: LogContext) => {
    console.log(`${LOG_PREFIX} ${message}`, context ?? '');
  },
  warn: (message: string, context?: LogContext) => {
    console.warn(`${LOG_PREFIX} ⚠️ ${message}`, context ?? '');
  },
  error: (message: string, error?: unknown, context?: LogContext) => {
    console.error(`${LOG_PREFIX} ❌ ${message}`, { error, ...context });
  },
  debug: (message: string, context?: LogContext) => {
    if (import.meta.env.DEV) {
      console.debug(`${LOG_PREFIX} 🔍 ${message}`, context ?? '');
    }
  },
  // Performance tracking
  time: (label: string): (() => number) => {
    const start = performance.now();
    return () => {
      const duration = performance.now() - start;
      console.log(`${LOG_PREFIX} ⏱️ ${label}: ${duration.toFixed(2)}ms`);
      return duration;
    };
  },
  // User action tracking
  action: (action: string, context?: LogContext) => {
    console.log(`${LOG_PREFIX} 👆 User Action: ${action}`, context ?? '');
  },
};

// Types
interface Stock {
  symbol: string;
  name: string;
  id?: number;
  market?: string;
}

interface DataPoint {
  date?: string;
  time?: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  ma5?: number;
  ma10?: number;
  obv?: number;
  obv_ma5?: number;
  obv_ma10?: number;
  cmf?: number;
  vwap?: number;
}

/**
 * Extended HistoricalResponse interface that handles schema mismatch.
 *
 * KNOWN ISSUE: OpenAPI schema defines 'data' but backend actually returns 'data_points'.
 * TODO: Fix backend OpenAPI schema in views.py to match actual response structure.
 *
 * @see src/django_api/stocks/views.py - HistoricalDataResponse schema
 * @see src/django_api/stocks/services.py - format_historical_response returns 'data_points'
 */
interface HistoricalResponse {
  success: boolean;
  data_points?: DataPoint[];  // Actual backend field name
  data?: DataPoint[];         // OpenAPI schema field name (incorrect)
  update_time?: string;
  previous_close?: number;
  stock_score?: ScoreData;
  error?: string;
  message?: string;
  current_price?: number;
  change?: number;
  change_pct?: number;
  open_price?: number;
  day_range?: string;
  price_52w_high?: number;
  price_52w_low?: number;
  volume?: number;
}

interface ScoreData {
  total_score: number;
  recommended_action: string;
  signal_date?: string;
  execution_date?: string;
  stop_loss_price?: number;
  take_profit_price?: number;
  suggested_position_pct?: number;
  score_components?: Record<string, { raw: number; weighted: number; reasons?: string[] }>;
}

interface TopPick {
  symbol: string;
  name: string;
  price?: number;
  change_percent?: number;
  sparkline?: { date: string; close: number }[];
  last_close?: number;
}

// Score component labels
const COMPONENT_LABELS: Record<string, string> = {
  momentum: 'Momentum',
  rsi: 'RSI',
  cmf: 'CMF',
  mfm: 'MFM',
  obv: 'OBV',
  dual_ma: 'Dual MA',
  divergence: 'Divergence',
  grid: 'Grid'
};

// Time Range Configuration - matches legacy exactly
const TIME_RANGES = ['1D', '6M', 'YTD', '1Y', '5Y', 'All'] as const;
type TimeRangeValue = typeof TIME_RANGES[number];

const timeRangeMap: Record<TimeRangeValue, { interval: string; period: string; chartType: 'intraday' | 'kline'; visibleBars: number }> = {
  '1D': { interval: '1m', period: '1d', chartType: 'intraday', visibleBars: 240 },
  '6M': { interval: '1d', period: 'max', chartType: 'kline', visibleBars: 120 },
  'YTD': { interval: '1d', period: 'max', chartType: 'kline', visibleBars: -1 },
  '1Y': { interval: '1d', period: 'max', chartType: 'kline', visibleBars: 250 },
  '5Y': { interval: '1wk', period: 'max', chartType: 'kline', visibleBars: 260 },
  'All': { interval: '1wk', period: 'max', chartType: 'kline', visibleBars: -1 },
};

export default function App() {
  // State
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [currentStock, setCurrentStockState] = useState<Stock | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState<Stock[]>([]);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  const [topGainers, setTopGainers] = useState<TopPick[]>([]);
  const [topLosers, setTopLosers] = useState<TopPick[]>([]);
  const [timeRange, setTimeRange] = useState<TimeRangeValue>('1Y');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generatingSingle, setGeneratingSingle] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [overlayMessage, setOverlayMessage] = useState('');
  const [overlayLogs, setOverlayLogs] = useState<string[]>([]);
  const [overlayError, setOverlayError] = useState(false);
  const [priceData, setPriceData] = useState<HistoricalResponse | null>(null);
  const [scoreData, setScoreData] = useState<ScoreData | null>(null);
  const [lastUpdateTime, setLastUpdateTime] = useState<string>('--');
  const [chartData, setChartData] = useState<DataPoint[]>([]);
  const [metricsInitialized, setMetricsInitialized] = useState(false);

  // Cached data for different time ranges
  const cachedDailyData = useRef<HistoricalResponse | null>(null);

  // Chart Refs
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const cmfChartContainerRef = useRef<HTMLDivElement>(null);
  const cmfChartRef = useRef<IChartApi | null>(null);
  const obvChartContainerRef = useRef<HTMLDivElement>(null);
  const obvChartRef = useRef<IChartApi | null>(null);

  // Company context for GlobalNav
  const companyContext: GlobalNavProps['companyContext'] = useMemo(() => {
    if (!currentStock) return undefined;
    return {
      id: String(currentStock.id || currentStock.symbol),
      name: currentStock.name,
    };
  }, [currentStock]);

  // Set current stock and reset metrics
  const setCurrentStock = useCallback((stock: Stock | null) => {
    if (stock) {
      logger.action('Stock Selected', { symbol: stock.symbol, component: 'StockSelector' });
    }
    setCurrentStockState(stock);
    setMetricsInitialized(false);
    setPriceData(null);
    setScoreData(null);
    cachedDailyData.current = null;
    // Clear suggestions first, then update search term
    setSuggestions([]);
    setActiveSuggestionIndex(-1);
    if (stock) {
      setSearchTerm(stock.name || stock.symbol);
    }
  }, []);

  // Load Stock List on mount
  useEffect(() => {
    const loadStockList = async () => {
      logger.info('Loading stock list...');
      try {
        const response = await ApiService.apiStocksListRetrieve();
        logger.debug('Stock list response', response);
        if (response.success && response.stocks) {
          const stockList = response.stocks as Stock[];
          setStocks(stockList);
          logger.info(`Loaded ${stockList.length} stocks`);

          // Check URL params
          const params = new URLSearchParams(window.location.search);
          const symbol = params.get('symbol');
          const company = params.get('company');

          if (symbol) {
            const found = stockList.find(s => s.symbol === symbol);
            if (found) {
              setCurrentStock(found);
              logger.info(`Selected stock from URL: ${symbol}`);
            } else if (company) {
              setCurrentStock({ symbol, name: decodeURIComponent(company) });
            }
          } else if (stockList.length > 0) {
            // Default to first stock
            setCurrentStock(stockList[0]);
            logger.info(`Default stock selected: ${stockList[0].symbol}`);
          }
        } else {
          logger.warn('Stock list response unsuccessful', response);
        }
      } catch (err) {
        logger.error('Failed to load stocks', err);
      }
    };

    loadStockList();
    loadTopPicks();
  }, [setCurrentStock]);

  const loadTopPicks = async () => {
    logger.info('Loading top picks...');
    try {
      const [gainersRes, losersRes] = await Promise.all([
        ApiService.apiStocksTopPicksFastRetrieve('buy', 5),
        ApiService.apiStocksTopPicksFastRetrieve('sell', 5)
      ]);

      logger.debug('Top picks response', { gainers: gainersRes, losers: losersRes });

      // The API returns 'picks' field
      if (gainersRes.success && gainersRes.picks) {
        setTopGainers(gainersRes.picks as TopPick[]);
        logger.info(`Loaded ${gainersRes.picks.length} top gainers`);
      }
      if (losersRes.success && losersRes.picks) {
        setTopLosers(losersRes.picks as TopPick[]);
        logger.info(`Loaded ${losersRes.picks.length} top losers`);
      }
    } catch (e) {
      logger.error("Failed to load top picks", e);
    }
  };

  // Search Logic
  useEffect(() => {
    if (!searchTerm.trim()) {
      setSuggestions([]);
      return;
    }

    // Don't show suggestions if search term exactly matches current stock
    if (currentStock) {
      const termLower = searchTerm.toLowerCase().trim();
      const nameMatch = currentStock.name?.toLowerCase() === termLower;
      const symbolMatch = currentStock.symbol?.toLowerCase() === termLower;
      if (nameMatch || symbolMatch) {
        setSuggestions([]);
        return;
      }
    }

    const lower = searchTerm.toLowerCase();
    const matches = stocks.filter(s =>
      s.symbol.toLowerCase().includes(lower) ||
      s.name.toLowerCase().includes(lower)
    ).slice(0, 10);
    setSuggestions(matches);
  }, [searchTerm, stocks, currentStock]);

  // Load Chart Data using ApiService
  useEffect(() => {
    if (!currentStock) return;

    const loadData = async () => {
      setLoading(true);
      setError(null);

      const config = timeRangeMap[timeRange];
      const isIntraday = config.chartType === 'intraday';

      logger.info(`Loading chart data for ${currentStock.symbol}`, { timeRange, chartType: config.chartType, symbol: currentStock.symbol });
      const endTimer = logger.time(`API: ${config.chartType} data for ${currentStock.symbol}`);

      try {
        let apiResponse: unknown;

        if (isIntraday) {
          // Use generated ApiService for intraday data
          apiResponse = await ApiService.apiStocksIntradayRetrieve(currentStock.symbol);
        } else {
          // Calculate days based on time range
          let days = 3650; // Default for 'All'
          if (timeRange === '6M') days = 180;
          else if (timeRange === 'YTD') {
            const now = new Date();
            const startOfYear = new Date(now.getFullYear(), 0, 1);
            days = Math.ceil((now.getTime() - startOfYear.getTime()) / (1000 * 60 * 60 * 24));
          }
          else if (timeRange === '1Y') days = 365;
          else if (timeRange === '5Y') days = 1825;

          // Use generated ApiService for historical data
          apiResponse = await ApiService.apiStocksHistoricalRetrieve(
            currentStock.symbol,
            days,
            config.interval,
            config.period
          );
        }

        const duration = endTimer();

        // Cast to our extended interface that handles both field names
        // Note: OpenAPI schema says 'data', but backend actually returns 'data_points'
        const data = apiResponse as HistoricalResponse;

        // Handle both field names: 'data_points' (actual backend) or 'data' (OpenAPI schema)
        const dataPoints = data.data_points || data.data || [];

        logger.debug('Chart data response (via ApiService)', {
          success: data.success,
          dataPointsCount: dataPoints.length,
          hasDataPoints: !!data.data_points,
          hasData: !!data.data,
          error: data.error || data.message,
          duration,
          symbol: currentStock.symbol
        });

        if (data.success && dataPoints.length > 0) {
          setChartData(dataPoints);
          setPriceData(data);
          cachedDailyData.current = data;
          logger.info(`Loaded ${dataPoints.length} data points for ${currentStock.symbol}`);

          // Extract score data
          if (data.stock_score) {
            setScoreData(data.stock_score);
            logger.debug('Score data loaded', { score: data.stock_score.total_score, action: data.stock_score.recommended_action });
          }

          // Update last update time
          updateLastUpdateTime();

          // Render charts
          renderCharts(dataPoints, isIntraday, data);
        } else {
          const errorMsg = data.error || data.message || 'No data available';
          logger.warn(`No data for ${currentStock.symbol}`, { success: data.success, errorMsg, responseKeys: Object.keys(data) });
          setError(errorMsg);
        }
      } catch (err) {
        endTimer();
        logger.error(`Failed to load chart data for ${currentStock.symbol}`, err);
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [currentStock, timeRange]);

  const updateLastUpdateTime = () => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'Asia/Shanghai',
      hour12: false
    });
    setLastUpdateTime(`${timeStr} GMT+8`);
  };

  // Chart Rendering
  const renderCharts = useCallback((dataPoints: DataPoint[], isIntraday: boolean, fullResponse: HistoricalResponse) => {
    logger.info(`Rendering charts: ${isIntraday ? 'intraday' : 'daily'} with ${dataPoints.length} points`);

    // Cleanup existing charts
    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }
    if (cmfChartRef.current) {
      cmfChartRef.current.remove();
      cmfChartRef.current = null;
    }
    if (obvChartRef.current) {
      obvChartRef.current.remove();
      obvChartRef.current = null;
    }

    // Main Price Chart
    if (!chartContainerRef.current) {
      logger.warn('Chart container ref not available');
      return;
    }

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#191919',
        fontSize: 12,
        fontFamily: 'Trebuchet MS, sans-serif'
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      grid: {
        vertLines: { visible: false },
        horzLines: { color: 'rgba(197, 203, 206, 0.4)', style: 0 }
      },
      crosshair: {
        mode: 0,
        vertLine: { color: '#758696', width: 1, style: 3, labelBackgroundColor: '#4682B4' },
        horzLine: { color: '#758696', width: 1, style: 3 }
      },
      rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
      timeScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
        timeVisible: isIntraday,
        secondsVisible: false
      },
    });

    chartRef.current = chart;

    // Convert time helper
    const toUtcSeconds = (timeStr: string): number => {
      if (timeStr.includes(' ')) {
        const [date, time] = timeStr.split(' ');
        const [year, month, day] = date.split('-').map(Number);
        const [hour, minute, second = 0] = time.split(':').map(Number);
        return Date.UTC(year, month - 1, day, hour, minute, second) / 1000;
      }
      if (timeStr.includes('-')) {
        // Date only
        const [year, month, day] = timeStr.split('-').map(Number);
        return Date.UTC(year, month - 1, day) / 1000;
      }
      // Time only
      const today = new Date();
      const [hour, minute, second = 0] = timeStr.split(':').map(Number);
      return Date.UTC(today.getFullYear(), today.getMonth(), today.getDate(), hour, minute, second) / 1000;
    };

    if (isIntraday) {
      // INTRADAY: Use BaselineSeries (like legacy)
      const previousClose = fullResponse.previous_close || dataPoints[0]?.open || 0;

      const baselineSeries = chart.addSeries(BaselineSeries, {
        baseValue: { type: 'price', price: previousClose },
        topLineColor: '#26a69a',
        topFillColor1: 'rgba(38, 166, 154, 0.28)',
        topFillColor2: 'rgba(38, 166, 154, 0.05)',
        bottomLineColor: '#ef5350',
        bottomFillColor1: 'rgba(239, 83, 80, 0.05)',
        bottomFillColor2: 'rgba(239, 83, 80, 0.28)',
        lineWidth: 2,
        lineType: LineType.Simple,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 6,
        lastValueVisible: true,
        priceLineVisible: true,
      });

      const baselineData = dataPoints.map(d => ({
        time: toUtcSeconds(d.time || d.date || '') as any,
        value: d.close
      }));

      baselineSeries.setData(baselineData);

      // Add VWAP if available
      if (dataPoints.some(d => d.vwap !== undefined)) {
        const vwapSeries = chart.addSeries(LineSeries, {
          color: '#2962FF',
          lineWidth: 2,
          title: 'VWAP'
        });

        const vwapData = dataPoints.filter(d => d.vwap !== undefined).map(d => ({
          time: toUtcSeconds(d.time || d.date || '') as any,
          value: d.vwap!
        }));

        vwapSeries.setData(vwapData);
      }

      // Setup tooltip
      setupChartTooltip(chart, baselineSeries, dataPoints, isIntraday, toUtcSeconds);

    } else {
      // DAILY/WEEKLY: Use Candlestick
      const candleSeries = chart.addSeries(CandlestickSeries, {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      });

      const candleData = dataPoints.map(d => ({
        time: toUtcSeconds(d.date || d.time || '') as any,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }));

      candleSeries.setData(candleData);

      // Add MA lines for price
      if (dataPoints.some(d => d.ma5 !== undefined)) {
        const ma5Series = chart.addSeries(LineSeries, { color: '#2962FF', lineWidth: 1, title: 'MA5' });
        const ma5Data = dataPoints.filter(d => d.ma5 !== undefined).map(d => ({
          time: toUtcSeconds(d.date || '') as any,
          value: d.ma5!
        }));
        ma5Series.setData(ma5Data);
      }

      if (dataPoints.some(d => d.ma10 !== undefined)) {
        const ma10Series = chart.addSeries(LineSeries, { color: '#FF6D00', lineWidth: 1, title: 'MA10' });
        const ma10Data = dataPoints.filter(d => d.ma10 !== undefined).map(d => ({
          time: toUtcSeconds(d.date || '') as any,
          value: d.ma10!
        }));
        ma10Series.setData(ma10Data);
      }

      // Setup tooltip
      setupChartTooltip(chart, candleSeries, dataPoints, isIntraday, toUtcSeconds);
    }

    chart.timeScale().fitContent();

    // CMF Chart (only for non-intraday)
    if (!isIntraday && cmfChartContainerRef.current && dataPoints.some(d => d.cmf !== undefined)) {
      setTimeout(() => renderCmfChart(dataPoints, toUtcSeconds), 0);
    }

    // OBV Chart (only for non-intraday)
    if (!isIntraday && obvChartContainerRef.current && dataPoints.some(d => d.obv !== undefined)) {
      setTimeout(() => renderObvChart(dataPoints, toUtcSeconds), 0);
    }

    // Resize handler
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
      if (cmfChartContainerRef.current && cmfChartRef.current) {
        cmfChartRef.current.applyOptions({ width: cmfChartContainerRef.current.clientWidth });
      }
      if (obvChartContainerRef.current && obvChartRef.current) {
        obvChartRef.current.applyOptions({ width: obvChartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const setupChartTooltip = (chart: IChartApi, series: any, dataPoints: DataPoint[], isIntraday: boolean, toUtcSeconds: (s: string) => number) => {
    const tooltip = tooltipRef.current;
    if (!tooltip) return;

    chart.subscribeCrosshairMove((param: any) => {
      if (!param.time || !param.point || param.point.x < 0 || param.point.y < 0) {
        tooltip.style.display = 'none';
        return;
      }

      const data = param.seriesData.get(series);
      if (!data) {
        tooltip.style.display = 'none';
        return;
      }

      // Find source point
      const hoveredPoint = dataPoints.find(d => {
        const t = toUtcSeconds(isIntraday ? (d.time || '') : (d.date || ''));
        return t === param.time;
      });

      const date = new Date((param.time as number) * 1000);
      const timeStr = isIntraday
        ? date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
        : date.toLocaleDateString('en-US', { timeZone: 'UTC' });

      let html = `<div class="tooltip-title">${timeStr}</div>`;
      html += '<div class="tooltip-section"><div class="tooltip-section-header">Price</div>';

      if (isIntraday) {
        html += `<div class="tooltip-metric-row"><span>Close</span><span>${formatNumber(data.value)}</span></div>`;
      } else {
        html += `<div class="tooltip-metric-row"><span>Open</span><span>${formatNumber(data.open)}</span></div>`;
        html += `<div class="tooltip-metric-row"><span>High</span><span class="tooltip-value-positive">${formatNumber(data.high)}</span></div>`;
        html += `<div class="tooltip-metric-row"><span>Low</span><span class="tooltip-value-negative">${formatNumber(data.low)}</span></div>`;
        html += `<div class="tooltip-metric-row"><span>Close</span><span>${formatNumber(data.close)}</span></div>`;
      }

      if (hoveredPoint?.volume) {
        html += '</div><div class="tooltip-section"><div class="tooltip-section-header">Volume</div>';
        html += `<div class="tooltip-metric-row"><span>Traded</span><span>${formatLargeNumber(hoveredPoint.volume)}</span></div>`;
      }

      html += '</div>';
      tooltip.innerHTML = html;
      tooltip.style.display = 'block';

      // Position tooltip
      const chartRect = chartContainerRef.current?.getBoundingClientRect();
      if (chartRect) {
        const x = param.point.x + 20;
        const y = param.point.y;
        tooltip.style.left = `${Math.min(x, chartRect.width - 200)}px`;
        tooltip.style.top = `${y}px`;
      }
    });
  };

  const renderCmfChart = (dataPoints: DataPoint[], toUtcSeconds: (s: string) => number) => {
    if (!cmfChartContainerRef.current) return;

    const cmfChart = createChart(cmfChartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#191919',
        fontSize: 11
      },
      width: cmfChartContainerRef.current.clientWidth,
      height: 200,
      grid: {
        vertLines: { visible: false },
        horzLines: { color: 'rgba(197, 203, 206, 0.4)' }
      },
      rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
      timeScale: { borderColor: 'rgba(197, 203, 206, 0.8)', visible: false },
    });

    cmfChartRef.current = cmfChart;

    const cmfSeries = cmfChart.addSeries(HistogramSeries, {
      priceFormat: { type: 'price', precision: 4, minMove: 0.0001 },
    });

    const cmfData = dataPoints.filter(d => d.cmf !== undefined).map(d => ({
      time: toUtcSeconds(d.date || '') as any,
      value: d.cmf!,
      color: d.cmf! >= 0 ? 'rgba(33, 150, 243, 0.6)' : 'rgba(239, 83, 80, 0.6)',
    }));

    cmfSeries.setData(cmfData);
    cmfChart.timeScale().fitContent();
  };

  const renderObvChart = (dataPoints: DataPoint[], toUtcSeconds: (s: string) => number) => {
    if (!obvChartContainerRef.current) return;

    const obvChart = createChart(obvChartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#191919',
        fontSize: 11
      },
      width: obvChartContainerRef.current.clientWidth,
      height: 200,
      grid: {
        vertLines: { visible: false },
        horzLines: { color: 'rgba(197, 203, 206, 0.4)' }
      },
      rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
      timeScale: { borderColor: 'rgba(197, 203, 206, 0.8)', visible: false },
    });

    obvChartRef.current = obvChart;

    const obvSeries = obvChart.addSeries(LineSeries, { color: '#2962FF', lineWidth: 2 });
    const obvData = dataPoints.filter(d => d.obv !== undefined).map(d => ({
      time: toUtcSeconds(d.date || '') as any,
      value: d.obv!,
    }));
    obvSeries.setData(obvData);

    // OBV MAs
    if (dataPoints.some(d => d.obv_ma5 !== undefined)) {
      const ma5Series = obvChart.addSeries(LineSeries, { color: '#FFAB00', lineWidth: 1 });
      const ma5Data = dataPoints.filter(d => d.obv_ma5 !== undefined).map(d => ({
        time: toUtcSeconds(d.date || '') as any,
        value: d.obv_ma5!,
      }));
      ma5Series.setData(ma5Data);
    }

    if (dataPoints.some(d => d.obv_ma10 !== undefined)) {
      const ma10Series = obvChart.addSeries(LineSeries, { color: '#00BFA5', lineWidth: 1 });
      const ma10Data = dataPoints.filter(d => d.obv_ma10 !== undefined).map(d => ({
        time: toUtcSeconds(d.date || '') as any,
        value: d.obv_ma10!,
      }));
      ma10Series.setData(ma10Data);
    }

    obvChart.timeScale().fitContent();
  };

  // Generate score for ALL stocks
  const handleGenerateAllScores = async () => {
    logger.info('Generating scores for all stocks...');
    setGenerating(true);
    try {
      const res = await ApiService.apiStocksScoreGenerateAllCreate();
      logger.debug('Generate all scores response', res);
      if (res.success) {
        logger.info('All scores generated successfully');
        await loadTopPicks();
      } else {
        logger.warn('Generate all scores failed', res);
      }
    } catch (e) {
      logger.error('Failed to generate all scores', e);
    } finally {
      setGenerating(false);
    }
  };

  // Generate score for SINGLE stock with overlay
  const handleGenerateSingleScore = async () => {
    if (!currentStock || generatingSingle) return;

    logger.info(`Generating score for ${currentStock.symbol}...`);
    setGeneratingSingle(true);
    setShowOverlay(true);
    setOverlayMessage(`Generating latest score for ${currentStock.symbol}…`);
    setOverlayLogs([]);
    setOverlayError(false);

    try {
      const res = await ApiService.apiStocksScoreGenerateCreate({ symbol: currentStock.symbol });
      logger.debug('Generate single score response', res);

      if (res.success) {
        logger.info(`Score generated successfully for ${currentStock.symbol}`);
        setOverlayMessage(`Score updated for ${currentStock.symbol}`);
        setOverlayLogs((res as any).logs || []);
        if ((res as any).score) {
          setScoreData((res as any).score);
        }
        await loadTopPicks();
      } else {
        logger.warn(`Score generation failed for ${currentStock.symbol}`, res);
        setOverlayError(true);
        setOverlayMessage(res.error || 'Unable to generate score.');
        setOverlayLogs((res as any).logs || []);
      }
    } catch (e) {
      logger.error(`Failed to generate score for ${currentStock.symbol}`, e);
      setOverlayError(true);
      setOverlayMessage('Unexpected error while generating score.');
      setOverlayLogs([(e as Error).message]);
    } finally {
      setGeneratingSingle(false);
    }
  };

  // Keyboard navigation for search
  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setSuggestions([]);
      setActiveSuggestionIndex(-1);
      return;
    }

    if (suggestions.length === 0) {
      if (e.key === 'Enter') {
        // Direct match
        const lower = searchTerm.toLowerCase().trim();
        const match = stocks.find(s =>
          s.symbol.toLowerCase() === lower || s.name.toLowerCase() === lower
        );
        if (match) {
          e.preventDefault();
          setCurrentStock(match);
          setSuggestions([]);
          setActiveSuggestionIndex(-1);
        }
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveSuggestionIndex(prev => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveSuggestionIndex(prev => Math.max(prev - 1, -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const idx = activeSuggestionIndex >= 0 ? activeSuggestionIndex : 0;
      if (suggestions[idx]) {
        setCurrentStock(suggestions[idx]);
        setSuggestions([]);
        setActiveSuggestionIndex(-1);
      }
    }
  };

  // Hide suggestions on blur
  const handleSearchBlur = () => {
    setTimeout(() => {
      setSuggestions([]);
      setActiveSuggestionIndex(-1);
    }, 200);
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchTerm('');
    setSuggestions([]);
    setActiveSuggestionIndex(-1);
  };

  // Calculate price display
  const getPriceDisplay = () => {
    if (!priceData || !priceData.success || !priceData.data_points || priceData.data_points.length === 0) {
      return { price: null, change: null, changePct: null };
    }

    const lastPoint = priceData.data_points[priceData.data_points.length - 1];
    const price = lastPoint.close;
    const open = lastPoint.open;
    const change = price - open;
    const changePct = open > 0 ? (change / open) * 100 : 0;

    return { price, change, changePct };
  };

  const { price, change, changePct } = getPriceDisplay();

  // Metrics calculation
  const getMetrics = () => {
    if (!priceData || !priceData.success || !priceData.data_points || priceData.data_points.length === 0) {
      return null;
    }

    const dataPoints = priceData.data_points;
    const lastPoint = dataPoints[dataPoints.length - 1];
    const prevPoint = dataPoints.length > 1 ? dataPoints[dataPoints.length - 2] : null;

    return {
      prevClose: prevPoint ? prevPoint.close : 0,
      open: lastPoint.open,
      dayRange: `${lastPoint.low.toFixed(2)} - ${lastPoint.high.toFixed(2)}`,
      volume: lastPoint.volume,
      high52w: priceData.price_52w_high || 0,
      low52w: priceData.price_52w_low || 0,
    };
  };

  const metrics = getMetrics();

  // Render Signal Summary Component
  const renderSignalSummary = () => {
    if (!scoreData) return null;

    const actionKey = (scoreData.recommended_action || 'hold').toLowerCase();
    const actionClass = actionKey === 'buy' ? 'is-buy' : actionKey === 'sell' ? 'is-sell' : 'is-hold';

    const components = Object.entries(scoreData.score_components || {})
      .map(([key, comp]) => ({ key, ...comp }))
      .filter(c => c.raw !== 0 || c.weighted !== 0)
      .sort((a, b) => Math.abs(b.weighted) - Math.abs(a.weighted));

    const positiveSum = components.filter(c => c.weighted > 0).reduce((s, c) => s + c.weighted, 0);
    const negativeSum = components.filter(c => c.weighted < 0).reduce((s, c) => s + Math.abs(c.weighted), 0);
    const magnitude = positiveSum + negativeSum;
    const positiveShare = magnitude > 0 ? (positiveSum / magnitude) * 100 : 0;
    const negativeShare = magnitude > 0 ? (negativeSum / magnitude) * 100 : 0;

    return (
      <section id="signalSummaryContainer" className="signal-summary-section">
        <div className={`stock-signal-progress ${actionClass}`}>
          <div className="signal-summary-grid">
            <section className="signal-overview">
              <div className="overview-metric">
                <span className="metric-label">Total score</span>
                <span className="metric-value">{scoreData.total_score?.toFixed(1) || '0.0'}</span>
              </div>
              <div className="overview-divider" role="presentation" />
              <div className="overview-metric">
                <span className="metric-label">Recommended action</span>
                <span className="metric-value action-value">{scoreData.recommended_action || 'Hold'}</span>
              </div>
            </section>

            <section className="signal-distribution" aria-label="Signal balance">
              <span className="metric-label distribution-label">Contribution balance</span>
              <div className="signal-progress-track">
                <span className="progress-axis" />
                <div className="progress-fill progress-negative" style={{ width: `${negativeShare}%` }} />
                <div className="progress-fill progress-positive" style={{ width: `${positiveShare}%` }} />
              </div>
              <div className="signal-progress-summary">
                <span className="summary-positive">Positive {positiveSum.toFixed(2)}</span>
                <span className="summary-negative">Negative -{negativeSum.toFixed(2)}</span>
              </div>
            </section>

            <section className="signal-stat-grid" aria-label="Risk parameters">
              <div className="stat-item">
                <span className="metric-label">Signal date</span>
                <span className="stat-value">{scoreData.signal_date || '--'}</span>
              </div>
              <div className="stat-item">
                <span className="metric-label">Execution window</span>
                <span className="stat-value">{scoreData.execution_date || '--'}</span>
              </div>
              <div className="stat-item">
                <span className="metric-label">Stop loss</span>
                <span className="stat-value">{scoreData.stop_loss_price?.toFixed(2) || '--'}</span>
              </div>
              <div className="stat-item">
                <span className="metric-label">Take profit</span>
                <span className="stat-value">{scoreData.take_profit_price?.toFixed(2) || '--'}</span>
              </div>
              <div className="stat-item">
                <span className="metric-label">Position sizing</span>
                <span className="stat-value">{scoreData.suggested_position_pct ? `${(scoreData.suggested_position_pct * 100).toFixed(0)}%` : '--'}</span>
              </div>
            </section>
          </div>

          <section className="signal-component-table" aria-label="Component contributions">
            <div className="component-header">
              <span className="header-name">Component</span>
              <span className="header-raw">Raw</span>
              <span className="header-weighted">Weighted</span>
            </div>
            <div className="component-body">
              {components.length > 0 ? components.map(comp => (
                <div key={comp.key} className={`component-row ${comp.weighted >= 0 ? 'is-positive' : 'is-negative'}`}>
                  <div className="component-cell component-name">
                    <span className="component-label-text">{COMPONENT_LABELS[comp.key] || comp.key}</span>
                    {comp.reasons && comp.reasons.length > 0 && (
                      <div className="component-notes">{comp.reasons.join(', ')}</div>
                    )}
                  </div>
                  <div className="component-cell component-raw">{comp.raw.toFixed(0)}</div>
                  <div className="component-cell component-weighted">{comp.weighted.toFixed(2)}</div>
                </div>
              )) : (
                <div className="component-row is-empty"><span>No component contributions recorded.</span></div>
              )}
            </div>
          </section>
        </div>
      </section>
    );
  };

  return (
    <>
      <GlobalNav companyContext={companyContext} />
      <div className="container app-shell fund-flow-app">
        <header className="page-header hero-panel">
          <h1 className="page-title">Fund Flow</h1>
          <p className="page-subtitle" id="pageSubtitle">
            Real-time liquidity, on-balance volume, and capital flow signals for Chinese stock constituents.
          </p>
        </header>

        <div className="fund-flow-layout-wrapper">
          <main className="fund-flow-main" aria-live="polite">
            {/* Search Section - ALWAYS visible (matches legacy) */}
            <section className="fund-flow-control-card app-card" aria-label="Fund flow controls" id="stockSearchSection">
              <div className="fund-flow-field app-form-field fund-flow-search-field">
                <label className="fund-flow-label app-label" htmlFor="stockSearch">Search Stocks</label>
                <div className="fund-flow-search-wrapper">
                  <input
                    id="stockSearch"
                    type="text"
                    className="app-input fund-flow-search-input"
                    placeholder="Search by name or ticker..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    onKeyDown={handleSearchKeyDown}
                    onBlur={handleSearchBlur}
                  />
                  {searchTerm && (
                    <button
                      type="button"
                      id="clearStockSearch"
                      className="fund-flow-search-clear"
                      aria-label="Clear search"
                      onClick={handleClearSearch}
                    >
                      ✕
                    </button>
                  )}
                </div>
                {suggestions.length > 0 && (
                  <div id="primaryCompanySuggestions" className="suggestions-dropdown" style={{ display: 'block' }}>
                    {suggestions.map((s, idx) => (
                      <div
                        key={s.symbol}
                        className={`suggestion-item ${idx === activeSuggestionIndex ? 'is-active' : ''}`}
                        data-index={idx}
                        onClick={() => {
                          setCurrentStock(s);
                          setSuggestions([]);
                          setActiveSuggestionIndex(-1);
                        }}
                        onMouseEnter={() => setActiveSuggestionIndex(idx)}
                      >
                        <div style={{ fontWeight: 500, color: '#111827' }}>{s.name || 'Unknown Name'}</div>
                        <div style={{ fontSize: 12, color: '#6b7280' }}>{s.symbol}{s.market ? ` • ${s.market}` : ''}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

            {/* Stock Info Banner */}
            <section id="stockInfo" className={`stock-info-banner ${currentStock ? '' : 'is-hidden'}`} aria-live="polite">
              {currentStock && (
                <>
                  <div className="stock-header-primary">
                    <div className="stock-title-stack">
                      <h1 className="stock-name-large">{currentStock.name}</h1>
                      <span className="stock-symbol-large">{currentStock.symbol}</span>
                    </div>
                  </div>

                  <div className="stock-price-primary">
                    <div className="price-left">
                      <span className="price-large">{price != null ? price.toFixed(2) : '--'}</span>
                      <span className={`change-large ${change != null && change >= 0 ? 'positive' : 'negative'}`}>
                        {change != null ? `${change >= 0 ? '+' : ''}${change.toFixed(2)}` : '--'}
                        {' '}
                        ({changePct != null ? `${changePct >= 0 ? '+' : ''}${changePct.toFixed(2)}%` : '--'})
                      </span>
                    </div>
                  </div>

                  <div className="stock-last-update">
                    <span className="last-update-label">Last update:</span>
                    <span className="last-update-time" id="lastUpdateTimeValue">{lastUpdateTime}</span>
                    <span className="last-update-data" id="lastUpdateData"></span>
                  </div>
                </>
              )}
            </section>

            {/* Generate Score for Current Stock */}
            <section className="generate-card app-card" aria-label="On-demand scoring" id="generateScoreSection">
              <div className="generate-card-copy">
                <h3>On-demand Signals</h3>
                <p>Refresh the latest scoring model for the selected company in real time.</p>
              </div>
              <button
                type="button"
                id="generateScoreButton"
                className="app-btn primary-btn"
                disabled={!currentStock || generatingSingle}
                onClick={handleGenerateSingleScore}
              >
                {generatingSingle ? 'Generating…' : 'Generate Score'}
              </button>
            </section>

            {/* Metrics Panel */}
            <section id="metricsPanel" className={`metrics-panel-inline ${metrics ? '' : 'is-hidden'}`} aria-label="Key metrics">
              <div id="metricsRow" className="metrics-grid-yf">
                {metrics && (
                  <>
                    <div className="metric-row">
                      <span className="metric-label-yf">Previous Close</span>
                      <span className="metric-value-yf">{metrics.prevClose > 0 ? metrics.prevClose.toFixed(2) : '--'}</span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label-yf">Open</span>
                      <span className="metric-value-yf">{metrics.open > 0 ? metrics.open.toFixed(2) : '--'}</span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label-yf">Day's Range</span>
                      <span className="metric-value-yf">{metrics.dayRange}</span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label-yf">52 Week Range</span>
                      <span className="metric-value-yf">
                        {metrics.low52w > 0 && metrics.high52w > 0 ? `${metrics.low52w.toFixed(2)} - ${metrics.high52w.toFixed(2)}` : '--'}
                      </span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label-yf">Volume</span>
                      <span className="metric-value-yf">{metrics.volume > 0 ? metrics.volume.toLocaleString() : '--'}</span>
                    </div>
                  </>
                )}
              </div>
            </section>

            {/* Chart Container */}
            <section id="chartContainer" className="chart-stack-clean" aria-label="Fund flow charts">
              {currentStock && (
                <>
                  {/* Time Range Selector */}
                  <div className="chart-section-clean">
                    <div className="time-range-selector">
                      {TIME_RANGES.map(range => (
                        <button
                          key={range}
                          className={`time-range-btn ${timeRange === range ? 'active' : ''}`}
                          data-range={range}
                          onClick={() => {
                            logger.action('Time Range Changed', { timeRange: range, symbol: currentStock?.symbol });
                            setTimeRange(range);
                          }}
                        >
                          {range}
                        </button>
                      ))}
                    </div>

                    <div style={{ position: 'relative' }}>
                      <div id="intradayChart" className="chart-canvas" ref={chartContainerRef}>
                        {loading && (
                          <div className="chart-panel loading-state">
                            <div className="loading-container">
                              <div className="loading-spinner" />
                              <div className="loading-text">Loading chart data...</div>
                              <div className="loading-progress-bar">
                                <div className="loading-progress-fill" id="loadingProgressFill" style={{ width: '50%' }} />
                              </div>
                              <div className="loading-hint">This may take 10-15 seconds for large datasets</div>
                            </div>
                          </div>
                        )}
                        {error && <div className="chart-panel error-state">{error}</div>}
                      </div>
                      <div id="tooltip-intraday" className="chart-tooltip" ref={tooltipRef} style={{ display: 'none' }} />
                    </div>
                  </div>

                  {/* CMF Chart */}
                  {timeRange !== '1D' && chartData.some(d => d.cmf !== undefined) && (
                    <div className="chart-section-clean indicator-chart">
                      <h3 className="indicator-title">Chaikin Money Flow (CMF)</h3>
                      <div className="chart-canvas" ref={cmfChartContainerRef} />
                    </div>
                  )}

                  {/* OBV Chart */}
                  {timeRange !== '1D' && chartData.some(d => d.obv !== undefined) && (
                    <div className="chart-section-clean indicator-chart">
                      <h3 className="indicator-title">On-Balance Volume (OBV)</h3>
                      <div className="chart-canvas" ref={obvChartContainerRef} />
                    </div>
                  )}
                </>
              )}

              {!currentStock && (
                <div className="chart-panel empty-state">Select a stock to view fund flow charts.</div>
              )}
            </section>

            {/* Signal Summary */}
            {currentStock && renderSignalSummary()}
          </main>

          {/* Sidebar */}
          <aside className="fund-flow-sidebar">
            {/* Market Actions Toolbar */}
            <div className="yf-sidebar-actions">
              <button
                id="generateScoreBtn"
                className={`yf-action-btn ${generating ? 'is-loading' : ''}`}
                aria-label="Generate Data Analysis"
                onClick={handleGenerateAllScores}
                disabled={generating}
              >
                <svg className="yf-action-icon" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
                <span className="yf-btn-text">{generating ? 'PROCESSING...' : 'GENERATE SIGNAL'}</span>
              </button>
            </div>

            {/* Top Gainers */}
            <div className="yf-card">
              <div className="yf-card-header">
                <h3 className="yf-card-title">Top Gainers</h3>
              </div>
              <div id="topGainersList" className="yf-list">
                {topGainers.length > 0 ? topGainers.map(stock => {
                  const stockPrice = stock.last_close || stock.price || 0;
                  const pct = stock.change_percent || 0;
                  return (
                    <div
                      key={stock.symbol}
                      className="yf-row"
                      onClick={() => {
                        const found = stocks.find(s => s.symbol === stock.symbol);
                        if (found) setCurrentStock(found);
                        else setCurrentStock({ symbol: stock.symbol, name: stock.name });
                      }}
                    >
                      <div className="yf-info">
                        <span className="yf-symbol">{stock.symbol}</span>
                        <span className="yf-name">{stock.name}</span>
                      </div>
                      <div className="yf-sparkline" />
                      <div className="yf-price-block">
                        <span className="yf-price">{formatNumber(stockPrice)}</span>
                        <span className={`yf-change ${pct >= 0 ? 'positive' : 'negative'}`}>
                          {pct >= 0 ? '+' : ''}{formatNumber(pct)}%
                        </span>
                      </div>
                    </div>
                  );
                }) : <div className="top-picks-loading"><p>Loading...</p></div>}
              </div>
            </div>

            {/* Top Losers */}
            <div className="yf-card">
              <div className="yf-card-header">
                <h3 className="yf-card-title">Top Losers</h3>
              </div>
              <div id="topLosersList" className="yf-list">
                {topLosers.length > 0 ? topLosers.map(stock => {
                  const stockPrice = stock.last_close || stock.price || 0;
                  const pct = stock.change_percent || 0;
                  return (
                    <div
                      key={stock.symbol}
                      className="yf-row"
                      onClick={() => {
                        const found = stocks.find(s => s.symbol === stock.symbol);
                        if (found) setCurrentStock(found);
                        else setCurrentStock({ symbol: stock.symbol, name: stock.name });
                      }}
                    >
                      <div className="yf-info">
                        <span className="yf-symbol">{stock.symbol}</span>
                        <span className="yf-name">{stock.name}</span>
                      </div>
                      <div className="yf-sparkline" />
                      <div className="yf-price-block">
                        <span className="yf-price">{formatNumber(stockPrice)}</span>
                        <span className={`yf-change ${pct >= 0 ? 'positive' : 'negative'}`}>
                          {pct >= 0 ? '+' : ''}{formatNumber(pct)}%
                        </span>
                      </div>
                    </div>
                  );
                }) : <div className="top-picks-loading"><p>Loading...</p></div>}
              </div>
            </div>
          </aside>
        </div>
      </div>

      {/* Generation Overlay Modal */}
      <div id="generationOverlay" className={`generation-overlay ${showOverlay ? '' : 'is-hidden'}`} role="dialog" aria-modal="true">
        <div className="generation-dialog">
          {!overlayError && <div className="generation-spinner" aria-hidden="true" />}
          <div className="generation-copy">
            <p className="generation-status" id="generationStatus">{overlayMessage}</p>
            {overlayLogs.length > 0 && <pre className="generation-logs" id="generationLogs">{overlayLogs.join('\n')}</pre>}
          </div>
          <button type="button" id="closeGenerationOverlay" className="app-btn ghost-btn" onClick={() => setShowOverlay(false)}>Close</button>
        </div>
      </div>
    </>
  );
}
