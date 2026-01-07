/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FredUsIndicatorResponse } from '../models/FredUsIndicatorResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FredUsService {
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
}
