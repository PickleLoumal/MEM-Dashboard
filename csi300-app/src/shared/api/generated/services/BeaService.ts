/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
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
import type { PatchedBeaConfigUpdate } from '../models/PatchedBeaConfigUpdate';
import type { PatchedBeaIndicator } from '../models/PatchedBeaIndicator';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class BeaService {
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
}
