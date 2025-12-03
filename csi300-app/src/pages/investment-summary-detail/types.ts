export interface InvestmentSummary {
  company_name: string;
  report_date: string;
  stock_price_previous_close: number | null;
  market_cap_display: string;
  recommended_action: string;
  industry: string;
  im_sector: string;
  
  // Markdown content sections
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
  recommended_action_detail: string;
  industry_ratio_analysis: string;
  tariffs_supply_chain_risks?: string;
  key_takeaways: string;
  sources: string;
}

