# ==========================================
# Prompt 子模块 - 统一导出
# ==========================================
"""
Investment Summary Prompt 模板模块。

使用方式:
    from csi300.services.prompt import PROMPT_TEMPLATE, AI_MODEL, AI_TIMEOUT
"""

from .config import (
    AI_MAX_RETRIES,
    AI_MODEL,
    AI_SYSTEM_PROMPT,
    AI_TIMEOUT,
    AIConfig,
)
from .sections import (
    SECTION_BUSINESS_OVERVIEW,
    SECTION_HEADER,
    SECTION_PERFORMANCE_FINANCIALS,
    SECTION_RECOMMENDATION_TAKEAWAYS,
    SECTION_RISKS_ANALYSTS,
    SECTION_SOURCES,
    SECTION_TRENDS_COMPETITION,
)
from .template import PROMPT_TEMPLATE

__all__ = [
    # AI 配置
    "AI_MAX_RETRIES",
    "AI_MODEL",
    "AI_SYSTEM_PROMPT",
    "AI_TIMEOUT",
    "AIConfig",
    # 主模板
    "PROMPT_TEMPLATE",
    # 段落常量
    "SECTION_BUSINESS_OVERVIEW",
    "SECTION_HEADER",
    "SECTION_PERFORMANCE_FINANCIALS",
    "SECTION_RECOMMENDATION_TAKEAWAYS",
    "SECTION_RISKS_ANALYSTS",
    "SECTION_SOURCES",
    "SECTION_TRENDS_COMPETITION",
]
