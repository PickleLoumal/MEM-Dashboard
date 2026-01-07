/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FundFlowPageResponse } from '../models/FundFlowPageResponse';
import type { GenerateAllScoresResponse } from '../models/GenerateAllScoresResponse';
import type { GenerateStockScoreRequest } from '../models/GenerateStockScoreRequest';
import type { GenerateStockScoreResponse } from '../models/GenerateStockScoreResponse';
import type { HistoricalDataResponse } from '../models/HistoricalDataResponse';
import type { IntradayDataResponse } from '../models/IntradayDataResponse';
import type { LightweightChartResponse } from '../models/LightweightChartResponse';
import type { StockListResponse } from '../models/StockListResponse';
import type { TopPicksResponse } from '../models/TopPicksResponse';
import type { TopPicksWithSparklinesResponse } from '../models/TopPicksWithSparklinesResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StocksService {
    /**
     * 生成TradingView Lightweight Charts图表
     * 使用lightweight-charts-python库（仿照Databento示例）
     * @param symbol Stock ticker symbol
     * @param type Chart type: intraday, cmf, obv
     * @returns LightweightChartResponse
     * @throws ApiError
     */
    public static apiStocksChartLightweightRetrieve(
        symbol: string,
        type?: string,
    ): CancelablePromise<LightweightChartResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stocks/chart/lightweight/',
            query: {
                'symbol': symbol,
                'type': type,
            },
        });
    }
    /**
     * Fund Flow页面 - 重定向到现有的HTML页面
     * @returns FundFlowPageResponse
     * @throws ApiError
     */
    public static apiStocksFundFlowRetrieve(): CancelablePromise<FundFlowPageResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stocks/fund-flow/',
        });
    }
    /**
     * 获取历史数据（支持不同时间间隔的K线数据）
     * @param symbol Stock ticker symbol
     * @param days Number of days
     * @param interval Data interval
     * @param period YFinance period
     * @returns HistoricalDataResponse
     * @throws ApiError
     */
    public static apiStocksHistoricalRetrieve(
        symbol: string,
        days?: number,
        interval?: string,
        period?: string,
    ): CancelablePromise<HistoricalDataResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stocks/historical/',
            query: {
                'days': days,
                'interval': interval,
                'period': period,
                'symbol': symbol,
            },
        });
    }
    /**
     * 获取分时数据（1分钟K线）
     * @param symbol Stock ticker symbol
     * @returns IntradayDataResponse
     * @throws ApiError
     */
    public static apiStocksIntradayRetrieve(
        symbol: string,
    ): CancelablePromise<IntradayDataResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stocks/intraday/',
            query: {
                'symbol': symbol,
            },
        });
    }
    /**
     * 获取股票列表 - 从CSI300 Company表读取
     * @returns StockListResponse
     * @throws ApiError
     */
    public static apiStocksListRetrieve(): CancelablePromise<StockListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stocks/list/',
        });
    }
    /**
     * Trigger a lightweight scoring run for a single ticker.
     * @param requestBody
     * @returns GenerateStockScoreResponse
     * @throws ApiError
     */
    public static apiStocksScoreGenerateCreate(
        requestBody: GenerateStockScoreRequest,
    ): CancelablePromise<GenerateStockScoreResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/stocks/score/generate/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Trigger scoring calculation for all stocks.
     * @returns GenerateAllScoresResponse
     * @throws ApiError
     */
    public static apiStocksScoreGenerateAllCreate(): CancelablePromise<GenerateAllScoresResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/stocks/score/generate-all/',
        });
    }
    /**
     * Return today's top scoring stocks to power the dashboard cards.
     * @param direction buy or sell
     * @param limit Number of results
     * @returns TopPicksResponse
     * @throws ApiError
     */
    public static apiStocksTopPicksRetrieve(
        direction?: string,
        limit?: number,
    ): CancelablePromise<TopPicksResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stocks/top-picks/',
            query: {
                'direction': direction,
                'limit': limit,
            },
        });
    }
    /**
     * Optimized endpoint: returns top picks WITH sparkline data in one request.
     * Reduces frontend API calls from 10+ to 1.
     * @param direction buy or sell
     * @param limit Number of results
     * @returns TopPicksWithSparklinesResponse
     * @throws ApiError
     */
    public static apiStocksTopPicksFastRetrieve(
        direction?: string,
        limit?: number,
    ): CancelablePromise<TopPicksWithSparklinesResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stocks/top-picks-fast/',
            query: {
                'direction': direction,
                'limit': limit,
            },
        });
    }
}
