/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Company serializer for API responses - includes all fields.
 */
export type Company = {
    readonly id: number;
    /**
     * Stock exchange code (SSE, SZSE, HKEX)
     *
     * * `SSE` - 上海证券交易所
     * * `SZSE` - 深圳证券交易所
     * * `HKEX` - 香港交易所
     */
    exchange?: Company.exchange;
    /**
     * Company name
     */
    name: string;
    /**
     * Stock ticker
     */
    ticker?: string | null;
    /**
     * Region (e.g., Mainland China, Hong Kong)
     */
    region?: string | null;
    /**
     * IM Sector (combined from im_code and industry)
     */
    im_sector?: string | null;
    /**
     * Industry
     */
    industry?: string | null;
    /**
     * GICS Industry
     */
    gics_industry?: string | null;
    /**
     * GICS Sub-industry
     */
    gics_sub_industry?: string | null;
    /**
     * Company naming
     */
    naming?: string | null;
    /**
     * Business description
     */
    business_description?: string | null;
    /**
     * Company info
     */
    company_info?: string | null;
    /**
     * Directors
     */
    directors?: string | null;
    /**
     * Price in local currency (Open)
     */
    price_local_currency?: string | null;
    /**
     * Previous close price
     */
    previous_close?: string | null;
    /**
     * Currency
     */
    currency?: string | null;
    /**
     * Total return 2018-2025
     */
    total_return_2018_to_2025?: string | null;
    /**
     * Last trade date
     */
    last_trade_date?: string | null;
    /**
     * 52-week high
     */
    price_52w_high?: string | null;
    /**
     * 52-week low
     */
    price_52w_low?: string | null;
    /**
     * Market cap (local)
     */
    market_cap_local?: string | null;
    /**
     * Market cap (USD)
     */
    market_cap_usd?: string | null;
    /**
     * Total revenue (local)
     */
    total_revenue_local?: string | null;
    /**
     * LTM revenue (local)
     */
    ltm_revenue_local?: string | null;
    /**
     * NTM revenue (local)
     */
    ntm_revenue_local?: string | null;
    /**
     * Total assets (local)
     */
    total_assets_local?: string | null;
    /**
     * Net assets (local)
     */
    net_assets_local?: string | null;
    /**
     * Total debt (local)
     */
    total_debt_local?: string | null;
    /**
     * Net profits FY0
     */
    net_profits_fy0?: string | null;
    /**
     * Operating margin (trailing)
     */
    operating_margin_trailing?: string | null;
    /**
     * Operating profits per share
     */
    operating_profits_per_share?: string | null;
    /**
     * EPS trailing
     */
    eps_trailing?: string | null;
    /**
     * EPS actual FY0
     */
    eps_actual_fy0?: string | null;
    /**
     * EPS forecast FY1
     */
    eps_forecast_fy1?: string | null;
    /**
     * EPS growth %
     */
    eps_growth_percent?: string | null;
    /**
     * Asset turnover LTM
     */
    asset_turnover_ltm?: string | null;
    /**
     * ROA trailing
     */
    roa_trailing?: string | null;
    /**
     * ROE trailing
     */
    roe_trailing?: string | null;
    /**
     * Operating leverage
     */
    operating_leverage?: string | null;
    /**
     * Altman Z-score (manufacturing)
     */
    altman_z_score_manufacturing?: string | null;
    /**
     * Altman Z-score (non-manufacturing)
     */
    altman_z_score_non_manufacturing?: string | null;
    /**
     * EBITDA FY0
     */
    ebitda_fy0?: string | null;
    /**
     * EBITDA FY-1
     */
    ebitda_fy_minus_1?: string | null;
    /**
     * Cash flow operations FY0
     */
    cash_flow_operations_fy0?: string | null;
    /**
     * Cash flow operations FY-1
     */
    cash_flow_operations_fy_minus_1?: string | null;
    /**
     * Interest expense FY0
     */
    interest_expense_fy0?: string | null;
    /**
     * Effective interest rate
     */
    effective_interest_rate?: string | null;
    /**
     * Interest coverage ratio
     */
    interest_coverage_ratio?: string | null;
    /**
     * Debt to total assets
     */
    debt_to_total_assets?: string | null;
    /**
     * Debt to equity
     */
    debt_to_equity?: string | null;
    /**
     * Current ratio
     */
    current_ratio?: string | null;
    /**
     * Quick ratio
     */
    quick_ratio?: string | null;
    /**
     * P/E ratio trailing
     */
    pe_ratio_trailing?: string | null;
    /**
     * P/E ratio consensus
     */
    pe_ratio_consensus?: string | null;
    /**
     * PEG ratio
     */
    peg_ratio?: string | null;
    /**
     * Dividend yield FY0
     */
    dividend_yield_fy0?: string | null;
    /**
     * Dividend payout ratio
     */
    dividend_payout_ratio?: string | null;
    /**
     * Dividend (local currency)
     */
    dividend_local_currency?: string | null;
    /**
     * Dividend 3yr CAGR
     */
    dividend_3yr_cagr?: string | null;
    /**
     * Dividend 5yr CAGR
     */
    dividend_5yr_cagr?: string | null;
    /**
     * Dividend 10yr CAGR
     */
    dividend_10yr_cagr?: string | null;
    readonly created_at: string;
    readonly updated_at: string;
};
export namespace Company {
    /**
     * Stock exchange code (SSE, SZSE, HKEX)
     *
     * * `SSE` - 上海证券交易所
     * * `SZSE` - 深圳证券交易所
     * * `HKEX` - 香港交易所
     */
    export enum exchange {
        SSE = 'SSE',
        SZSE = 'SZSE',
        HKEX = 'HKEX',
    }
}

