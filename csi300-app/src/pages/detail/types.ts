export interface CompanyDetail {
  id: number | string;
  name: string;
  ticker: string;
  
  // Basic Info
  im_sector?: string;
  im_code?: string;
  industry?: string;
  sub_industry?: string;
  gics_industry?: string;
  currency?: string;
  last_trade_date?: string;

  // Description
  business_description?: string;

  // Market Data
  price_local_currency?: number;
  previous_close?: number;
  market_cap_local?: number;
  market_cap_usd?: number;
  price_52w_high?: number;
  price_52w_low?: number;
  total_return_2018_to_2025?: number;

  // Financial Metrics
  total_revenue_local?: number;
  ltm_revenue_local?: number;
  ntm_revenue_local?: number;
  net_profits_fy0?: number;
  total_assets_local?: number;
  net_assets_local?: number;
  total_debt_local?: number;
  asset_turnover_ltm?: number;

  // EPS
  eps_trailing?: number;
  eps_actual_fy0?: number;
  eps_forecast_fy1?: number;
  eps_growth_percent?: number;

  // Cash Flow
  ebitda_fy0?: number;
  ebitda_fy_minus_1?: number;
  cash_flow_operations_fy0?: number;
  cash_flow_operations_fy_minus_1?: number;

  // Debt
  interest_expense_fy0?: number;
  effective_interest_rate?: number;
  interest_coverage_ratio?: number;
  debt_to_total_assets?: number;
  debt_to_equity?: number;

  // Ratios
  pe_ratio_trailing?: number;
  pe_ratio_consensus?: number;
  peg_ratio?: number;
  roe_trailing?: number;
  roa_trailing?: number;
  operating_margin_trailing?: number;
  operating_profits_per_share?: number;
  operating_leverage?: number;

  // Liquidity
  current_ratio?: number;
  quick_ratio?: number;

  // Dividend
  dividend_yield_fy0?: number;
  dividend_payout_ratio?: number;
  dividend_local_currency?: number;
  dividend_3yr_cagr?: number;
  dividend_5yr_cagr?: number;
  dividend_10yr_cagr?: number;

  // Risk
  altman_z_score_manufacturing?: number;
  altman_z_score_non_manufacturing?: number;
}

export interface PeerComparisonData {
  target_company: {
    rank: number;
  };
  total_companies_in_industry: number;
  total_peers_found: number;
  industry?: string;
  im_sector?: string;
  comparison_data: Array<{
    name: string;
    ticker: string;
    rank: number;
    is_current_company: boolean;
    market_cap_display: string;
    pe_ratio_display: string;
    roe_display: string;
    operating_margin_display: string;
    eps_growth_display: string;
  }>;
}

