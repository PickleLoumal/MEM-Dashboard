# ==========================================
# Refinitiv 数据模型
# 用于 Investment Summary 数据注入
# ==========================================

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class SegmentData:
    """业务分部数据。"""

    name: str
    description: str | None = None
    revenue_pct: Decimal | None = None  # 占总收入百分比
    gross_margin: Decimal | None = None  # 毛利率
    operating_margin: Decimal | None = None  # 营业利润率
    profit_contribution: Decimal | None = None  # 利润贡献百分比


@dataclass
class AnalystConsensus:
    """分析师一致预期数据。"""

    consensus_rating: str | None = None  # Buy/Hold/Sell
    buy_pct: int | None = None
    hold_pct: int | None = None
    sell_pct: int | None = None
    num_analysts: int | None = None
    target_price_low: Decimal | None = None
    target_price_high: Decimal | None = None
    target_price_avg: Decimal | None = None
    target_price_median: Decimal | None = None
    upside_pct: Decimal | None = None


@dataclass
class KeyMetrics:
    """关键财务指标。"""

    fiscal_year: str | None = None
    total_revenue: Decimal | None = None
    total_revenue_yoy: Decimal | None = None  # 同比增长率
    operating_income: Decimal | None = None
    operating_income_yoy: Decimal | None = None
    net_income: Decimal | None = None
    net_income_yoy: Decimal | None = None
    operating_margin: Decimal | None = None
    operating_margin_yoy: Decimal | None = None  # 同比变化 (pp)
    gross_margin: Decimal | None = None
    net_margin: Decimal | None = None


@dataclass
class ValuationMetrics:
    """估值指标。"""

    pe_ttm: Decimal | None = None
    pe_forward: Decimal | None = None
    peg_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    ev_ebitda: Decimal | None = None
    dividend_yield: Decimal | None = None


@dataclass
class BalanceSheetMetrics:
    """资产负债表指标。"""

    total_debt: Decimal | None = None
    total_equity: Decimal | None = None
    debt_to_equity: Decimal | None = None
    current_ratio: Decimal | None = None
    quick_ratio: Decimal | None = None
    interest_coverage: Decimal | None = None


@dataclass
class ProfitabilityMetrics:
    """盈利能力指标。"""

    roe: Decimal | None = None
    roa: Decimal | None = None
    roic: Decimal | None = None
    operating_cash_flow: Decimal | None = None
    free_cash_flow: Decimal | None = None
    capex: Decimal | None = None


@dataclass
class PricingData:
    """股价数据。"""

    price_close: Decimal | None = None
    price_date: str | None = None
    week_52_high: Decimal | None = None
    week_52_low: Decimal | None = None
    market_cap: Decimal | None = None
    market_cap_display: str | None = None  # 格式化显示 (e.g., "132.10B CNY")
    currency: str = "CNY"


@dataclass
class FinancialContext:
    """
    Investment Summary 完整财务上下文。

    用于注入到 AI Prompt 中，确保所有数字来自 Refinitiv 真实数据。
    """

    ric: str
    company_name: str | None = None
    ticker: str | None = None

    # 核心数据
    pricing: PricingData | None = None
    key_metrics: KeyMetrics | None = None
    valuation: ValuationMetrics | None = None
    balance_sheet: BalanceSheetMetrics | None = None
    profitability: ProfitabilityMetrics | None = None

    # 分析师预期
    analyst_consensus: AnalystConsensus | None = None

    # 分部业绩
    segments: list[SegmentData] = field(default_factory=list)

    # 预测数据
    revenue_forecast: Decimal | None = None
    revenue_forecast_yoy: Decimal | None = None
    eps_forecast: Decimal | None = None
    eps_forecast_yoy: Decimal | None = None

    # 元数据
    data_source: str = "Refinitiv"
    fetch_timestamp: str | None = None
    errors: list[str] = field(default_factory=list)

    def to_prompt_context(self) -> str:
        """
        将财务上下文转换为 Prompt 注入格式。

        Returns:
            格式化的上下文字符串，用于插入到 AI Prompt 中。
        """
        lines = [
            "=== OFFICIAL FINANCIAL DATA (SOURCE OF TRUTH) ===",
            "You MUST use the following data. DO NOT use external numbers if they conflict.",
            "",
        ]

        # Pricing
        if self.pricing:
            lines.append("**Market Data:**")
            if self.pricing.price_close:
                lines.append(
                    f"- Stock Price (Previous Close): {self.pricing.price_close} {self.pricing.currency}"
                )
            if self.pricing.market_cap_display:
                lines.append(f"- Market Cap: {self.pricing.market_cap_display}")
            if self.pricing.week_52_high and self.pricing.week_52_low:
                lines.append(
                    f"- 52-Week Range: {self.pricing.week_52_low} - {self.pricing.week_52_high}"
                )
            lines.append("")

        # Key Metrics
        if self.key_metrics:
            lines.append("**Key Financial Metrics:**")
            if self.key_metrics.total_revenue:
                yoy = (
                    f" ({self.key_metrics.total_revenue_yoy:+.1%})"
                    if self.key_metrics.total_revenue_yoy
                    else ""
                )
                lines.append(f"- Total Revenue: {self.key_metrics.total_revenue}{yoy}")
            if self.key_metrics.operating_income:
                yoy = (
                    f" ({self.key_metrics.operating_income_yoy:+.1%})"
                    if self.key_metrics.operating_income_yoy
                    else ""
                )
                lines.append(f"- Operating Income: {self.key_metrics.operating_income}{yoy}")
            if self.key_metrics.net_income:
                yoy = (
                    f" ({self.key_metrics.net_income_yoy:+.1%})"
                    if self.key_metrics.net_income_yoy
                    else ""
                )
                lines.append(f"- Net Income: {self.key_metrics.net_income}{yoy}")
            if self.key_metrics.operating_margin:
                lines.append(f"- Operating Margin: {self.key_metrics.operating_margin:.1%}")
            lines.append("")

        # Valuation
        if self.valuation:
            lines.append("**Valuation Metrics:**")
            if self.valuation.pe_ttm:
                lines.append(f"- P/E (TTM): {self.valuation.pe_ttm:.1f}x")
            if self.valuation.peg_ratio:
                lines.append(f"- PEG Ratio: {self.valuation.peg_ratio:.2f}")
            if self.valuation.dividend_yield:
                lines.append(f"- Dividend Yield: {self.valuation.dividend_yield:.1%}")
            lines.append("")

        # Balance Sheet
        if self.balance_sheet:
            lines.append("**Financial Ratios:**")
            if self.balance_sheet.debt_to_equity:
                lines.append(f"- D/E Ratio: {self.balance_sheet.debt_to_equity:.2f}")
            if self.balance_sheet.current_ratio:
                lines.append(f"- Current Ratio: {self.balance_sheet.current_ratio:.2f}")
            if self.balance_sheet.interest_coverage:
                lines.append(f"- Interest Coverage: {self.balance_sheet.interest_coverage:.1f}x")
            lines.append("")

        # Profitability
        if self.profitability:
            lines.append("**Profitability:**")
            if self.profitability.roe:
                lines.append(f"- ROE: {self.profitability.roe:.1%}")
            if self.profitability.roa:
                lines.append(f"- ROA: {self.profitability.roa:.1%}")
            lines.append("")

        # Segments
        if self.segments:
            lines.append("**Business Segments:**")
            for seg in self.segments:
                seg_line = f"- {seg.name}"
                if seg.revenue_pct:
                    seg_line += f": {seg.revenue_pct:.0%} of revenue"
                if seg.operating_margin:
                    seg_line += f", margin {seg.operating_margin:.1%}"
                lines.append(seg_line)
            lines.append("")

        # Analyst Consensus
        if self.analyst_consensus:
            lines.append("**Analyst Consensus:**")
            if self.analyst_consensus.consensus_rating:
                lines.append(f"- Rating: {self.analyst_consensus.consensus_rating}")
            if self.analyst_consensus.buy_pct is not None:
                lines.append(
                    f"- Distribution: Buy {self.analyst_consensus.buy_pct}%, "
                    f"Hold {self.analyst_consensus.hold_pct}%, "
                    f"Sell {self.analyst_consensus.sell_pct}%"
                )
            if self.analyst_consensus.target_price_avg:
                lines.append(f"- Target Price (Avg): {self.analyst_consensus.target_price_avg}")
            if self.analyst_consensus.upside_pct:
                lines.append(f"- Upside Potential: {self.analyst_consensus.upside_pct:+.1%}")
            lines.append("")

        lines.append("=== END OFFICIAL DATA ===")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """
        将上下文转换为字典格式。

        Returns:
            可序列化的字典
        """
        return {
            "ric": self.ric,
            "company_name": self.company_name,
            "ticker": self.ticker,
            "pricing": {
                "price_close": float(self.pricing.price_close)
                if self.pricing and self.pricing.price_close
                else None,
                "market_cap": self.pricing.market_cap_display if self.pricing else None,
                "52_week_high": float(self.pricing.week_52_high)
                if self.pricing and self.pricing.week_52_high
                else None,
                "52_week_low": float(self.pricing.week_52_low)
                if self.pricing and self.pricing.week_52_low
                else None,
            },
            "key_metrics": {
                "total_revenue": float(self.key_metrics.total_revenue)
                if self.key_metrics and self.key_metrics.total_revenue
                else None,
                "operating_income": float(self.key_metrics.operating_income)
                if self.key_metrics and self.key_metrics.operating_income
                else None,
                "net_income": float(self.key_metrics.net_income)
                if self.key_metrics and self.key_metrics.net_income
                else None,
                "operating_margin": float(self.key_metrics.operating_margin)
                if self.key_metrics and self.key_metrics.operating_margin
                else None,
            },
            "analyst_consensus": {
                "rating": self.analyst_consensus.consensus_rating
                if self.analyst_consensus
                else None,
                "target_price_avg": float(self.analyst_consensus.target_price_avg)
                if self.analyst_consensus and self.analyst_consensus.target_price_avg
                else None,
            },
            "segments": [
                {
                    "name": s.name,
                    "revenue_pct": float(s.revenue_pct) if s.revenue_pct else None,
                    "margin": float(s.operating_margin) if s.operating_margin else None,
                }
                for s in self.segments
            ],
            "data_source": self.data_source,
            "errors": self.errors,
        }


__all__ = [
    "AnalystConsensus",
    "BalanceSheetMetrics",
    "FinancialContext",
    "KeyMetrics",
    "PricingData",
    "ProfitabilityMetrics",
    "SegmentData",
    "ValuationMetrics",
]
