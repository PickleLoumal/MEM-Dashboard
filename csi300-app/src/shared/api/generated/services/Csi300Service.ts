/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CSI300Company } from '../models/CSI300Company';
import type { CSI300FilterOptions } from '../models/CSI300FilterOptions';
import type { CSI300HealthCheckResponse } from '../models/CSI300HealthCheckResponse';
import type { CSI300IndexResponse } from '../models/CSI300IndexResponse';
import type { CSI300InvestmentSummary } from '../models/CSI300InvestmentSummary';
import type { CSI300PeerComparisonResponse } from '../models/CSI300PeerComparisonResponse';
import type { GenerateInvestmentSummaryRequest } from '../models/GenerateInvestmentSummaryRequest';
import type { GenerateInvestmentSummaryResponse } from '../models/GenerateInvestmentSummaryResponse';
import type { PaginatedCSI300CompanyListList } from '../models/PaginatedCSI300CompanyListList';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class Csi300Service {
    /**
     * CSI300 API 索引端点 (向后兼容)
     * @returns CSI300IndexResponse
     * @throws ApiError
     */
    public static csi300Retrieve(): CancelablePromise<CSI300IndexResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/',
        });
    }
    /**
     * 获取公司列表或 API 概览
     * @param page A page number within the paginated result set.
     * @param pageSize Number of results to return per page.
     * @returns PaginatedCSI300CompanyListList
     * @throws ApiError
     */
    public static csi300ApiCompaniesList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedCSI300CompanyListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/api/companies/',
            query: {
                'page': page,
                'page_size': pageSize,
            },
        });
    }
    /**
     * 获取单个公司详情
     * @param id A unique integer value identifying this CSI300 Company.
     * @returns CSI300Company
     * @throws ApiError
     */
    public static csi300ApiCompaniesRetrieve(
        id: number,
    ): CancelablePromise<CSI300Company> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/api/companies/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 获取同行业公司对比数据
     * @param id A unique integer value identifying this CSI300 Company.
     * @returns CSI300PeerComparisonResponse
     * @throws ApiError
     */
    public static csi300ApiCompaniesIndustryPeersComparisonRetrieve(
        id: number,
    ): CancelablePromise<CSI300PeerComparisonResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/api/companies/{id}/industry_peers_comparison/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 获取公司投资摘要
     * @param id A unique integer value identifying this CSI300 Company.
     * @returns CSI300InvestmentSummary
     * @throws ApiError
     */
    public static csi300ApiCompaniesInvestmentSummaryRetrieve(
        id: number,
    ): CancelablePromise<CSI300InvestmentSummary> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/api/companies/{id}/investment_summary/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 获取可用的筛选选项
     * @param imSector
     * @param region
     * @returns CSI300FilterOptions
     * @throws ApiError
     */
    public static csi300ApiCompaniesFilterOptionsRetrieve(
        imSector?: string,
        region?: string,
    ): CancelablePromise<CSI300FilterOptions> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/api/companies/filter_options/',
            query: {
                'im_sector': imSector,
                'region': region,
            },
        });
    }
    /**
     * 生成指定公司的 Investment Summary
     *
     * 使用 AI 模型生成公司投资摘要并保存到数据库。
     * @param requestBody
     * @returns CSI300Company
     * @throws ApiError
     */
    public static csi300ApiCompaniesGenerateSummaryCreate(
        requestBody: CSI300Company,
    ): CancelablePromise<CSI300Company> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/csi300/api/companies/generate-summary/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 健康检查端点
     * @returns CSI300Company
     * @throws ApiError
     */
    public static csi300ApiCompaniesHealthRetrieve(): CancelablePromise<CSI300Company> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/api/companies/health/',
        });
    }
    /**
     * 搜索公司
     * @param q
     * @param page A page number within the paginated result set.
     * @param pageSize Number of results to return per page.
     * @returns PaginatedCSI300CompanyListList
     * @throws ApiError
     */
    public static csi300ApiCompaniesSearchList(
        q: string,
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedCSI300CompanyListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/api/companies/search/',
            query: {
                'page': page,
                'page_size': pageSize,
                'q': q,
            },
        });
    }
    /**
     * 生成指定公司的 Investment Summary (向后兼容)
     * @param requestBody
     * @returns GenerateInvestmentSummaryResponse
     * @throws ApiError
     */
    public static csi300ApiGenerateSummaryCreate(
        requestBody: GenerateInvestmentSummaryRequest,
    ): CancelablePromise<GenerateInvestmentSummaryResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/csi300/api/generate-summary/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * CSI300 API 健康检查端点 (向后兼容)
     * @returns CSI300HealthCheckResponse
     * @throws ApiError
     */
    public static csi300HealthRetrieve(): CancelablePromise<CSI300HealthCheckResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/health/',
        });
    }
}
