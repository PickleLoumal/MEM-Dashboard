/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiOverviewResponse } from '../models/ApiOverviewResponse';
import type { BeaAllIndicatorsResponse } from '../models/BeaAllIndicatorsResponse';
import type { BeaCategoryIndicatorsResponse } from '../models/BeaCategoryIndicatorsResponse';
import type { BeaConfigCreate } from '../models/BeaConfigCreate';
import type { BeaConfigUpdate } from '../models/BeaConfigUpdate';
import type { BeaDynamicIndicatorResponse } from '../models/BeaDynamicIndicatorResponse';
import type { BeaIndexResponse } from '../models/BeaIndexResponse';
import type { BeaIndicator } from '../models/BeaIndicator';
import type { BeaIndicatorConfig } from '../models/BeaIndicatorConfig';
import type { BeaInvestmentResponse } from '../models/BeaInvestmentResponse';
import type { BeaStatsResponse } from '../models/BeaStatsResponse';
import type { ContentCategory } from '../models/ContentCategory';
import type { CSI300Company } from '../models/CSI300Company';
import type { CSI300FilterOptions } from '../models/CSI300FilterOptions';
import type { CSI300HealthCheckResponse } from '../models/CSI300HealthCheckResponse';
import type { CSI300IndexResponse } from '../models/CSI300IndexResponse';
import type { CSI300InvestmentSummary } from '../models/CSI300InvestmentSummary';
import type { CSI300PeerComparisonResponse } from '../models/CSI300PeerComparisonResponse';
import type { FredJpHealthCheckResponse } from '../models/FredJpHealthCheckResponse';
import type { FredJpLatestValue } from '../models/FredJpLatestValue';
import type { FredUsIndicatorResponse } from '../models/FredUsIndicatorResponse';
import type { FundFlowPageResponse } from '../models/FundFlowPageResponse';
import type { GenerateAllScoresResponse } from '../models/GenerateAllScoresResponse';
import type { GenerateInvestmentSummaryRequest } from '../models/GenerateInvestmentSummaryRequest';
import type { GenerateStockScoreRequest } from '../models/GenerateStockScoreRequest';
import type { GenerateStockScoreResponse } from '../models/GenerateStockScoreResponse';
import type { GenerateSummaryRequest } from '../models/GenerateSummaryRequest';
import type { GenerationTaskStartResponse } from '../models/GenerationTaskStartResponse';
import type { GenerationTaskStatusResponse } from '../models/GenerationTaskStatusResponse';
import type { GlobalHealthCheckResponse } from '../models/GlobalHealthCheckResponse';
import type { HistoricalDataResponse } from '../models/HistoricalDataResponse';
import type { IntradayDataResponse } from '../models/IntradayDataResponse';
import type { LightweightChartResponse } from '../models/LightweightChartResponse';
import type { ModalContent } from '../models/ModalContent';
import type { PaginatedCSI300CompanyListList } from '../models/PaginatedCSI300CompanyListList';
import type { PatchedBeaConfigUpdate } from '../models/PatchedBeaConfigUpdate';
import type { PatchedBeaIndicator } from '../models/PatchedBeaIndicator';
import type { PDFDownloadResponse } from '../models/PDFDownloadResponse';
import type { PDFRequest } from '../models/PDFRequest';
import type { PDFTask } from '../models/PDFTask';
import type { PDFTaskCreateResponse } from '../models/PDFTaskCreateResponse';
import type { PDFTemplate } from '../models/PDFTemplate';
import type { PDFTemplateDetail } from '../models/PDFTemplateDetail';
import type { PolicyUpdatesResponse } from '../models/PolicyUpdatesResponse';
import type { StockListResponse } from '../models/StockListResponse';
import type { TopPicksResponse } from '../models/TopPicksResponse';
import type { TopPicksWithSparklinesResponse } from '../models/TopPicksWithSparklinesResponse';
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
     * BEA API首页 - 动态端点列表
     * @returns BeaIndexResponse
     * @throws ApiError
     */
    public static apiBeaRetrieve(): CancelablePromise<BeaIndexResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/',
        });
    }
    /**
     * 获取所有指标数据 - 动态处理
     * @returns BeaAllIndicatorsResponse
     * @throws ApiError
     */
    public static apiBeaAllIndicatorsRetrieve(): CancelablePromise<BeaAllIndicatorsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/all_indicators/',
        });
    }
    /**
     * BEA指标配置ViewSet - 动态配置管理
     * @returns BeaIndicatorConfig
     * @throws ApiError
     */
    public static apiBeaApiConfigsList(): CancelablePromise<Array<BeaIndicatorConfig>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/api/configs/',
        });
    }
    /**
     * BEA指标配置ViewSet - 动态配置管理
     * @param requestBody
     * @returns BeaConfigCreate
     * @throws ApiError
     */
    public static apiBeaApiConfigsCreate(
        requestBody: BeaConfigCreate,
    ): CancelablePromise<BeaConfigCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/bea/api/configs/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * BEA指标配置ViewSet - 动态配置管理
     * @param id A unique integer value identifying this bea indicator config.
     * @returns BeaIndicatorConfig
     * @throws ApiError
     */
    public static apiBeaApiConfigsRetrieve(
        id: number,
    ): CancelablePromise<BeaIndicatorConfig> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/api/configs/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * BEA指标配置ViewSet - 动态配置管理
     * @param id A unique integer value identifying this bea indicator config.
     * @param requestBody
     * @returns BeaConfigUpdate
     * @throws ApiError
     */
    public static apiBeaApiConfigsUpdate(
        id: number,
        requestBody: BeaConfigUpdate,
    ): CancelablePromise<BeaConfigUpdate> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/bea/api/configs/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * BEA指标配置ViewSet - 动态配置管理
     * @param id A unique integer value identifying this bea indicator config.
     * @param requestBody
     * @returns BeaConfigUpdate
     * @throws ApiError
     */
    public static apiBeaApiConfigsPartialUpdate(
        id: number,
        requestBody?: PatchedBeaConfigUpdate,
    ): CancelablePromise<BeaConfigUpdate> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/bea/api/configs/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * BEA指标配置ViewSet - 动态配置管理
     * @param id A unique integer value identifying this bea indicator config.
     * @returns void
     * @throws ApiError
     */
    public static apiBeaApiConfigsDestroy(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/bea/api/configs/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 激活指标配置
     * @param id A unique integer value identifying this bea indicator config.
     * @param requestBody
     * @returns BeaIndicatorConfig
     * @throws ApiError
     */
    public static apiBeaApiConfigsActivateCreate(
        id: number,
        requestBody: BeaIndicatorConfig,
    ): CancelablePromise<BeaIndicatorConfig> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/bea/api/configs/{id}/activate/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 停用指标配置
     * @param id A unique integer value identifying this bea indicator config.
     * @param requestBody
     * @returns BeaIndicatorConfig
     * @throws ApiError
     */
    public static apiBeaApiConfigsDeactivateCreate(
        id: number,
        requestBody: BeaIndicatorConfig,
    ): CancelablePromise<BeaIndicatorConfig> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/bea/api/configs/{id}/deactivate/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 获取所有激活的配置
     * @returns BeaIndicatorConfig
     * @throws ApiError
     */
    public static apiBeaApiConfigsActiveRetrieve(): CancelablePromise<BeaIndicatorConfig> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/api/configs/active/',
        });
    }
    /**
     * 获取所有指标分类
     * @returns BeaIndicatorConfig
     * @throws ApiError
     */
    public static apiBeaApiConfigsCategoriesRetrieve(): CancelablePromise<BeaIndicatorConfig> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/api/configs/categories/',
        });
    }
    /**
     * BEA指标数据ViewSet - 支持CRUD操作
     * @returns BeaIndicator
     * @throws ApiError
     */
    public static apiBeaApiDataList(): CancelablePromise<Array<BeaIndicator>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/api/data/',
        });
    }
    /**
     * BEA指标数据ViewSet - 支持CRUD操作
     * @param requestBody
     * @returns BeaIndicator
     * @throws ApiError
     */
    public static apiBeaApiDataCreate(
        requestBody: BeaIndicator,
    ): CancelablePromise<BeaIndicator> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/bea/api/data/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * BEA指标数据ViewSet - 支持CRUD操作
     * @param id A unique integer value identifying this bea indicator.
     * @returns BeaIndicator
     * @throws ApiError
     */
    public static apiBeaApiDataRetrieve(
        id: number,
    ): CancelablePromise<BeaIndicator> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/api/data/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * BEA指标数据ViewSet - 支持CRUD操作
     * @param id A unique integer value identifying this bea indicator.
     * @param requestBody
     * @returns BeaIndicator
     * @throws ApiError
     */
    public static apiBeaApiDataUpdate(
        id: number,
        requestBody: BeaIndicator,
    ): CancelablePromise<BeaIndicator> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/bea/api/data/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * BEA指标数据ViewSet - 支持CRUD操作
     * @param id A unique integer value identifying this bea indicator.
     * @param requestBody
     * @returns BeaIndicator
     * @throws ApiError
     */
    public static apiBeaApiDataPartialUpdate(
        id: number,
        requestBody?: PatchedBeaIndicator,
    ): CancelablePromise<BeaIndicator> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/bea/api/data/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * BEA指标数据ViewSet - 支持CRUD操作
     * @param id A unique integer value identifying this bea indicator.
     * @returns void
     * @throws ApiError
     */
    public static apiBeaApiDataDestroy(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/bea/api/data/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 按分类获取指标数据
     * @param category Category name
     * @returns BeaCategoryIndicatorsResponse
     * @throws ApiError
     */
    public static apiBeaCategoryRetrieve(
        category: string,
    ): CancelablePromise<BeaCategoryIndicatorsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/category/{category}/',
            path: {
                'category': category,
            },
        });
    }
    /**
     * Gross Government Investment - GET /bea/govt-investment-total/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaGovtInvestmentTotalRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/govt-investment-total/',
        });
    }
    /**
     * 动态指标端点 - 根据series_id获取数据
     * @param seriesId Series ID
     * @param quarterly Include quarterly data
     * @returns BeaDynamicIndicatorResponse
     * @throws ApiError
     */
    public static apiBeaIndicatorRetrieve(
        seriesId: string,
        quarterly?: boolean,
    ): CancelablePromise<BeaDynamicIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/indicator/{series_id}/',
            path: {
                'series_id': seriesId,
            },
            query: {
                'quarterly': quarterly,
            },
        });
    }
    /**
     * Equipment Investment - GET /bea/investment-equipment/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentEquipmentRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-equipment/',
        });
    }
    /**
     * Fixed Investment - GET /bea/investment-fixed/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentFixedRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-fixed/',
        });
    }
    /**
     * Change in Private Inventories - GET /bea/investment-inventories/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentInventoriesRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-inventories/',
        });
    }
    /**
     * Intellectual Property Products Investment - GET /bea/investment-ip/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentIpRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-ip/',
        });
    }
    /**
     * Net Private Domestic Investment - GET /bea/investment-net/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentNetRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-net/',
        });
    }
    /**
     * Nonresidential Investment - GET /bea/investment-nonresidential/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentNonresidentialRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-nonresidential/',
        });
    }
    /**
     * Residential Investment - GET /bea/investment-residential/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentResidentialRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-residential/',
        });
    }
    /**
     * Structures Investment - GET /bea/investment-structures/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentStructuresRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-structures/',
        });
    }
    /**
     * Gross Private Domestic Investment - GET /bea/investment-total/
     * @returns BeaInvestmentResponse
     * @throws ApiError
     */
    public static apiBeaInvestmentTotalRetrieve(): CancelablePromise<BeaInvestmentResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/investment-total/',
        });
    }
    /**
     * BEA系统统计信息
     * @returns BeaStatsResponse
     * @throws ApiError
     */
    public static apiBeaStatsRetrieve(): CancelablePromise<BeaStatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/bea/stats/',
        });
    }
    /**
     * Content category API
     * @returns ContentCategory
     * @throws ApiError
     */
    public static apiContentCategoriesList(): CancelablePromise<Array<ContentCategory>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/categories/',
        });
    }
    /**
     * Content category API
     * @param id A unique integer value identifying this Content Category.
     * @returns ContentCategory
     * @throws ApiError
     */
    public static apiContentCategoriesRetrieve(
        id: number,
    ): CancelablePromise<ContentCategory> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/categories/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * Modal content API
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsList(): CancelablePromise<Array<ModalContent>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/',
        });
    }
    /**
     * Modal content API
     * @param id A unique integer value identifying this Modal Content.
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsRetrieve(
        id: number,
    ): CancelablePromise<ModalContent> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * Get all content - simplified version for batch retrieval
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsAllContentRetrieve(): CancelablePromise<ModalContent> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/all_content/',
        });
    }
    /**
     * Get content by modal_id
     * @returns ModalContent
     * @throws ApiError
     */
    public static apiContentModalsByModalIdRetrieve(): CancelablePromise<ModalContent> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/content/modals/by_modal_id/',
        });
    }
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
     * @param page A page number within the paginated result set.
     * @param pageSize Number of results to return per page.
     * @returns PaginatedCSI300CompanyListList
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesList(
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedCSI300CompanyListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/',
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
    public static apiCsi300ApiCompaniesRetrieve(
        id: number,
    ): CancelablePromise<CSI300Company> {
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
     * @param id A unique integer value identifying this CSI300 Company.
     * @returns CSI300PeerComparisonResponse
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesIndustryPeersComparisonRetrieve(
        id: number,
    ): CancelablePromise<CSI300PeerComparisonResponse> {
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
     * @param id A unique integer value identifying this CSI300 Company.
     * @returns CSI300InvestmentSummary
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesInvestmentSummaryRetrieve(
        id: number,
    ): CancelablePromise<CSI300InvestmentSummary> {
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
     * @param imSector
     * @param region
     * @returns CSI300FilterOptions
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesFilterOptionsRetrieve(
        imSector?: string,
        region?: string,
    ): CancelablePromise<CSI300FilterOptions> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/filter_options/',
            query: {
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
     * @returns CSI300Company
     * @throws ApiError
     */
    public static apiCsi300ApiCompaniesHealthRetrieve(): CancelablePromise<CSI300Company> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/health/',
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
    public static apiCsi300ApiCompaniesSearchList(
        q: string,
        page?: number,
        pageSize?: number,
    ): CancelablePromise<PaginatedCSI300CompanyListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/csi300/api/companies/search/',
            query: {
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
    /**
     * API 根端点 - 返回 API 概览信息
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredList(): CancelablePromise<Array<FredUsIndicatorResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/',
        });
    }
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
    /**
     * API 根端点 - 返回 API 概览信息
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsList(): CancelablePromise<Array<FredUsIndicatorResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/',
        });
    }
    /**
     * 美国 FRED 指标数据 ViewSet
     *
     * 提供美国 FRED 经济指标的 API 端点:
     * - list: API 概览信息
     * - indicator: 获取指定指标数据
     * - status: 服务状态
     * - all_indicators: 所有指标摘要
     * - health: 健康检查
     * - 各种特定指标端点 (通过 Mixins 提供)
     * @param id A unique integer value identifying this US FRED Indicator.
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsRetrieve(
        id: number,
    ): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 穆迪Aaa级企业债券收益率 - GET /api/fred-us/aaa-corporate-bond-yield/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsAaaCorporateBondYieldRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/aaa-corporate-bond-yield/',
        });
    }
    /**
     * 获取所有美国FRED指标概览
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsAllIndicatorsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/all_indicators/',
        });
    }
    /**
     * 平均时薪增长 - GET /api/fred-us/average-hourly-earnings/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsAverageHourlyEarningsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/average-hourly-earnings/',
        });
    }
    /**
     * 穆迪Baa级企业债券收益率 - GET /api/fred-us/baa-corporate-bond-yield/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBaaCorporateBondYieldRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/baa-corporate-bond-yield/',
        });
    }
    /**
     * 银行贷款标准 - GET /api/fred-us/bank-lending-standards/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankLendingStandardsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/bank-lending-standards/',
        });
    }
    /**
     * 商业银行贷款和租赁 - GET /api/fred-us/banking-commercial-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingCommercialLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-commercial-loans/',
        });
    }
    /**
     * 美联储资产负债表总资产 - GET /api/fred-us/banking-fed-balance-sheet/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingFedBalanceSheetRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-fed-balance-sheet/',
        });
    }
    /**
     * 联邦基金利率 (Banking) - GET /api/fred-us/banking-federal-funds-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingFederalFundsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-federal-funds-rate/',
        });
    }
    /**
     * PCE价格指数 (Banking) - GET /api/fred-us/banking-pce-inflation/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingPceInflationRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-pce-inflation/',
        });
    }
    /**
     * 银行基准贷款利率 - GET /api/fred-us/banking-prime-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingPrimeRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-prime-rate/',
        });
    }
    /**
     * 准备金余额利率 - GET /api/fred-us/banking-reserve-balances-interest/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingReserveBalancesInterestRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-reserve-balances-interest/',
        });
    }
    /**
     * 总准备金余额 - GET /api/fred-us/banking-total-reserves/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingTotalReservesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-total-reserves/',
        });
    }
    /**
     * 失业率 (Banking) - GET /api/fred-us/banking-unemployment-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsBankingUnemploymentRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/banking-unemployment-rate/',
        });
    }
    /**
     * 商业银行贷款和租赁总额 - GET /api/fred-us/commercial-bank-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsCommercialBankLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/commercial-bank-loans/',
        });
    }
    /**
     * 总消费者信贷 - GET /api/fred-us/consumer-credit/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsConsumerCreditRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/consumer-credit/',
        });
    }
    /**
     * 消费者价格通胀率 - GET /api/fred-us/consumer-price-inflation/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsConsumerPriceInflationRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/consumer-price-inflation/',
        });
    }
    /**
     * 非金融企业债务占股权市值比例 - GET /api/fred-us/corporate-debt-equity-ratio/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsCorporateDebtEquityRatioRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/corporate-debt-equity-ratio/',
        });
    }
    /**
     * 非金融企业：债券和贷款负债水平 - GET /api/fred-us/corporate-debt-securities/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsCorporateDebtSecuritiesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/corporate-debt-securities/',
        });
    }
    /**
     * 消费者价格指数 - GET /api/fred-us/cpi/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsCpiRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/cpi/',
        });
    }
    /**
     * 信用卡债务余额 - GET /api/fred-us/credit-card-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsCreditCardDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/credit-card-debt/',
        });
    }
    /**
     * 经常账户余额 - GET /api/fred-us/current-account-balance/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsCurrentAccountBalanceRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/current-account-balance/',
        });
    }
    /**
     * 关税收入 - GET /api/fred-us/customs-duties/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsCustomsDutiesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/customs-duties/',
        });
    }
    /**
     * 家庭债务偿还比率 - GET /api/fred-us/debt-service-ratio/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsDebtServiceRatioRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/debt-service-ratio/',
        });
    }
    /**
     * 债务与GDP比率 - GET /api/fred-us/debt-to-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsDebtToGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/debt-to-gdp/',
        });
    }
    /**
     * 就业成本指数 - GET /api/fred-us/employment-cost-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsEmploymentCostIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/employment-cost-index/',
        });
    }
    /**
     * 存款机构超额准备金 - GET /api/fred-us/excess-reserves/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsExcessReservesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/excess-reserves/',
        });
    }
    /**
     * 美联储资产负债表总资产 - GET /api/fred-us/fed-balance-sheet/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFedBalanceSheetRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/fed-balance-sheet/',
        });
    }
    /**
     * 联邦基金利率 - GET /api/fred-us/fed-funds/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFedFundsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/fed-funds/',
        });
    }
    /**
     * 联邦政府当期支出 - GET /api/fred-us/federal-current-expenditures/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalCurrentExpendituresRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-current-expenditures/',
        });
    }
    /**
     * 联邦政府当期收入 - GET /api/fred-us/federal-current-receipts/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalCurrentReceiptsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-current-receipts/',
        });
    }
    /**
     * 联邦债务占GDP比例 - GET /api/fred-us/federal-debt-gdp-ratio/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalDebtGdpRatioRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-debt-gdp-ratio/',
        });
    }
    /**
     * 联邦债务占GDP比例 (GDF) - GET /api/fred-us/federal-debt-gdp-ratio-gdf/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalDebtGdpRatioGdfRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-debt-gdp-ratio-gdf/',
        });
    }
    /**
     * 联邦公共债务占GDP比例 - GET /api/fred-us/federal-debt-public-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalDebtPublicGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-debt-public-gdp/',
        });
    }
    /**
     * 联邦债务总额 - GET /api/fred-us/federal-debt-total/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalDebtTotalRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-debt-total/',
        });
    }
    /**
     * 联邦债务总额 (GDF) - GET /api/fred-us/federal-debt-total-gdf/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalDebtTotalGdfRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-debt-total-gdf/',
        });
    }
    /**
     * 联邦基金利率 (Money Supply) - GET /api/fred-us/federal-funds-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalFundsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-funds-rate/',
        });
    }
    /**
     * 联邦利息支出占GDP比例 - GET /api/fred-us/federal-interest-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalInterestGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-interest-gdp/',
        });
    }
    /**
     * 联邦净支出 - GET /api/fred-us/federal-net-outlays/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalNetOutlaysRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-net-outlays/',
        });
    }
    /**
     * 联邦盈余或赤字 - GET /api/fred-us/federal-surplus-deficit/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalSurplusDeficitRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-surplus-deficit/',
        });
    }
    /**
     * 联邦盈余或赤字 (GDF) - GET /api/fred-us/federal-surplus-deficit-gdf/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalSurplusDeficitGdfRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-surplus-deficit-gdf/',
        });
    }
    /**
     * 财政盈余/赤字 - GET /api/fred-us/federal-surplus-deficit-mts/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalSurplusDeficitMtsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-surplus-deficit-mts/',
        });
    }
    /**
     * 联邦政府当期税收 - GET /api/fred-us/federal-tax-receipts/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFederalTaxReceiptsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/federal-tax-receipts/',
        });
    }
    /**
     * 手动获取美国FRED数据
     * @param requestBody
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsFetchDataCreate(
        requestBody: FredUsIndicatorResponse,
    ): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/fred-us/fetch_data/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 外国持有的美国国债 - GET /api/fred-us/foreign-treasury-holdings/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsForeignTreasuryHoldingsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/foreign-treasury-holdings/',
        });
    }
    /**
     * 政府消费者信贷 - GET /api/fred-us/government-consumer-credit/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsGovernmentConsumerCreditRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/government-consumer-credit/',
        });
    }
    /**
     * 联邦总债务 - GET /api/fred-us/gross-federal-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsGrossFederalDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/gross-federal-debt/',
        });
    }
    /**
     * 健康检查端点
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsHealthRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/health/',
        });
    }
    /**
     * 高收益债券利差 - GET /api/fred-us/high-yield-bond-spread/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsHighYieldBondSpreadRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/high-yield-bond-spread/',
        });
    }
    /**
     * 家庭债务占GDP比重 - GET /api/fred-us/household-debt-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsHouseholdDebtGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/household-debt-gdp/',
        });
    }
    /**
     * 房屋开工数 - GET /api/fred-us/housing/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsHousingRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/housing/',
        });
    }
    /**
     * 获取指定美国 FRED 指标数据
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsIndicatorRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/indicator/',
        });
    }
    /**
     * 10年盈亏平衡通胀率 - GET /api/fred-us/inflation-breakeven-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationBreakevenRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-breakeven-rate/',
        });
    }
    /**
     * 消费者价格指数 (CPI) - GET /api/fred-us/inflation-consumer-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationConsumerPriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-consumer-price-index/',
        });
    }
    /**
     * 核心PCE价格指数 - GET /api/fred-us/inflation-core-pce-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationCorePcePriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-core-pce-price-index/',
        });
    }
    /**
     * 联邦基金利率 (Inflation) - GET /api/fred-us/inflation-federal-funds-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationFederalFundsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-federal-funds-rate/',
        });
    }
    /**
     * 原油价格 (WTI) - GET /api/fred-us/inflation-oil-prices/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationOilPricesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-oil-prices/',
        });
    }
    /**
     * 生产者价格指数 - GET /api/fred-us/inflation-producer-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationProducerPriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-producer-price-index/',
        });
    }
    /**
     * 零售销售 - GET /api/fred-us/inflation-retail-sales/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationRetailSalesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-retail-sales/',
        });
    }
    /**
     * 失业率 (Inflation) - GET /api/fred-us/inflation-unemployment-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInflationUnemploymentRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/inflation-unemployment-rate/',
        });
    }
    /**
     * 首次申请失业救济人数 - GET /api/fred-us/initial-jobless-claims/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInitialJoblessClaimsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/initial-jobless-claims/',
        });
    }
    /**
     * 准备金余额利率 - GET /api/fred-us/interest-rate-reserve-balances/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsInterestRateReserveBalancesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/interest-rate-reserve-balances/',
        });
    }
    /**
     * 职位空缺总数 - GET /api/fred-us/job-openings/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsJobOpeningsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/job-openings/',
        });
    }
    /**
     * 劳动力参与率 - GET /api/fred-us/labor-force-participation/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsLaborForceParticipationRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/labor-force-participation/',
        });
    }
    /**
     * M1货币供应量 - GET /api/fred-us/m1/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsM1Retrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/m1/',
        });
    }
    /**
     * M1货币供应量 - GET /api/fred-us/m1-money-supply/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsM1MoneySupplyRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/m1-money-supply/',
        });
    }
    /**
     * M2货币供应量 - GET /api/fred-us/m2/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsM2Retrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/m2/',
        });
    }
    /**
     * M2货币供应量 - GET /api/fred-us/m2-money-supply/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsM2MoneySupplyRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/m2-money-supply/',
        });
    }
    /**
     * M2货币流通速度 - GET /api/fred-us/m2v/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsM2VRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/m2v/',
        });
    }
    /**
     * 货币基础 - GET /api/fred-us/monetary-base/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsMonetaryBaseRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/monetary-base/',
        });
    }
    /**
     * 30年固定抵押贷款利率 - GET /api/fred-us/mortgage-30y/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsMortgage30YRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/mortgage-30y/',
        });
    }
    /**
     * 抵押贷款债务未偿余额 - GET /api/fred-us/mortgage-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsMortgageDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/mortgage-debt/',
        });
    }
    /**
     * NBER经济衰退指标 - GET /api/fred-us/nber-recession-indicator/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsNberRecessionIndicatorRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/nber-recession-indicator/',
        });
    }
    /**
     * 净出口 - GET /api/fred-us/net-exports/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsNetExportsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/net-exports/',
        });
    }
    /**
     * 非农就业人数 - GET /api/fred-us/nonfarm-payroll/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsNonfarmPayrollRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/nonfarm-payroll/',
        });
    }
    /**
     * 隔夜逆回购协议 - GET /api/fred-us/overnight-reverse-repo/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsOvernightReverseRepoRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/overnight-reverse-repo/',
        });
    }
    /**
     * PCE价格指数 - GET /api/fred-us/pce-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsPcePriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/pce-price-index/',
        });
    }
    /**
     * 55岁及以上人口 - GET /api/fred-us/population-55-over/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsPopulation55OverRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/population-55-over/',
        });
    }
    /**
     * 主要信贷贷款 - GET /api/fred-us/primary-credit-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsPrimaryCreditLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/primary-credit-loans/',
        });
    }
    /**
     * 辞职率 - GET /api/fred-us/quits-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsQuitsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/quits-rate/',
        });
    }
    /**
     * 实际出口 - GET /api/fred-us/real-exports/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsRealExportsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/real-exports/',
        });
    }
    /**
     * 实际进口 - GET /api/fred-us/real-imports/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsRealImportsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/real-imports/',
        });
    }
    /**
     * 获取美国FRED服务状态
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsStatusRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/status/',
        });
    }
    /**
     * 学生贷款 - GET /api/fred-us/student-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsStudentLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/student-loans/',
        });
    }
    /**
     * 家庭总债务 - GET /api/fred-us/total-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsTotalDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/total-debt/',
        });
    }
    /**
     * 贸易平衡 - GET /api/fred-us/trade-balance-goods-services/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsTradeBalanceGoodsServicesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/trade-balance-goods-services/',
        });
    }
    /**
     * 10年期国债利率 - GET /api/fred-us/treasury-10y/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsTreasury10YRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/treasury-10y/',
        });
    }
    /**
     * 2年期国债利率 - GET /api/fred-us/treasury-2y/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsTreasury2YRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/treasury-2y/',
        });
    }
    /**
     * 3个月国债利率 - GET /api/fred-us/treasury-3m/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsTreasury3MRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/treasury-3m/',
        });
    }
    /**
     * 失业率 - GET /api/fred-us/unemployment/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsUnemploymentRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/unemployment/',
        });
    }
    /**
     * 失业率 - GET /api/fred-us/unemployment-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUsUnemploymentRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred-us/unemployment-rate/',
        });
    }
    /**
     * 美国 FRED 指标数据 ViewSet
     *
     * 提供美国 FRED 经济指标的 API 端点:
     * - list: API 概览信息
     * - indicator: 获取指定指标数据
     * - status: 服务状态
     * - all_indicators: 所有指标摘要
     * - health: 健康检查
     * - 各种特定指标端点 (通过 Mixins 提供)
     * @param id A unique integer value identifying this US FRED Indicator.
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredRetrieve(
        id: number,
    ): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * 穆迪Aaa级企业债券收益率 - GET /api/fred-us/aaa-corporate-bond-yield/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredAaaCorporateBondYieldRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/aaa-corporate-bond-yield/',
        });
    }
    /**
     * 获取所有美国FRED指标概览
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredAllIndicatorsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/all_indicators/',
        });
    }
    /**
     * 平均时薪增长 - GET /api/fred-us/average-hourly-earnings/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredAverageHourlyEarningsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/average-hourly-earnings/',
        });
    }
    /**
     * 穆迪Baa级企业债券收益率 - GET /api/fred-us/baa-corporate-bond-yield/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBaaCorporateBondYieldRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/baa-corporate-bond-yield/',
        });
    }
    /**
     * 银行贷款标准 - GET /api/fred-us/bank-lending-standards/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankLendingStandardsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/bank-lending-standards/',
        });
    }
    /**
     * 商业银行贷款和租赁 - GET /api/fred-us/banking-commercial-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingCommercialLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-commercial-loans/',
        });
    }
    /**
     * 美联储资产负债表总资产 - GET /api/fred-us/banking-fed-balance-sheet/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingFedBalanceSheetRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-fed-balance-sheet/',
        });
    }
    /**
     * 联邦基金利率 (Banking) - GET /api/fred-us/banking-federal-funds-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingFederalFundsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-federal-funds-rate/',
        });
    }
    /**
     * PCE价格指数 (Banking) - GET /api/fred-us/banking-pce-inflation/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingPceInflationRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-pce-inflation/',
        });
    }
    /**
     * 银行基准贷款利率 - GET /api/fred-us/banking-prime-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingPrimeRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-prime-rate/',
        });
    }
    /**
     * 准备金余额利率 - GET /api/fred-us/banking-reserve-balances-interest/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingReserveBalancesInterestRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-reserve-balances-interest/',
        });
    }
    /**
     * 总准备金余额 - GET /api/fred-us/banking-total-reserves/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingTotalReservesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-total-reserves/',
        });
    }
    /**
     * 失业率 (Banking) - GET /api/fred-us/banking-unemployment-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredBankingUnemploymentRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/banking-unemployment-rate/',
        });
    }
    /**
     * 商业银行贷款和租赁总额 - GET /api/fred-us/commercial-bank-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredCommercialBankLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/commercial-bank-loans/',
        });
    }
    /**
     * 总消费者信贷 - GET /api/fred-us/consumer-credit/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredConsumerCreditRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/consumer-credit/',
        });
    }
    /**
     * 消费者价格通胀率 - GET /api/fred-us/consumer-price-inflation/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredConsumerPriceInflationRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/consumer-price-inflation/',
        });
    }
    /**
     * 非金融企业债务占股权市值比例 - GET /api/fred-us/corporate-debt-equity-ratio/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredCorporateDebtEquityRatioRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/corporate-debt-equity-ratio/',
        });
    }
    /**
     * 非金融企业：债券和贷款负债水平 - GET /api/fred-us/corporate-debt-securities/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredCorporateDebtSecuritiesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/corporate-debt-securities/',
        });
    }
    /**
     * 消费者价格指数 - GET /api/fred-us/cpi/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredCpiRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/cpi/',
        });
    }
    /**
     * 信用卡债务余额 - GET /api/fred-us/credit-card-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredCreditCardDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/credit-card-debt/',
        });
    }
    /**
     * 经常账户余额 - GET /api/fred-us/current-account-balance/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredCurrentAccountBalanceRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/current-account-balance/',
        });
    }
    /**
     * 关税收入 - GET /api/fred-us/customs-duties/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredCustomsDutiesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/customs-duties/',
        });
    }
    /**
     * 家庭债务偿还比率 - GET /api/fred-us/debt-service-ratio/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredDebtServiceRatioRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/debt-service-ratio/',
        });
    }
    /**
     * 债务与GDP比率 - GET /api/fred-us/debt-to-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredDebtToGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/debt-to-gdp/',
        });
    }
    /**
     * 就业成本指数 - GET /api/fred-us/employment-cost-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredEmploymentCostIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/employment-cost-index/',
        });
    }
    /**
     * 存款机构超额准备金 - GET /api/fred-us/excess-reserves/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredExcessReservesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/excess-reserves/',
        });
    }
    /**
     * 美联储资产负债表总资产 - GET /api/fred-us/fed-balance-sheet/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFedBalanceSheetRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/fed-balance-sheet/',
        });
    }
    /**
     * 联邦基金利率 - GET /api/fred-us/fed-funds/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFedFundsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/fed-funds/',
        });
    }
    /**
     * 联邦政府当期支出 - GET /api/fred-us/federal-current-expenditures/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalCurrentExpendituresRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-current-expenditures/',
        });
    }
    /**
     * 联邦政府当期收入 - GET /api/fred-us/federal-current-receipts/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalCurrentReceiptsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-current-receipts/',
        });
    }
    /**
     * 联邦债务占GDP比例 - GET /api/fred-us/federal-debt-gdp-ratio/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalDebtGdpRatioRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-debt-gdp-ratio/',
        });
    }
    /**
     * 联邦债务占GDP比例 (GDF) - GET /api/fred-us/federal-debt-gdp-ratio-gdf/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalDebtGdpRatioGdfRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-debt-gdp-ratio-gdf/',
        });
    }
    /**
     * 联邦公共债务占GDP比例 - GET /api/fred-us/federal-debt-public-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalDebtPublicGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-debt-public-gdp/',
        });
    }
    /**
     * 联邦债务总额 - GET /api/fred-us/federal-debt-total/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalDebtTotalRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-debt-total/',
        });
    }
    /**
     * 联邦债务总额 (GDF) - GET /api/fred-us/federal-debt-total-gdf/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalDebtTotalGdfRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-debt-total-gdf/',
        });
    }
    /**
     * 联邦基金利率 (Money Supply) - GET /api/fred-us/federal-funds-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalFundsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-funds-rate/',
        });
    }
    /**
     * 联邦利息支出占GDP比例 - GET /api/fred-us/federal-interest-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalInterestGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-interest-gdp/',
        });
    }
    /**
     * 联邦净支出 - GET /api/fred-us/federal-net-outlays/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalNetOutlaysRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-net-outlays/',
        });
    }
    /**
     * 联邦盈余或赤字 - GET /api/fred-us/federal-surplus-deficit/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalSurplusDeficitRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-surplus-deficit/',
        });
    }
    /**
     * 联邦盈余或赤字 (GDF) - GET /api/fred-us/federal-surplus-deficit-gdf/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalSurplusDeficitGdfRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-surplus-deficit-gdf/',
        });
    }
    /**
     * 财政盈余/赤字 - GET /api/fred-us/federal-surplus-deficit-mts/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalSurplusDeficitMtsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-surplus-deficit-mts/',
        });
    }
    /**
     * 联邦政府当期税收 - GET /api/fred-us/federal-tax-receipts/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFederalTaxReceiptsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/federal-tax-receipts/',
        });
    }
    /**
     * 手动获取美国FRED数据
     * @param requestBody
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredFetchDataCreate(
        requestBody: FredUsIndicatorResponse,
    ): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/fred/fetch_data/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 外国持有的美国国债 - GET /api/fred-us/foreign-treasury-holdings/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredForeignTreasuryHoldingsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/foreign-treasury-holdings/',
        });
    }
    /**
     * 政府消费者信贷 - GET /api/fred-us/government-consumer-credit/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredGovernmentConsumerCreditRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/government-consumer-credit/',
        });
    }
    /**
     * 联邦总债务 - GET /api/fred-us/gross-federal-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredGrossFederalDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/gross-federal-debt/',
        });
    }
    /**
     * 健康检查端点
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredHealthRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/health/',
        });
    }
    /**
     * 高收益债券利差 - GET /api/fred-us/high-yield-bond-spread/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredHighYieldBondSpreadRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/high-yield-bond-spread/',
        });
    }
    /**
     * 家庭债务占GDP比重 - GET /api/fred-us/household-debt-gdp/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredHouseholdDebtGdpRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/household-debt-gdp/',
        });
    }
    /**
     * 房屋开工数 - GET /api/fred-us/housing/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredHousingRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/housing/',
        });
    }
    /**
     * 获取指定美国 FRED 指标数据
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredIndicatorRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/indicator/',
        });
    }
    /**
     * 10年盈亏平衡通胀率 - GET /api/fred-us/inflation-breakeven-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationBreakevenRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-breakeven-rate/',
        });
    }
    /**
     * 消费者价格指数 (CPI) - GET /api/fred-us/inflation-consumer-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationConsumerPriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-consumer-price-index/',
        });
    }
    /**
     * 核心PCE价格指数 - GET /api/fred-us/inflation-core-pce-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationCorePcePriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-core-pce-price-index/',
        });
    }
    /**
     * 联邦基金利率 (Inflation) - GET /api/fred-us/inflation-federal-funds-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationFederalFundsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-federal-funds-rate/',
        });
    }
    /**
     * 原油价格 (WTI) - GET /api/fred-us/inflation-oil-prices/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationOilPricesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-oil-prices/',
        });
    }
    /**
     * 生产者价格指数 - GET /api/fred-us/inflation-producer-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationProducerPriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-producer-price-index/',
        });
    }
    /**
     * 零售销售 - GET /api/fred-us/inflation-retail-sales/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationRetailSalesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-retail-sales/',
        });
    }
    /**
     * 失业率 (Inflation) - GET /api/fred-us/inflation-unemployment-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInflationUnemploymentRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/inflation-unemployment-rate/',
        });
    }
    /**
     * 首次申请失业救济人数 - GET /api/fred-us/initial-jobless-claims/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInitialJoblessClaimsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/initial-jobless-claims/',
        });
    }
    /**
     * 准备金余额利率 - GET /api/fred-us/interest-rate-reserve-balances/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredInterestRateReserveBalancesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/interest-rate-reserve-balances/',
        });
    }
    /**
     * 职位空缺总数 - GET /api/fred-us/job-openings/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredJobOpeningsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/job-openings/',
        });
    }
    /**
     * 劳动力参与率 - GET /api/fred-us/labor-force-participation/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredLaborForceParticipationRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/labor-force-participation/',
        });
    }
    /**
     * M1货币供应量 - GET /api/fred-us/m1/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredM1Retrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/m1/',
        });
    }
    /**
     * M1货币供应量 - GET /api/fred-us/m1-money-supply/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredM1MoneySupplyRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/m1-money-supply/',
        });
    }
    /**
     * M2货币供应量 - GET /api/fred-us/m2/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredM2Retrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/m2/',
        });
    }
    /**
     * M2货币供应量 - GET /api/fred-us/m2-money-supply/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredM2MoneySupplyRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/m2-money-supply/',
        });
    }
    /**
     * M2货币流通速度 - GET /api/fred-us/m2v/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredM2VRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/m2v/',
        });
    }
    /**
     * 货币基础 - GET /api/fred-us/monetary-base/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredMonetaryBaseRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/monetary-base/',
        });
    }
    /**
     * 30年固定抵押贷款利率 - GET /api/fred-us/mortgage-30y/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredMortgage30YRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/mortgage-30y/',
        });
    }
    /**
     * 抵押贷款债务未偿余额 - GET /api/fred-us/mortgage-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredMortgageDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/mortgage-debt/',
        });
    }
    /**
     * NBER经济衰退指标 - GET /api/fred-us/nber-recession-indicator/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredNberRecessionIndicatorRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/nber-recession-indicator/',
        });
    }
    /**
     * 净出口 - GET /api/fred-us/net-exports/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredNetExportsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/net-exports/',
        });
    }
    /**
     * 非农就业人数 - GET /api/fred-us/nonfarm-payroll/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredNonfarmPayrollRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/nonfarm-payroll/',
        });
    }
    /**
     * 隔夜逆回购协议 - GET /api/fred-us/overnight-reverse-repo/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredOvernightReverseRepoRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/overnight-reverse-repo/',
        });
    }
    /**
     * PCE价格指数 - GET /api/fred-us/pce-price-index/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredPcePriceIndexRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/pce-price-index/',
        });
    }
    /**
     * 55岁及以上人口 - GET /api/fred-us/population-55-over/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredPopulation55OverRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/population-55-over/',
        });
    }
    /**
     * 主要信贷贷款 - GET /api/fred-us/primary-credit-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredPrimaryCreditLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/primary-credit-loans/',
        });
    }
    /**
     * 辞职率 - GET /api/fred-us/quits-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredQuitsRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/quits-rate/',
        });
    }
    /**
     * 实际出口 - GET /api/fred-us/real-exports/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredRealExportsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/real-exports/',
        });
    }
    /**
     * 实际进口 - GET /api/fred-us/real-imports/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredRealImportsRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/real-imports/',
        });
    }
    /**
     * 获取美国FRED服务状态
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredStatusRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/status/',
        });
    }
    /**
     * 学生贷款 - GET /api/fred-us/student-loans/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredStudentLoansRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/student-loans/',
        });
    }
    /**
     * 家庭总债务 - GET /api/fred-us/total-debt/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredTotalDebtRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/total-debt/',
        });
    }
    /**
     * 贸易平衡 - GET /api/fred-us/trade-balance-goods-services/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredTradeBalanceGoodsServicesRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/trade-balance-goods-services/',
        });
    }
    /**
     * 10年期国债利率 - GET /api/fred-us/treasury-10y/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredTreasury10YRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/treasury-10y/',
        });
    }
    /**
     * 2年期国债利率 - GET /api/fred-us/treasury-2y/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredTreasury2YRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/treasury-2y/',
        });
    }
    /**
     * 3个月国债利率 - GET /api/fred-us/treasury-3m/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredTreasury3MRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/treasury-3m/',
        });
    }
    /**
     * 失业率 - GET /api/fred-us/unemployment/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUnemploymentRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/unemployment/',
        });
    }
    /**
     * 失业率 - GET /api/fred-us/unemployment-rate/
     * @returns FredUsIndicatorResponse
     * @throws ApiError
     */
    public static apiFredUnemploymentRateRetrieve(): CancelablePromise<FredUsIndicatorResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fred/unemployment-rate/',
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
    /**
     * Internal callback for LaTeX worker status updates
     * @param requestBody
     * @returns any
     * @throws ApiError
     */
    public static apiPdfInternalCallbackCreate(
        requestBody?: Record<string, any>,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/pdf/internal/callback/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Get pre-signed download URL for a completed PDF
     * @param taskId Task UUID
     * @returns PDFDownloadResponse
     * @throws ApiError
     */
    public static apiPdfTasksDownloadRetrieve(
        taskId: string,
    ): CancelablePromise<PDFDownloadResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/tasks/download/{task_id}/',
            path: {
                'task_id': taskId,
            },
        });
    }
    /**
     * List recent PDF generation tasks
     * @param companyId Optional company ID filter
     * @returns PDFTask
     * @throws ApiError
     */
    public static apiPdfTasksHistoryList(
        companyId?: number,
    ): CancelablePromise<Array<PDFTask>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/tasks/history/',
            query: {
                'company_id': companyId,
            },
        });
    }
    /**
     * Request generation of a PDF report for a company
     * @param requestBody
     * @returns PDFTaskCreateResponse
     * @throws ApiError
     */
    public static apiPdfTasksRequestCreate(
        requestBody: PDFRequest,
    ): CancelablePromise<PDFTaskCreateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/pdf/tasks/request/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Get current status and progress of a PDF generation task
     * @param taskId Task UUID
     * @returns PDFTask
     * @throws ApiError
     */
    public static apiPdfTasksStatusRetrieve(
        taskId: string,
    ): CancelablePromise<PDFTask> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/tasks/status/{task_id}/',
            path: {
                'task_id': taskId,
            },
        });
    }
    /**
     * ViewSet for listing available PDF templates.
     *
     * Provides read-only access to active templates for selection.
     * @returns PDFTemplate
     * @throws ApiError
     */
    public static apiPdfTemplatesList(): CancelablePromise<Array<PDFTemplate>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/templates/',
        });
    }
    /**
     * ViewSet for listing available PDF templates.
     *
     * Provides read-only access to active templates for selection.
     * @param id A unique integer value identifying this PDF Template.
     * @returns PDFTemplateDetail
     * @throws ApiError
     */
    public static apiPdfTemplatesRetrieve(
        id: number,
    ): CancelablePromise<PDFTemplateDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/pdf/templates/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * Serve curated policy updates sourced from the Federal Register API.
     * @param country Country code
     * @param limit Number of results
     * @param q Search term
     * @param topicsArray Topic filters
     * @returns PolicyUpdatesResponse
     * @throws ApiError
     */
    public static apiPolicyUpdatesRetrieve(
        country?: string,
        limit?: number,
        q?: string,
        topicsArray?: string,
    ): CancelablePromise<PolicyUpdatesResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/policy/updates/',
            query: {
                'country': country,
                'limit': limit,
                'q': q,
                'topics[]': topicsArray,
            },
        });
    }
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
