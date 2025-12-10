/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnalystConsensus } from './AnalystConsensus';
import type { BalanceSheetMetrics } from './BalanceSheetMetrics';
import type { KeyMetrics } from './KeyMetrics';
import type { PricingData } from './PricingData';
import type { ProfitabilityMetrics } from './ProfitabilityMetrics';
import type { SegmentData } from './SegmentData';
import type { ValuationMetrics } from './ValuationMetrics';
/**
 * Investment Summary 完整财务上下文序列化器。
 *
 * 用于 API 响应和 OpenAPI schema 生成。
 */
export type FinancialContext = {
    /**
     * Reuters Instrument Code
     */
    ric: string;
    /**
     * 公司名称
     */
    company_name?: string | null;
    /**
     * 股票代码
     */
    ticker?: string | null;
    /**
     * 股价数据
     */
    pricing?: PricingData | null;
    /**
     * 关键指标
     */
    key_metrics?: KeyMetrics | null;
    /**
     * 估值指标
     */
    valuation?: ValuationMetrics | null;
    /**
     * 资产负债表指标
     */
    balance_sheet?: BalanceSheetMetrics | null;
    /**
     * 盈利能力指标
     */
    profitability?: ProfitabilityMetrics | null;
    /**
     * 分析师共识
     */
    analyst_consensus?: AnalystConsensus | null;
    /**
     * 业务分部
     */
    segments?: Array<SegmentData>;
    /**
     * 收入预测
     */
    revenue_forecast?: string | null;
    /**
     * 收入预测同比
     */
    revenue_forecast_yoy?: string | null;
    /**
     * EPS 预测
     */
    eps_forecast?: string | null;
    /**
     * EPS 预测同比
     */
    eps_forecast_yoy?: string | null;
    /**
     * 数据来源
     */
    data_source?: string;
    /**
     * 获取时间
     */
    fetch_timestamp?: string | null;
    /**
     * 错误信息列表
     */
    errors?: Array<string>;
};

