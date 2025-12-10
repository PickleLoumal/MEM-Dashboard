/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FinancialContext } from '../models/FinancialContext';
import type { RefinitivConnectionStatus } from '../models/RefinitivConnectionStatus';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RefinitivService {
    /**
     * 获取公司财务数据
     * 从 Refinitiv 获取指定公司的完整财务数据，用于 Investment Summary 生成。
     * @param ric Reuters Instrument Code (e.g., 0425.SZ for XCMG)
     * @returns FinancialContext
     * @throws ApiError
     */
    public static apiRefinitivFinancialDataRetrieve(
        ric: string,
    ): CancelablePromise<FinancialContext> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/refinitiv/financial-data/',
            query: {
                'ric': ric,
            },
        });
    }
    /**
     * 搜索股票代码
     * 通过公司名称或代码搜索 Refinitiv 股票代码 (RIC)。
     * @param query 搜索关键词 (e.g., 'XCMG', 'construction machinery')
     * @param limit 最大返回数量
     * @returns FinancialContext
     * @throws ApiError
     */
    public static apiRefinitivSearchRetrieve(
        query: string,
        limit: number = 10,
    ): CancelablePromise<FinancialContext> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/refinitiv/search/',
            query: {
                'limit': limit,
                'query': query,
            },
        });
    }
    /**
     * 测试 Refinitiv 连接
     * 测试与 Refinitiv Data Platform 的连接状态。
     * @returns RefinitivConnectionStatus
     * @throws ApiError
     */
    public static apiRefinitivStatusRetrieve(): CancelablePromise<RefinitivConnectionStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/refinitiv/status/',
        });
    }
}
