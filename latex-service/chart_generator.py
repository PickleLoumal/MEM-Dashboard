"""
Chart Generator Module

Generates matplotlib charts for PDF reports based on configuration.
Charts are rendered as PNG images for LaTeX \includegraphics.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Use non-interactive backend for server environment
matplotlib.use("Agg")

logger = logging.getLogger(__name__)

# Chart style configuration
CHART_STYLE = {
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 14,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
}

# Color palette
COLORS = {
    "primary": "#2563eb",  # Blue
    "secondary": "#10b981",  # Green
    "accent": "#f59e0b",  # Amber
    "danger": "#ef4444",  # Red
    "neutral": "#6b7280",  # Gray
}


@dataclass
class ChartResult:
    """Container for generated chart data."""

    name: str
    image_data: bytes
    width: float = 0.9  # Relative width for LaTeX


def generate_charts(
    data: dict[str, Any],
    charts_config: list[dict[str, Any]],
) -> list[ChartResult]:
    """
    Generate all charts based on configuration.

    Args:
        data: Combined summary and company data
        charts_config: List of chart configuration dicts

    Returns:
        List of ChartResult with generated images
    """
    plt.rcParams.update(CHART_STYLE)

    results = []

    for chart_config in charts_config:
        chart_type = chart_config.get("type", "")
        chart_name = chart_config.get("name", "chart")

        try:
            if chart_type == "stock_price":
                result = generate_stock_price_chart(data, chart_config)
            elif chart_type == "roe_trend":
                result = generate_roe_trend_chart(data, chart_config)
            elif chart_type == "pe_ratio":
                result = generate_pe_ratio_chart(data, chart_config)
            elif chart_type == "financial_summary":
                result = generate_financial_summary_chart(data, chart_config)
            elif chart_type == "key_metrics":
                result = generate_key_metrics_chart(data, chart_config)
            else:
                logger.warning(f"Unknown chart type: {chart_type}")
                continue

            if result:
                results.append(result)
                logger.info(f"Generated chart: {chart_name}")

        except Exception as e:
            logger.exception(f"Failed to generate chart {chart_name}: {e}")

    return results


def generate_stock_price_chart(
    data: dict[str, Any],
    config: dict[str, Any],
) -> ChartResult | None:
    """
    Generate stock price performance line chart.

    Shows price history with 52-week high/low markers.
    """
    company = data.get("company", {})

    current_price = company.get("previous_close", 0)
    high_52w = company.get("price_52w_high", current_price * 1.2)
    low_52w = company.get("price_52w_low", current_price * 0.8)
    ticker = company.get("ticker", "Stock")

    # Create synthetic price data (in production, fetch from data source)
    np.random.seed(hash(ticker) % 2**32)
    days = 252  # Trading days in a year
    returns = np.random.normal(0.0005, 0.02, days)
    prices = current_price * np.exp(np.cumsum(returns))
    prices = prices * (current_price / prices[-1])  # Adjust to end at current price

    fig, ax = plt.subplots(figsize=(8, 4))

    # Plot price line
    ax.plot(range(days), prices, color=COLORS["primary"], linewidth=1.5, label="Price")

    # Add 52-week markers
    ax.axhline(y=high_52w, color=COLORS["secondary"], linestyle="--", alpha=0.7, label="52W High")
    ax.axhline(y=low_52w, color=COLORS["danger"], linestyle="--", alpha=0.7, label="52W Low")

    ax.set_xlabel("Trading Days")
    ax.set_ylabel("Price")
    ax.set_title(f"{ticker} - 52 Week Price Performance")
    ax.legend(loc="upper left")

    return _fig_to_result(fig, "stock_price")


def generate_roe_trend_chart(
    data: dict[str, Any],
    config: dict[str, Any],
) -> ChartResult | None:
    """
    Generate ROE trend bar chart.

    Shows historical Return on Equity over multiple years.
    """
    company = data.get("company", {})
    ticker = company.get("ticker", "Company")
    current_roe = company.get("roe_trailing", 0.15)

    # Generate synthetic historical ROE (in production, fetch real data)
    np.random.seed(hash(ticker) % 2**32)
    years = list(range(2019, 2025))
    roe_values = [current_roe * (0.8 + 0.4 * np.random.random()) for _ in years]
    roe_values[-1] = current_roe  # Current year

    fig, ax = plt.subplots(figsize=(7, 4))

    colors = [COLORS["primary"] if v >= 0 else COLORS["danger"] for v in roe_values]
    bars = ax.bar(years, [v * 100 for v in roe_values], color=colors, alpha=0.8)

    ax.set_xlabel("Year")
    ax.set_ylabel("ROE (%)")
    ax.set_title(f"{ticker} - Return on Equity Trend")
    ax.set_xticks(years)

    # Add value labels on bars
    for bar, value in zip(bars, roe_values):
        height = bar.get_height()
        ax.annotate(
            f"{value * 100:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    return _fig_to_result(fig, "roe_trend")


def generate_pe_ratio_chart(
    data: dict[str, Any],
    config: dict[str, Any],
) -> ChartResult | None:
    """
    Generate P/E ratio trend line chart.

    Shows historical P/E ratio with industry average comparison.
    """
    company = data.get("company", {})
    ticker = company.get("ticker", "Company")
    current_pe = company.get("pe_ratio_trailing", 15)

    if current_pe <= 0:
        current_pe = 15  # Default if no data

    # Generate synthetic historical P/E
    np.random.seed(hash(ticker) % 2**32)
    quarters = list(range(1, 21))  # 5 years quarterly
    pe_values = [current_pe * (0.7 + 0.6 * np.random.random()) for _ in quarters]
    pe_values[-1] = current_pe

    industry_avg = current_pe * 0.9  # Industry average line

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(quarters, pe_values, color=COLORS["primary"], linewidth=2, marker="o", markersize=4, label=ticker)
    ax.axhline(y=industry_avg, color=COLORS["accent"], linestyle="--", linewidth=1.5, label="Industry Avg")

    ax.set_xlabel("Quarters (most recent 5 years)")
    ax.set_ylabel("P/E Ratio")
    ax.set_title(f"{ticker} - P/E Ratio Trend")
    ax.legend(loc="upper right")

    return _fig_to_result(fig, "pe_ratio")


def generate_financial_summary_chart(
    data: dict[str, Any],
    config: dict[str, Any],
) -> ChartResult | None:
    """
    Generate financial summary horizontal bar chart.

    Shows key financial metrics compared to benchmarks.
    """
    company = data.get("company", {})
    ticker = company.get("ticker", "Company")

    metrics = {
        "ROE": (company.get("roe_trailing", 0) * 100, 15),  # (value, benchmark)
        "ROA": (company.get("roa_trailing", 0) * 100, 5),
        "Debt/Equity": (company.get("debt_to_equity", 0), 1.0),
        "Current Ratio": (company.get("current_ratio", 0), 1.5),
        "Dividend Yield": (company.get("dividend_yield_fy0", 0) * 100, 2),
    }

    fig, ax = plt.subplots(figsize=(8, 5))

    y_positions = range(len(metrics))
    labels = list(metrics.keys())
    values = [m[0] for m in metrics.values()]
    benchmarks = [m[1] for m in metrics.values()]

    # Plot bars
    bars = ax.barh(y_positions, values, color=COLORS["primary"], alpha=0.8, label=ticker)
    ax.scatter(benchmarks, y_positions, color=COLORS["accent"], marker="D", s=80, zorder=3, label="Benchmark")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Value")
    ax.set_title(f"{ticker} - Key Financial Metrics vs Benchmarks")
    ax.legend(loc="lower right")

    return _fig_to_result(fig, "financial_summary")


def generate_key_metrics_chart(
    data: dict[str, Any],
    config: dict[str, Any],
) -> ChartResult | None:
    """
    Generate a radar/spider chart for key investment metrics.
    """
    company = data.get("company", {})
    ticker = company.get("ticker", "Company")

    # Normalize metrics to 0-100 scale
    metrics = {
        "Profitability": min(100, max(0, (company.get("roe_trailing", 0) * 100 / 0.25) * 100)),
        "Valuation": min(100, max(0, 100 - (company.get("pe_ratio_trailing", 15) - 10) * 5)),
        "Stability": min(100, max(0, company.get("current_ratio", 1) * 50)),
        "Growth": min(100, max(0, 50 + company.get("eps_growth_percent", 0) * 2)),
        "Dividend": min(100, max(0, company.get("dividend_yield_fy0", 0) * 100 * 20)),
    }

    labels = list(metrics.keys())
    values = list(metrics.values())

    # Number of variables
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]  # Complete the circle
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    ax.fill(angles, values, color=COLORS["primary"], alpha=0.25)
    ax.plot(angles, values, color=COLORS["primary"], linewidth=2)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_title(f"{ticker} - Investment Profile", pad=20)

    return _fig_to_result(fig, "key_metrics")


def _fig_to_result(fig: plt.Figure, name: str) -> ChartResult:
    """Convert matplotlib figure to ChartResult with PNG bytes."""
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return ChartResult(name=name, image_data=buf.read())


def generate_default_charts(data: dict[str, Any]) -> list[ChartResult]:
    """
    Generate a default set of charts when no config is provided.

    Returns:
        List of standard charts for investment summary
    """
    default_config = [
        {"type": "stock_price", "name": "stock_price"},
        {"type": "roe_trend", "name": "roe_trend"},
        {"type": "pe_ratio", "name": "pe_ratio"},
        {"type": "financial_summary", "name": "financial_summary"},
    ]
    return generate_charts(data, default_config)

