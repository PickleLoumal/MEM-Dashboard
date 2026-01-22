/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Company } from '../models/Company';
import type { CSI300HealthCheckResponse } from '../models/CSI300HealthCheckResponse';
import type { CSI300IndexResponse } from '../models/CSI300IndexResponse';
import type { FilterOptions } from '../models/FilterOptions';
import type { GenerateInvestmentSummaryRequest } from '../models/GenerateInvestmentSummaryRequest';
import type { GenerateSummaryRequest } from '../models/GenerateSummaryRequest';
import type { GenerationTaskStartResponse } from '../models/GenerationTaskStartResponse';
import type { GenerationTaskStatusResponse } from '../models/GenerationTaskStatusResponse';
import type { InvestmentSummary } from '../models/InvestmentSummary';
import type { PaginatedCompanyListList } from '../models/PaginatedCompanyListList';
import type { PeerComparisonResponse } from '../models/PeerComparisonResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class Csi300Service {
    /**
     * CSI300 API 索引端点 (向后兼容)
     * @returns CSI300IndexResponse
     * @throws ApiError
     */
    public static apiCsi300Retrieve(): CancelablePromise<CSI300IndexResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/',
        });
    }
    /**
     * 获取公司列表或 API 概览
     * @param exchange Filter by exchange (SSE, SZSE, HKEX)
     * @param gicsIndustry Filter by GICS industry (partial match)
     * @param imSector Filter by Industry Matrix sector
     * @param industry Filter by industry name
     * @param industrySearch Search by industry name (partial match)
     * @param marketCapMax Maximum market cap filter
     * @param marketCapMin Minimum market cap filter
     * @param page A page number within the paginated result set.
     * @param pageSize Number of results to return per page.
     * @param region Filter by region (legacy, prefer using 'exchange')
     * @param search Search by company name or ticker
     * @returns PaginatedCompanyListList
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesList(
        exchange?: 'HKEX' | 'SSE' | 'SZSE',
        gicsIndustry?: string,
        imSector?: string,
        industry?: string,
        industrySearch?: string,
        marketCapMax?: number,
        marketCapMin?: number,
        page?: number,
        pageSize?: number,
        region?: string,
        search?: string,
    ): CancelablePromise<PaginatedCompanyListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/',
            query: {
                'exchange': exchange,
                'gics_industry': gicsIndustry,
                'im_sector': imSector,
                'industry': industry,
                'industry_search': industrySearch,
                'market_cap_max': marketCapMax,
                'market_cap_min': marketCapMin,
                'page': page,
                'page_size': pageSize,
                'region': region,
                'search': search,
            },
        });
    }
    /**
     * 获取单个公司详情
     * @param id A unique integer value identifying this Company.
     * @returns Company
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesRetrieve(
        id: number,
    ): CancelablePromise<Company> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 获取同行业公司对比数据
     * @param id A unique integer value identifying this Company.
     * @returns PeerComparisonResponse
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesIndustryPeersComparisonRetrieve(
        id: number,
    ): CancelablePromise<PeerComparisonResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/{id}/industry_peers_comparison/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 获取公司投资摘要
     * @param id A unique integer value identifying this Company.
     * @returns InvestmentSummary
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesInvestmentSummaryRetrieve(
        id: number,
    ): CancelablePromise<InvestmentSummary> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/{id}/investment_summary/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 获取可用的筛选选项
     * @param exchange
     * @param imSector
     * @param region
     * @returns FilterOptions
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesFilterOptionsRetrieve(
        exchange?: 'HKEX' | 'SSE' | 'SZSE',
        imSector?: string,
        region?: string,
    ): CancelablePromise<FilterOptions> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/filter_options/',
            query: {
                'exchange': exchange,
                'im_sector': imSector,
                'region': region,
            },
        });
    }
    /**
     * 异步启动 Investment Summary 生成任务。立即返回 task_id，前端可通过 task-status API 轮询进度。
     * @param requestBody
     * @returns GenerationTaskStartResponse
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesGenerateSummaryCreate(
        requestBody: GenerateSummaryRequest,
    ): CancelablePromise<GenerationTaskStartResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/csi300/api/companies/generate-summary/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 健康检查端点
     * @returns Company
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesHealthRetrieve(): CancelablePromise<Company> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/health/',
        });
    }
    /**
     * 搜索公司
     * @param q
     * @param exchange
     * @param page A page number within the paginated result set.
     * @param pageSize Number of results to return per page.
     * @returns PaginatedCompanyListList
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesSearchList(
        q: string,
        exchange?: 'HKEX' | 'SSE' | 'SZSE',
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedCompanyListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/search/',
            query: {
                'exchange': exchange,
                'page': page,
                'page_size': pageSize,
                'q': q,
            },
        });
    }
    /**
     * 查询异步生成任务的状态和进度。前端轮询此 API 获取生成进度。
     * @param taskId 任务 UUID
     * @returns GenerationTaskStatusResponse
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesTaskStatusRetrieve(
        taskId: string,
    ): CancelablePromise<GenerationTaskStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/task-status/{task_id}/',
            path: {
                'task_id': taskId,
            },
        });
    }
    /**
     * 异步启动 Investment Summary 生成任务 (向后兼容端点)
     * @param requestBody
     * @returns GenerationTaskStartResponse
     * @throws ApiError
     */
    public static apiCsi300ApiGenerateSummaryCreate(
        requestBody: GenerateInvestmentSummaryRequest,
    ): CancelablePromise<GenerationTaskStartResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/csi300/api/generate-summary/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 查询任务状态
     * 查询异步生成任务的状态和进度 (向后兼容端点)
     * @param taskId 任务 UUID
     * @returns GenerationTaskStatusResponse
     * @throws ApiError
     */
    public static apiCsi300ApiTaskStatusRetrieve(
        taskId: string,
    ): CancelablePromise<GenerationTaskStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/task-status/{task_id}/',
            path: {
                'task_id': taskId,
            },
        });
    }
    /**
     * CSI300 API 健康检查端点 (向后兼容)
     * @returns CSI300HealthCheckResponse
     * @throws ApiError
     */
    public static apiCsi300HealthRetrieve(): CancelablePromise<CSI300HealthCheckResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/health/',
        });
    }
}
