# CSI300 Services
# 包含 Investment Summary 生成等服务

from .generator import generate_company_summary, generate_company_summary_async, main
from .parser import (
    extract_ai_content_sections,
    extract_sources_from_key_takeaways,
    parse_business_overview_to_json,
)
from .utils import safe_decimal, format_market_cap, get_stock_data_sync

__all__ = [
    # Main API
    'generate_company_summary',
    'generate_company_summary_async',
    'main',
    # Parser functions
    'extract_ai_content_sections',
    'extract_sources_from_key_takeaways',
    'parse_business_overview_to_json',
    # Utils
    'safe_decimal',
    'format_market_cap',
    'get_stock_data_sync',
]
