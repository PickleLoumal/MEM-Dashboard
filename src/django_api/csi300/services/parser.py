"""
Investment Summary Parser Module

正则表达式解析器 - 用于从 AI 生成的 Markdown 内容中提取结构化数据。
"""

import json
import logging
import re
import textwrap
from typing import Any

logger = logging.getLogger(__name__)

# ==========================================
# 预编译正则表达式 (模块级别，只编译一次)
# ==========================================

# Section 正则表达式 - 必须匹配标题格式（以 # 开头或在行首作为独立标题）
SECTION_PREFIX = r"(?:SECTION\s*\d+\s*:\s*)?"  # 匹配可选的 "SECTION 2: " 前缀

SECTION_PATTERNS = {
    "recommended_action": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Recommended Action.*?(Buy|Hold|Sell)",
        re.IGNORECASE | re.DOTALL,
    ),
    "recommended_action_section": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Recommended Action.*?(?=\n#|\Z)", re.IGNORECASE | re.DOTALL
    ),
    "business_overview": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Business Overview.*?(?=\n#|\Z)", re.IGNORECASE | re.DOTALL
    ),
    "business_performance": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Business Performance.*?(?=\n#|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
    "industry_context": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Industry context.*?(?=\n#|\Z)", re.IGNORECASE | re.DOTALL
    ),
    "financial_stability": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Financial Stability.*?(?=\n#|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
    "key_financials": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Key Financials.*?(?=\n#|\Z)", re.IGNORECASE | re.DOTALL
    ),
    "big_trends": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Big Trends.*?(?=\n#|\Z)", re.IGNORECASE | re.DOTALL
    ),
    "customer_segments": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Customer Segments.*?(?=\n#|\Z)", re.IGNORECASE | re.DOTALL
    ),
    "competitive_landscape": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Competitive Landscape.*?(?=\n#|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
    "risks_anomalies": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Risks and anomalies.*?(?=\n#|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
    "forecast_outlook": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Forecast and outlook.*?(?=\n#|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
    "investment_firms": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Leading Investment Firms.*?(?=\n#|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
    "industry_ratio": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Industry Ratio.*?(?=\n#|\Z)", re.IGNORECASE | re.DOTALL
    ),
    "key_takeaways": re.compile(
        rf"(?:^|\n)#+?\s*{SECTION_PREFIX}Key Takeaways.*?(?=\n#+?\s*(?:SECTION\s*\d+\s*:\s*)?Sources|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
    "sources": re.compile(
        r"(?:^|\n)#+?\s*(?:SECTION\s*\d+\s*:\s*)?Sources?\s*(?:Cited)?\s*:?\s*\n(.*?)(?:\n---|\Z)",
        re.IGNORECASE | re.DOTALL,
    ),
}

HEADER_CLEANUP_PATTERN = re.compile(r"^#+.*?\n")

# Pattern to extract sources from key_takeaways content (when embedded)
SOURCES_IN_CONTENT_PATTERN = re.compile(
    r"(?:Sources?\s*Cited?\s*:?\s*\n)(.*?)(?:\n\n\((?:Word|Total word)\s+count|$)",
    re.IGNORECASE | re.DOTALL,
)

# ==========================================
# Business Overview 结构化解析正则
# ==========================================

BO_PATTERNS = {
    "fiscal_year": re.compile(
        r"(?:FY\s?(\d{4})|fiscal year[- ]?end[:\s]*([A-Za-z]+\s+\d{1,2}))", re.IGNORECASE
    ),
    "revenue": re.compile(
        r"(?:total\s+)?(?:revenue|sales)\s+(?:of\s+)?"
        r"([^\s,]+(?:\s+(?:CNY|USD|RMB|billion|million|B|M))+|"
        r"(?:CNY|USD|RMB|\$)\s*[\d.]+\s*(?:billion|million|B|M)?)",
        re.IGNORECASE,
    ),
    "sales_standalone": re.compile(
        r"(?:^|[;:,]\s*)sales\s+([\d.]+\s*[BMT]?\s*(?:CNY|USD|RMB|billion|million)?)", re.IGNORECASE
    ),
    "operating_income": re.compile(
        r"operating\s+income\s+(?:of\s+)?"
        r"([^\s,]+(?:\s+(?:CNY|USD|RMB|billion|million|B|M))+|"
        r"(?:CNY|USD|RMB|\$)\s*[\d.]+\s*(?:billion|million|B|M)?)",
        re.IGNORECASE,
    ),
    "net_income": re.compile(
        r"net\s+(?:income|profit)\s+(?:of\s+)?"
        r"([^\s,]+(?:\s+(?:CNY|USD|RMB|billion|million|B|M))+|"
        r"(?:CNY|USD|RMB|\$)\s*[\d.]+\s*(?:billion|million|B|M)?)",
        re.IGNORECASE,
    ),
    "nim": re.compile(
        r"(?:net\s+interest\s+margin|NIM)\s*(?:\(NIM\))?\s*(?:of\s+)?([\d.]+%)", re.IGNORECASE
    ),
    "operating_margin": re.compile(
        r"(?:operating\s+)?margins?\s+(?:of\s+)?(?:~|about\s+|approximately\s+)?([\d.]+%)",
        re.IGNORECASE,
    ),
    "division_contribution": re.compile(
        r"([A-Za-z][A-Za-z\s&]+?)\s+contributes?\s+([\d.]+%)\s+(?:of\s+)?(?:total\s+)?sales\s*"
        r"(?:\((?:gross\s+)?(?:profit\s+)?margin\s+([\d.]+%)?"
        r"(?:,?\s*([\d.]+%)\s+(?:of\s+)?(?:group\s+)?profits?)?\))?",
        re.IGNORECASE,
    ),
    "division_parenthesis": re.compile(
        r"([A-Z][A-Za-z\s&]+?)\s*\([^)]*?(\d+%)\s+(?:of\s+)?(?:FY\d{4}\s+)?sales"
        r"[^)]*?(?:(\d+%)\s+(?:gross\s+)?margin)?[^)]*\)",
        re.IGNORECASE,
    ),
    "division_simple": re.compile(
        r"([A-Z][A-Za-z\s&]+?)\s*\((\d+%)\s+(?:of\s+)?sales(?:,\s*(\d+%)\s+margin)?\)",
        re.IGNORECASE,
    ),
    "division_def": re.compile(
        r"([A-Z][A-Za-z\s&]+?)\s*\((?:e\.g\.,?\s*)?([^)]+)\)", re.IGNORECASE
    ),
}


def extract_ai_content_sections(content: str) -> dict[str, str]:
    """从AI返回的Markdown内容中提取各个部分 (使用预编译正则)"""
    # 统一去除多行字符串的公共缩进
    content = textwrap.dedent(content)
    sections = {}

    for key, pattern in SECTION_PATTERNS.items():
        try:
            match = pattern.search(content)
            if match:
                text = match.group(0).strip()
                # 清理前导换行符和 # 标题标记
                text = text.lstrip("\n")
                text = HEADER_CLEANUP_PATTERN.sub("", text).strip()

                if key == "recommended_action":
                    text = match.group(1)
                elif key == "sources":
                    # For sources, we want only the captured group
                    text = match.group(1).strip() if match.lastindex and match.group(1) else text
                sections[key] = text
        except Exception:
            sections[key] = ""

    return sections


def extract_sources_from_key_takeaways(key_takeaways: str) -> tuple[str, str]:
    """
    从 key_takeaways 内容中提取 Sources 部分。

    Returns:
        tuple: (cleaned_key_takeaways, extracted_sources)
    """
    if not key_takeaways:
        return "", ""

    match = SOURCES_IN_CONTENT_PATTERN.search(key_takeaways)
    if match:
        sources = match.group(1).strip()
        # Remove sources section and word count from key_takeaways
        cleaned = key_takeaways[: match.start()].strip()
        # Also clean up any trailing word count notes
        cleaned = re.sub(
            r"\((?:Word|Total word)\s+count:.*?\)$", "", cleaned, flags=re.IGNORECASE
        ).strip()
        return cleaned, sources

    # No embedded sources found
    return key_takeaways, ""


def _parse_with_regex(raw_text: str, company_name: str = "") -> dict[str, Any]:
    """使用正则表达式从文本中提取结构化数据（回退方案）"""
    parsed = {
        "company_name": company_name,
        "fiscal_year": None,
        "fiscal_year_end": None,
        "key_metrics": {},
        "divisions": [],
    }

    # 提取财年
    fy_match = BO_PATTERNS["fiscal_year"].search(raw_text)
    if fy_match:
        parsed["fiscal_year"] = fy_match.group(1) or None
        parsed["fiscal_year_end"] = fy_match.group(2) or None

    # 提取关键财务指标
    revenue_match = BO_PATTERNS["revenue"].search(raw_text)
    if revenue_match:
        parsed["key_metrics"]["total_revenue"] = revenue_match.group(1).strip()
    else:
        sales_match = BO_PATTERNS["sales_standalone"].search(raw_text)
        if sales_match:
            parsed["key_metrics"]["total_revenue"] = sales_match.group(1).strip()

    op_income_match = BO_PATTERNS["operating_income"].search(raw_text)
    if op_income_match:
        parsed["key_metrics"]["operating_income"] = op_income_match.group(1).strip()

    net_income_match = BO_PATTERNS["net_income"].search(raw_text)
    if net_income_match:
        parsed["key_metrics"]["net_income"] = net_income_match.group(1).strip()

    nim_match = BO_PATTERNS["nim"].search(raw_text)
    if nim_match:
        parsed["key_metrics"]["net_interest_margin"] = nim_match.group(1).strip()

    margin_match = BO_PATTERNS["operating_margin"].search(raw_text)
    if margin_match:
        parsed["key_metrics"]["operating_margin"] = margin_match.group(1).strip()

    # 提取部门数据
    added_divisions = set()

    for match in BO_PATTERNS["division_parenthesis"].finditer(raw_text):
        div_name = match.group(1).strip()
        sales_pct = match.group(2)
        margin = match.group(3) if len(match.groups()) > 2 and match.group(3) else None

        div_key = div_name.lower()
        if div_key not in added_divisions and len(div_name) > 3:
            parsed["divisions"].append(
                {
                    "name": div_name,
                    "description": "",
                    "sales_percentage": sales_pct,
                    "gross_profit_margin": margin,
                    "profit_percentage": None,
                }
            )
            added_divisions.add(div_key)

    return parsed


def parse_business_overview_to_json(raw_text: str, company_name: str = "") -> str:
    """
    将 Business Overview 原始文本解析为结构化 JSON 字符串。
    优先提取 AI 生成的 JSON 代码块（支持多种格式），
    如果没有则回退到正则表达式解析。
    """
    if not raw_text or not raw_text.strip():
        return json.dumps({"raw_text": "", "parsed": None}, ensure_ascii=False)

    # 尝试提取 AI 生成的 JSON 代码块（支持多种格式）
    # 1. ```business_overview_data ... ```
    # 2. ```json ... ```
    # 3. ``` ... ``` (无语言标识但内容是JSON)
    # 注意：使用 (.*?) 匹配到代码块结束标记，而不是 (\{.*?\}) 避免嵌套 JSON 截断
    json_block_patterns = [
        re.compile(r"```business_overview_data\s*\n?(.*?)\n?```", re.DOTALL | re.IGNORECASE),
        re.compile(r"```json\s*\n?(.*?)\n?```", re.DOTALL | re.IGNORECASE),
        re.compile(r"```\s*\n?(\{[\s\S]*?\})\s*\n?```"),
    ]

    json_match = None
    for pattern in json_block_patterns:
        json_match = pattern.search(raw_text)
        if json_match:
            break

    # 提取纯文本部分（去除所有可能的 JSON 代码块）
    clean_text = raw_text
    for pattern in json_block_patterns:
        clean_text = pattern.sub("", clean_text)
    clean_text = clean_text.strip()

    parsed = {
        "company_name": company_name,
        "fiscal_year": None,
        "fiscal_year_end": None,
        "key_metrics": {},
        "divisions": [],
    }

    if json_match:
        # 从 AI 生成的 JSON 块提取数据
        try:
            json_str = json_match.group(1).strip()
            ai_data = json.loads(json_str)

            # 提取财年
            parsed["fiscal_year"] = ai_data.get("fiscal_year")

            # 提取关键指标
            key_metrics = ai_data.get("key_metrics", {})
            if key_metrics:
                for key, value in key_metrics.items():
                    if value and value != "null":
                        parsed["key_metrics"][key] = value

            # 提取部门数据
            divisions = ai_data.get("divisions", [])
            for div in divisions:
                if isinstance(div, dict) and div.get("name"):
                    parsed["divisions"].append(
                        {
                            "name": div.get("name", ""),
                            "description": div.get("description", ""),
                            "sales_percentage": div.get("sales_pct"),
                            "gross_profit_margin": div.get("gross_margin"),
                            "profit_percentage": div.get("profit_pct"),
                        }
                    )

            logger.info(
                f"Successfully extracted structured data from JSON block: "
                f"{len(parsed['key_metrics'])} metrics, {len(parsed['divisions'])} divisions"
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"JSON block parsing failed, falling back to regex: {e}")
            parsed = _parse_with_regex(raw_text, company_name)
    else:
        # 没有 JSON 块，使用正则解析
        parsed = _parse_with_regex(raw_text, company_name)

    result = {"raw_text": clean_text if clean_text else raw_text, "parsed": parsed}

    return json.dumps(result, ensure_ascii=False, indent=None)


def parse_analyst_consensus(investment_firms_content: str) -> dict[str, Any] | None:
    """
    从 Investment Firms 内容中提取 analyst_consensus JSON 块。

    Returns:
        dict with consensus data or None if not found
    """
    if not investment_firms_content:
        return None

    consensus_pattern = re.compile(
        r"```analyst_consensus\s*\n?(.*?)\n?```", re.DOTALL | re.IGNORECASE
    )
    match = consensus_pattern.search(investment_firms_content)

    if not match:
        return None

    try:
        json_str = match.group(1).strip()
        consensus_data = json.loads(json_str)

        # Validate required fields
        required_fields = ["consensus_rating", "buy_pct", "hold_pct", "sell_pct"]
        if all(field in consensus_data for field in required_fields):
            logger.info(
                f"Successfully extracted analyst consensus: {consensus_data.get('consensus_rating')}"
            )
            return consensus_data
        logger.warning("Analyst consensus JSON missing required fields")
        return None

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Failed to parse analyst_consensus JSON: {e}")
        return None


def extract_risk_severity(risks_content: str) -> list[dict[str, str]]:
    """
    从 Risks and Anomalies 内容中提取带严重程度的风险列表。

    Returns:
        list of dicts with 'text' and 'severity' keys
    """
    if not risks_content:
        return []

    risks = []
    # Pattern to match [HIGH], [MEDIUM], [LOW] prefixed risks
    severity_pattern = re.compile(
        r"\*?\*?\[?(HIGH|MEDIUM|LOW)\]?\*?\*?\s*[-:]*\s*(.+?)(?=\n\*?\*?\[?(?:HIGH|MEDIUM|LOW)|\n\n|\Z)",
        re.IGNORECASE | re.DOTALL,
    )

    for match in severity_pattern.finditer(risks_content):
        severity = match.group(1).upper()
        text = match.group(2).strip()
        # Clean up markdown formatting
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\s+", " ", text).strip()

        if text and len(text) > 20:
            risks.append(
                {
                    "text": text[:200] + ("..." if len(text) > 200 else ""),
                    "severity": severity.lower(),
                }
            )

    # If no severity markers found, fall back to extracting bullet points
    if not risks:
        bullet_pattern = re.compile(r"[-•●]\s*(.+?)(?=\n[-•●]|\n\n|\Z)", re.DOTALL)
        for match in bullet_pattern.finditer(risks_content):
            text = match.group(1).strip()
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
            text = re.sub(r"\s+", " ", text).strip()

            if text and len(text) > 20:
                # Default to medium severity if not specified
                risks.append(
                    {"text": text[:200] + ("..." if len(text) > 200 else ""), "severity": "medium"}
                )

    return risks[:5]  # Limit to top 5 risks


__all__ = [
    "BO_PATTERNS",
    "SECTION_PATTERNS",
    "extract_ai_content_sections",
    "extract_risk_severity",
    "extract_sources_from_key_takeaways",
    "parse_analyst_consensus",
    "parse_business_overview_to_json",
]
