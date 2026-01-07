/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiOverviewResponse } from '../models/ApiOverviewResponse';
import type { GlobalHealthCheckResponse } from '../models/GlobalHealthCheckResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ApiService {
    /**
     * API概览 - 所有可用端点
     * @returns ApiOverviewResponse
     * @throws ApiError
     */
    public static apiRetrieve(): CancelablePromise<ApiOverviewResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/',
        });
    }
    /**
     * 全局健康检查端点 - 前端和Docker健康检查使用
     * @returns GlobalHealthCheckResponse
     * @throws ApiError
     */
    public static apiHealthRetrieve(): CancelablePromise<GlobalHealthCheckResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/health/',
        });
    }
}
