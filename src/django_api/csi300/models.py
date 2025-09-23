from django.db import models


class CSI300Company(models.Model):
    """CSI300 Company model matching existing database structure"""
    
    # Basic Company Information
    name = models.CharField(max_length=200, help_text="Company name")
    ticker = models.CharField(max_length=20, blank=True, null=True, help_text="Stock ticker")
    im_code = models.CharField(max_length=50, blank=True, null=True, help_text="IM Industry Code")
    industry = models.CharField(max_length=100, blank=True, null=True, help_text="Industry classification")
    sub_industry = models.CharField(max_length=100, blank=True, null=True, help_text="Sub-industry")
    gics_industry = models.CharField(max_length=100, blank=True, null=True, help_text="GICS Industry")
    gics_sub_industry = models.CharField(max_length=100, blank=True, null=True, help_text="GICS Sub-industry")
    
    # Company Details
    naming = models.CharField(max_length=200, blank=True, null=True, help_text="Company naming")
    business_description = models.TextField(blank=True, null=True, help_text="Business description")
    company_info = models.TextField(blank=True, null=True, help_text="Company info")
    directors = models.CharField(max_length=500, blank=True, null=True, help_text="Directors")
    
    # Price Information
    price_local_currency = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="Price in local currency")
    currency = models.CharField(max_length=3, blank=True, null=True, help_text="Currency")
    total_return_2018_to_2025 = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True, help_text="Total return 2018-2025")
    last_trade_date = models.DateField(blank=True, null=True, help_text="Last trade date")
    price_52w_high = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="52-week high")
    price_52w_low = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True, help_text="52-week low")
    
    # Market Cap
    market_cap_local = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Market cap (local)")
    market_cap_usd = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Market cap (USD)")
    
    # Revenue
    total_revenue_local = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Total revenue (local)")
    ltm_revenue_local = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="LTM revenue (local)")
    ntm_revenue_local = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="NTM revenue (local)")
    
    # Assets & Liabilities
    total_assets_local = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Total assets (local)")
    net_assets_local = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Net assets (local)")
    total_debt_local = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Total debt (local)")
    
    # Profitability
    net_profits_fy0 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Net profits FY0")
    operating_margin_trailing = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Operating margin (trailing)")
    operating_profits_per_share = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Operating profits per share")
    
    # Earnings Per Share
    eps_trailing = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="EPS trailing")
    eps_actual_fy0 = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="EPS actual FY0")
    eps_forecast_fy1 = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="EPS forecast FY1")
    eps_growth_percent = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="EPS growth %")
    
    # Financial Ratios
    asset_turnover_ltm = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Asset turnover LTM")
    roa_trailing = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="ROA trailing")
    roe_trailing = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="ROE trailing")
    operating_leverage = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Operating leverage")
    
    # Risk Metrics
    altman_z_score_manufacturing = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Altman Z-score (manufacturing)")
    altman_z_score_non_manufacturing = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Altman Z-score (non-manufacturing)")
    
    # Cash Flow
    ebitda_fy0 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="EBITDA FY0")
    ebitda_fy_minus_1 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="EBITDA FY-1")
    cash_flow_operations_fy0 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Cash flow operations FY0")
    cash_flow_operations_fy_minus_1 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Cash flow operations FY-1")
    
    # Interest & Debt
    interest_expense_fy0 = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, help_text="Interest expense FY0")
    effective_interest_rate = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Effective interest rate")
    interest_coverage_ratio = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Interest coverage ratio")
    debt_to_total_assets = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Debt to total assets")
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Debt to equity")
    
    # Liquidity Ratios
    current_ratio = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Current ratio")
    quick_ratio = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Quick ratio")
    
    # Valuation Ratios
    pe_ratio_trailing = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="P/E ratio trailing")
    pe_ratio_consensus = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="P/E ratio consensus")
    peg_ratio = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="PEG ratio")
    
    # Dividends
    dividend_yield_fy0 = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Dividend yield FY0")
    dividend_payout_ratio = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Dividend payout ratio")
    dividend_local_currency = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Dividend (local currency)")
    dividend_3yr_cagr = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Dividend 3yr CAGR")
    dividend_5yr_cagr = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Dividend 5yr CAGR")
    dividend_10yr_cagr = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Dividend 10yr CAGR")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'csi300_company'
        verbose_name = 'CSI300 Company'
        verbose_name_plural = 'CSI300 Companies'
        ordering = ['ticker']
    
    def __str__(self):
        return f"{self.ticker} - {self.name}"


class CSI300InvestmentSummary(models.Model):
    """CSI300 Investment Summary model"""
    
    company = models.ForeignKey(CSI300Company, on_delete=models.CASCADE, related_name='investment_summaries')
    report_date = models.DateField(help_text="Report date")
    
    # Market Data
    stock_price_previous_close = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Previous close price")
    market_cap_display = models.CharField(max_length=100, blank=True, null=True, help_text="Market cap display format")
    recommended_action = models.CharField(max_length=50, blank=True, null=True, help_text="Investment recommendation")
    recommended_action_detail = models.TextField(blank=True, null=True, help_text="Detailed recommendation")
    
    # Analysis Sections
    business_overview = models.TextField(blank=True, null=True, help_text="Business overview")
    business_performance = models.TextField(blank=True, null=True, help_text="Business performance analysis")
    industry_context = models.TextField(blank=True, null=True, help_text="Industry context")
    financial_stability = models.TextField(blank=True, null=True, help_text="Financial stability analysis")
    key_financials_valuation = models.TextField(blank=True, null=True, help_text="Key financials and valuation")
    big_trends_events = models.TextField(blank=True, null=True, help_text="Big trends and events")
    customer_segments = models.TextField(blank=True, null=True, help_text="Customer segments analysis")
    competitive_landscape = models.TextField(blank=True, null=True, help_text="Competitive landscape")
    risks_anomalies = models.TextField(blank=True, null=True, help_text="Risks and anomalies")
    forecast_outlook = models.TextField(blank=True, null=True, help_text="Forecast and outlook")
    investment_firms_views = models.TextField(blank=True, null=True, help_text="Investment firms views")
    industry_ratio_analysis = models.TextField(blank=True, null=True, help_text="Industry ratio analysis")
    tariffs_supply_chain_risks = models.TextField(blank=True, null=True, help_text="Tariffs and supply chain risks")
    key_takeaways = models.TextField(blank=True, null=True, help_text="Key takeaways")
    sources = models.TextField(blank=True, null=True, help_text="Data sources")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'csi300_investment_summary'
        verbose_name = 'CSI300 Investment Summary'
        verbose_name_plural = 'CSI300 Investment Summaries'
        ordering = ['-report_date']
        unique_together = ['company', 'report_date']
    
    def __str__(self):
        return f"{self.company.ticker} - {self.report_date}"

