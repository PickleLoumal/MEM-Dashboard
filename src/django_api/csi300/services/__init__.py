# CSI300 Services
# 包含 Investment Summary 生成等服务
#
# 注意: 使用延迟导入以支持 CLI 模式 (python -m csi300.services.cli)
# 在 CLI 模式下，Django 需要先初始化才能导入 models

__all__ = [
    # Parser functions
    "extract_ai_content_sections",
    "extract_sources_from_key_takeaways",
    "format_market_cap",
    # Main API
    "generate_company_summary",
    "generate_company_summary_async",
    "get_stock_data_sync",
    "main",
    "parse_business_overview_to_json",
    # Utils
    "safe_decimal",
]


def __getattr__(name: str):
    """延迟导入以支持 CLI 模式"""
    if name in ("generate_company_summary", "generate_company_summary_async", "main"):
        from .generator import generate_company_summary, generate_company_summary_async, main

        return {
            "generate_company_summary": generate_company_summary,
            "generate_company_summary_async": generate_company_summary_async,
            "main": main,
        }[name]

    if name in (
        "extract_ai_content_sections",
        "extract_sources_from_key_takeaways",
        "parse_business_overview_to_json",
    ):
        from .parser import (
            extract_ai_content_sections,
            extract_sources_from_key_takeaways,
            parse_business_overview_to_json,
        )

        return {
            "extract_ai_content_sections": extract_ai_content_sections,
            "extract_sources_from_key_takeaways": extract_sources_from_key_takeaways,
            "parse_business_overview_to_json": parse_business_overview_to_json,
        }[name]

    if name in ("format_market_cap", "get_stock_data_sync", "safe_decimal"):
        from .utils import format_market_cap, get_stock_data_sync, safe_decimal

        return {
            "format_market_cap": format_market_cap,
            "get_stock_data_sync": get_stock_data_sync,
            "safe_decimal": safe_decimal,
        }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
