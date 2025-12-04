/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CSI300Company } from '../models/CSI300Company';
import type { CSI300FilterOptions } from '../models/CSI300FilterOptions';
import type { CSI300IndustryPeersComparison } from '../models/CSI300IndustryPeersComparison';
import type { CSI300InvestmentSummary } from '../models/CSI300InvestmentSummary';
import type { PaginatedCSI300CompanyListList } from '../models/PaginatedCSI300CompanyListList';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class Csi300Service {
    /**
     * CSI300 API 索引端点
     *
     * 返回 API 概览信息，包括可用端点和统计数据。
     *
     * Args:
     * request: DRF 请求对象
     *
     * Returns:
     * Response: API 概览信息
     * @returns any No response body
     * @throws ApiError
     */
    public static csi300Retrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/csi300/',
        });
    }
    /**
     * CSI300 公司数据 ViewSet
     *
     * 提供 CSI300 指数成分股的只读 API 端点:
     * - list: 获取公司列表 (支持筛选和分页)
     * - retrieve: 获取单个公司详情
     * - filter_options: 获取筛选选项
     * - search: 搜索公司
     * - investment_summary: 获取投资摘要
     * - industry_peers_comparison: 获取同行业对比
     *
     * 类型注解:
     * - 所有方法返回 Response 对象
     * - 查询参数通过 request.query_params 获取
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
     *
     * Args:
     * request: DRF 请求对象
     * *args: 位置参数
     * **kwargs: 关键字参数，包含 pk (公司 ID)
     *
     * Returns:
     * Response: 包含公司详情的响应
     *
     * Raises:
     * Http404: 当公司不存在时
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
     *
     * 返回目标公司与同行业前3名公司的关键指标对比。
     *
     * Args:
     * request: DRF 请求对象
     * pk: 公司 ID
     *
     * Returns:
     * Response: 同行业对比数据
     * {
         * target_company: { id, name, ticker, im_sector, rank },
         * industry: str,
         * comparison_data: List[PeerComparisonItem],
         * total_top_companies_shown: int,
         * total_companies_in_industry: int
         * }
         * @param id A unique integer value identifying this CSI300 Company.
         * @returns CSI300IndustryPeersComparison
         * @throws ApiError
         */
        public static csi300ApiCompaniesIndustryPeersComparisonRetrieve(
            id: number,
        ): CancelablePromise<CSI300IndustryPeersComparison> {
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
         *
         * Args:
         * request: DRF 请求对象
         * pk: 公司 ID
         *
         * Returns:
         * Response: 投资摘要数据或错误响应
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
         *
         * 支持级联筛选：
         * - 根据 region 返回对应地区的选项
         * - 根据 im_sector 返回对应行业的细分选项
         *
         * Args:
         * request: DRF 请求对象
         *
         * Returns:
         * Response: 包含筛选选项的响应
         * {
             * regions: List[str],
             * im_sectors: List[str],
             * industries: List[str],
             * gics_industries: List[str],
             * market_cap_range: { min: float, max: float },
             * filtered_by_region: bool,
             * filtered_by_sector: bool
             * }
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
             * 搜索公司
             *
             * 通过公司名称、股票代码或别名进行搜索。
             *
             * Args:
             * request: DRF 请求对象，需要 'q' 查询参数
             *
             * Returns:
             * Response: 匹配的公司列表 (最多 10 条)
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
             * CSI300 API 健康检查端点
             *
             * 检查数据库连接和数据可用性。
             *
             * Args:
             * request: DRF 请求对象
             *
             * Returns:
             * Response: 健康状态信息
             * @returns any No response body
             * @throws ApiError
             */
            public static csi300HealthRetrieve(): CancelablePromise<any> {
                return __request(OpenAPI, {
                    method: 'GET',
                    url: '/csi300/health/',
                });
            }
        }
