/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * CSI300 Investment Summary serializer
 */
export type CSI300InvestmentSummary = {
    readonly id: number;
    readonly company_name: string;
    readonly company_ticker: string;
    readonly im_sector: string;
    readonly industry: string;
    /**
     * Report date
     */
    report_date: string;
    /**
     * Previous close price
     */
    stock_price_previous_close?: string;
    /**
     * Market cap display format
     */
    market_cap_display?: string;
    /**
     * Investment recommendation
     */
    recommended_action?: string;
    /**
     * Detailed recommendation
     */
    recommended_action_detail?: string;
    /**
     * Business overview
     */
    business_overview?: string;
    /**
     * Business performance analysis
     */
    business_performance?: string;
    /**
     * Industry context
     */
    industry_context?: string;
    /**
     * Financial stability analysis
     */
    financial_stability?: string;
    /**
     * Key financials and valuation
     */
    key_financials_valuation?: string;
    /**
     * Big trends and events
     */
    big_trends_events?: string;
    /**
     * Customer segments analysis
     */
    customer_segments?: string;
    /**
     * Competitive landscape
     */
    competitive_landscape?: string;
    /**
     * Risks and anomalies
     */
    risks_anomalies?: string;
    /**
     * Forecast and outlook
     */
    forecast_outlook?: string;
    /**
     * Investment firms views
     */
    investment_firms_views?: string;
    /**
     * Industry ratio analysis
     */
    industry_ratio_analysis?: string;
    /**
     * Tariffs and supply chain risks
     */
    tariffs_supply_chain_risks?: string;
    /**
     * Key takeaways
     */
    key_takeaways?: string;
    /**
     * Data sources
     */
    sources?: string;
    readonly created_at: string;
    readonly updated_at: string;
    company: number;
};

