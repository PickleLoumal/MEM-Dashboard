# ==========================================
# Refinitiv 数据 Serializers
# 用于 OpenAPI schema 生成和 API 响应
# ==========================================

from rest_framework import serializers


class SegmentDataSerializer(serializers.Serializer):
    """业务分部数据序列化器。"""

    name = serializers.CharField(help_text="分部名称")
    description = serializers.CharField(allow_null=True, required=False, help_text="分部描述")
    revenue_pct = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True, required=False, help_text="占总收入百分比"
    )
    gross_margin = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True, required=False, help_text="毛利率"
    )
    operating_margin = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True, required=False, help_text="营业利润率"
    )
    profit_contribution = serializers.DecimalField(
        max_digits=5, decimal_places=2, allow_null=True, required=False, help_text="利润贡献百分比"
    )


class AnalystConsensusSerializer(serializers.Serializer):
    """分析师一致预期序列化器。"""

    consensus_rating = serializers.CharField(allow_null=True, required=False, help_text="共识评级 (Buy/Hold/Sell)")
    buy_pct = serializers.IntegerField(allow_null=True, required=False, help_text="买入评级占比")
    hold_pct = serializers.IntegerField(allow_null=True, required=False, help_text="持有评级占比")
    sell_pct = serializers.IntegerField(allow_null=True, required=False, help_text="卖出评级占比")
    num_analysts = serializers.IntegerField(allow_null=True, required=False, help_text="分析师数量")
    target_price_low = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, required=False, help_text="目标价最低"
    )
    target_price_high = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, required=False, help_text="目标价最高"
    )
    target_price_avg = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, required=False, help_text="目标价平均"
    )
    target_price_median = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True, required=False, help_text="目标价中位数"
    )
    upside_pct = serializers.DecimalField(
        max_digits=6, decimal_places=2, allow_null=True, required=False, help_text="上涨潜力百分比"
    )


class KeyMetricsSerializer(serializers.Serializer):
    """关键财务指标序列化器。"""

    fiscal_year = serializers.CharField(allow_null=True, required=False, help_text="财年")
    total_revenue = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="总收入"
    )
    total_revenue_yoy = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="收入同比增长率"
    )
    operating_income = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="营业收入"
    )
    operating_income_yoy = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="营业收入同比增长率"
    )
    net_income = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="净利润"
    )
    net_income_yoy = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="净利润同比增长率"
    )
    operating_margin = serializers.DecimalField(
        max_digits=6, decimal_places=4, allow_null=True, required=False, help_text="营业利润率"
    )
    operating_margin_yoy = serializers.DecimalField(
        max_digits=6, decimal_places=4, allow_null=True, required=False, help_text="营业利润率同比变化"
    )
    gross_margin = serializers.DecimalField(
        max_digits=6, decimal_places=4, allow_null=True, required=False, help_text="毛利率"
    )
    net_margin = serializers.DecimalField(
        max_digits=6, decimal_places=4, allow_null=True, required=False, help_text="净利率"
    )


class ValuationMetricsSerializer(serializers.Serializer):
    """估值指标序列化器。"""

    pe_ttm = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True, required=False, help_text="市盈率 (TTM)"
    )
    pe_forward = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True, required=False, help_text="预测市盈率"
    )
    peg_ratio = serializers.DecimalField(
        max_digits=8, decimal_places=2, allow_null=True, required=False, help_text="PEG 比率"
    )
    pb_ratio = serializers.DecimalField(
        max_digits=8, decimal_places=2, allow_null=True, required=False, help_text="市净率"
    )
    ev_ebitda = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True, required=False, help_text="EV/EBITDA"
    )
    dividend_yield = serializers.DecimalField(
        max_digits=6, decimal_places=4, allow_null=True, required=False, help_text="股息收益率"
    )


class BalanceSheetMetricsSerializer(serializers.Serializer):
    """资产负债表指标序列化器。"""

    total_debt = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="总负债"
    )
    total_equity = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="总权益"
    )
    debt_to_equity = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="负债权益比"
    )
    current_ratio = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="流动比率"
    )
    quick_ratio = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="速动比率"
    )
    interest_coverage = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True, required=False, help_text="利息覆盖率"
    )


class ProfitabilityMetricsSerializer(serializers.Serializer):
    """盈利能力指标序列化器。"""

    roe = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="净资产收益率"
    )
    roa = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="总资产收益率"
    )
    roic = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="投入资本收益率"
    )
    operating_cash_flow = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="经营现金流"
    )
    free_cash_flow = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="自由现金流"
    )
    capex = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="资本支出"
    )


class PricingDataSerializer(serializers.Serializer):
    """股价数据序列化器。"""

    price_close = serializers.DecimalField(
        max_digits=12, decimal_places=4, allow_null=True, required=False, help_text="收盘价"
    )
    price_date = serializers.CharField(allow_null=True, required=False, help_text="价格日期")
    week_52_high = serializers.DecimalField(
        max_digits=12, decimal_places=4, allow_null=True, required=False, help_text="52周最高"
    )
    week_52_low = serializers.DecimalField(
        max_digits=12, decimal_places=4, allow_null=True, required=False, help_text="52周最低"
    )
    market_cap = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="市值"
    )
    market_cap_display = serializers.CharField(
        allow_null=True, required=False, help_text="市值显示格式 (e.g., '132.10B CNY')"
    )
    currency = serializers.CharField(default="CNY", help_text="货币")


class FinancialContextSerializer(serializers.Serializer):
    """
    Investment Summary 完整财务上下文序列化器。

    用于 API 响应和 OpenAPI schema 生成。
    """

    ric = serializers.CharField(help_text="Reuters Instrument Code")
    company_name = serializers.CharField(allow_null=True, required=False, help_text="公司名称")
    ticker = serializers.CharField(allow_null=True, required=False, help_text="股票代码")

    # 核心数据
    pricing = PricingDataSerializer(allow_null=True, required=False, help_text="股价数据")
    key_metrics = KeyMetricsSerializer(allow_null=True, required=False, help_text="关键指标")
    valuation = ValuationMetricsSerializer(allow_null=True, required=False, help_text="估值指标")
    balance_sheet = BalanceSheetMetricsSerializer(allow_null=True, required=False, help_text="资产负债表指标")
    profitability = ProfitabilityMetricsSerializer(allow_null=True, required=False, help_text="盈利能力指标")

    # 分析师预期
    analyst_consensus = AnalystConsensusSerializer(allow_null=True, required=False, help_text="分析师共识")

    # 分部业绩
    segments = SegmentDataSerializer(many=True, required=False, help_text="业务分部")

    # 预测数据
    revenue_forecast = serializers.DecimalField(
        max_digits=18, decimal_places=2, allow_null=True, required=False, help_text="收入预测"
    )
    revenue_forecast_yoy = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="收入预测同比"
    )
    eps_forecast = serializers.DecimalField(
        max_digits=12, decimal_places=4, allow_null=True, required=False, help_text="EPS 预测"
    )
    eps_forecast_yoy = serializers.DecimalField(
        max_digits=8, decimal_places=4, allow_null=True, required=False, help_text="EPS 预测同比"
    )

    # 元数据
    data_source = serializers.CharField(default="Refinitiv", help_text="数据来源")
    fetch_timestamp = serializers.CharField(allow_null=True, required=False, help_text="获取时间")
    errors = serializers.ListField(
        child=serializers.CharField(), required=False, help_text="错误信息列表"
    )


class RefinitivConnectionStatusSerializer(serializers.Serializer):
    """Refinitiv 连接状态序列化器。"""

    authenticated = serializers.BooleanField(help_text="是否已认证")
    credentials_configured = serializers.BooleanField(help_text="凭证是否已配置")
    error = serializers.CharField(allow_null=True, required=False, help_text="错误信息")


__all__ = [
    "AnalystConsensusSerializer",
    "BalanceSheetMetricsSerializer",
    "FinancialContextSerializer",
    "KeyMetricsSerializer",
    "PricingDataSerializer",
    "ProfitabilityMetricsSerializer",
    "RefinitivConnectionStatusSerializer",
    "SegmentDataSerializer",
    "ValuationMetricsSerializer",
]

