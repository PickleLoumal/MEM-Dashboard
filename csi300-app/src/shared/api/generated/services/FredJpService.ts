/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FredJpHealthCheckResponse } from '../models/FredJpHealthCheckResponse';
import type { FredJpLatestValue } from '../models/FredJpLatestValue';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FredJpService {
    /**
     * 日本FRED健康检查端点
     * @returns FredJpHealthCheckResponse
     * @throws ApiError
     */
    public static apiFredJpHealthRetrieve(): CancelablePromise<FredJpHealthCheckResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-jp/health/',
        });
    }
    /**
     * 日本FRED指标视图集 - 对应Flask API功能
     * @returns FredJpLatestValue
     * @throws ApiError
     */
    public static apiFredJpIndicatorsList(): CancelablePromise<Array<FredJpLatestValue>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-jp/indicators/',
        });
    }
    /**
     * 获取特定日本指标数据
     * @param indicatorName
     * @returns FredJpLatestValue
     * @throws ApiError
     */
    public static apiFredJpIndicatorsRetrieve2(
        indicatorName: string,
    ): CancelablePromise<FredJpLatestValue> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-jp/indicators/{indicator_name}/',
            path: {
                'indicator_name': indicatorName,
            },
        });
    }
    /**
     * 日本FRED指标视图集 - 对应Flask API功能
     * @param id A unique integer value identifying this Japan FRED Indicator.
     * @returns FredJpLatestValue
     * @throws ApiError
     */
    public static apiFredJpIndicatorsRetrieve(
        id: number,
    ): CancelablePromise<FredJpLatestValue> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-jp/indicators/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 日本FRED系统状态
     * @returns FredJpLatestValue
     * @throws ApiError
     */
    public static apiFredJpIndicatorsStatusRetrieve(): CancelablePromise<FredJpLatestValue> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-jp/indicators/status/',
        });
    }
    /**
     * 日本FRED系统状态
     * @returns FredJpLatestValue
     * @throws ApiError
     */
    public static apiFredJpStatusRetrieve(): CancelablePromise<FredJpLatestValue> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-jp/status/',
        });
    }
}
