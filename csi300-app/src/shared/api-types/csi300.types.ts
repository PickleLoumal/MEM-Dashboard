/**
 * @fileoverview CSI300 相关 API 类型定义
 * @description 定义 CSI300 指数成分股相关的所有类型
 * @module shared/api-types/csi300
 * @version 1.0.0
 *
 * 后端对应:
 * - Model: src/django_api/csi300/models.py
 * - Serializer: src/django_api/csi300/serializers.py
 * - Views: src/django_api/csi300/views.py
 */

import type {
  ISODateString,
  ISODateTimeString,
  FormattedNumberString,
  PercentageString,
  PaginatedResponse,
} from './common.types';

// ============================================================================
// 公司基础信息类型
// ============================================================================

/**
 * CSI300 公司完整详情
 * 对应 Python Model: CSI300Company
 * 对应 Serializer: CSI300CompanySerializer
 */
export interface CSI300Company {
  id: number;
  
  // 基本信息
  name: string;
  ticker: string | null;
  region: string | null;
  im_sector: string | null;
  industry: string | null;
  gics_industry: string | null;
  gics_sub_industry: string | null;
  
  // 公司详情
  naming: string | null;
  business_description: string | null;
  company_info: string | null;
  directors: string | null;
  
  // 价格信息
  price_local_currency: number | null;
  previous_close: number | null;
  currency: string | null;
  total_return_2018_to_2025: number | null;
  last_trade_date: ISODateString | null;
  price_52w_high: number | null;
  price_52w_low: number | null;
  
  // 市值
  market_cap_local: number | null;
  market_cap_usd: number | null;
  
  // 营收
  total_revenue_local: number | null;
  ltm_revenue_local: number | null;
  ntm_revenue_local: number | null;
  
  // 资产负债
  total_assets_local: number | null;
  net_assets_local: number | null;
  total_debt_local: number | null;
  
  // 盈利能力
  net_profits_fy0: number | null;
  operating_margin_trailing: number | null;
  operating_profits_per_share: number | null;
  
  // 每股收益
  eps_trailing: number | null;
  eps_actual_fy0: number | null;
  eps_forecast_fy1: number | null;
  eps_growth_percent: number | null;
  
  // 财务比率
  asset_turnover_ltm: number | null;
  roa_trailing: number | null;
  roe_trailing: number | null;
  operating_leverage: number | null;
  
  // 风险指标
  altman_z_score_manufacturing: number | null;
  altman_z_score_non_manufacturing: number | null;
  
  // 现金流
  ebitda_fy0: number | null;
  ebitda_fy_minus_1: number | null;
  cash_flow_operations_fy0: number | null;
  cash_flow_operations_fy_minus_1: number | null;
  
  // 利息与债务
  interest_expense_fy0: number | null;
  effective_interest_rate: number | null;
  interest_coverage_ratio: number | null;
  debt_to_total_assets: number | null;
  debt_to_equity: number | null;
  
  // 流动性比率
  current_ratio: number | null;
  quick_ratio: number | null;
  
  // 估值比率
  pe_ratio_trailing: number | null;
  pe_ratio_consensus: number | null;
  peg_ratio: number | null;
  
  // 股息
  dividend_yield_fy0: number | null;
  dividend_payout_ratio: number | null;
  dividend_local_currency: number | null;
  dividend_3yr_cagr: number | null;
  dividend_5yr_cagr: number | null;
  dividend_10yr_cagr: number | null;
  
  // 元数据
  created_at?: ISODateTimeString;
  updated_at?: ISODateTimeString;
}

/**
 * CSI300 公司列表项 (简化版)
 * 对应 Serializer: CSI300CompanyListSerializer
 */
export type CSI300CompanyListItem = Omit<CSI300Company, 'created_at' | 'updated_at'>;

/**
 * H股公司类型 (与 CSI300Company 结构相同)
 * 对应 Python Model: CSI300HSharesCompany
 */
export type CSI300HSharesCompany = CSI300Company;

// ============================================================================
// 投资摘要类型
// ============================================================================

/**
 * CSI300 投资摘要
 * 对应 Python Model: CSI300InvestmentSummary
 * 对应 Serializer: CSI300InvestmentSummarySerializer
 */
export interface CSI300InvestmentSummary {
  id: number;
  company: number;
  company_name: string;
  company_ticker: string;
  im_sector: string;
  industry: string;
  
  report_date: ISODateString;
  
  // 市场数据
  stock_price_previous_close: number;
  market_cap_display: string;
  recommended_action: string;
  recommended_action_detail: string;
  
  // 分析章节 (Markdown 内容)
  business_overview: string;
  business_performance: string;
  industry_context: string;
  financial_stability: string;
  key_financials_valuation: string;
  big_trends_events: string;
  customer_segments: string;
  competitive_landscape: string;
  risks_anomalies: string;
  forecast_outlook: string;
  investment_firms_views: string;
  industry_ratio_analysis: string;
  tariffs_supply_chain_risks?: string;
  key_takeaways: string;
  sources: string;
  
  // 元数据
  created_at?: ISODateTimeString;
  updated_at?: ISODateTimeString;
}

// ============================================================================
// 同行业对比类型
// ============================================================================

/**
 * 同行业公司对比项
 * 对应 Serializer: CSI300IndustryPeersComparisonSerializer
 */
export interface CSI300PeerComparisonItem {
  id: number;
  ticker: string;
  name: string;
  im_sector: string | null;
  
  // 原始数值
  market_cap_local: number | null;
  market_cap_usd: number | null;
  pe_ratio_trailing: number | null;
  roe_trailing: number | null;
  operating_margin_trailing: number | null;
  
  // 格式化显示值
  market_cap_display: FormattedNumberString;
  pe_ratio_display: string;
  pb_ratio_display: string;
  roe_display: PercentageString;
  revenue_growth_display: string;
  operating_margin_display: PercentageString;
  
  // 排名信息 (动态添加)
  rank?: number;
  is_current_company?: boolean;
}

/**
 * 同行业对比响应
 * 对应 Views: industry_peers_comparison action
 */
export interface CSI300IndustryPeersComparisonResponse {
  target_company: {
    id: number;
    name: string;
    ticker: string;
    im_sector: string | null;
    rank: number | null;
  };
  industry: string | null;
  comparison_data: CSI300PeerComparisonItem[];
  total_top_companies_shown: number;
  total_companies_in_industry: number;
}

// ============================================================================
// API 响应类型
// ============================================================================

/**
 * 公司列表分页响应
 */
export type CSI300CompanyListResponse = PaginatedResponse<CSI300CompanyListItem>;

/**
 * 搜索响应
 */
export type CSI300SearchResponse = CSI300CompanyListItem[];

/**
 * API 索引响应
 */
export interface CSI300ApiIndexResponse {
  message: string;
  version: string;
  endpoints: {
    companies: string;
    company_detail: string;
    filter_options: string;
    search: string;
  };
  total_companies: number;
}

// ============================================================================
// 查询参数类型
// ============================================================================

/**
 * 公司列表查询参数
 */
export interface CSI300CompanyListParams {
  page?: number;
  page_size?: number;
  region?: string;
  im_sector?: string;
  industry?: string;
  gics_industry?: string;
  market_cap_min?: number;
  market_cap_max?: number;
  search?: string;
  industry_search?: string;
}

/**
 * 公司详情查询参数
 */
export interface CSI300CompanyDetailParams {
  region?: string;
}

