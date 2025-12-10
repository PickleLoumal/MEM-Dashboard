# ==========================================
# Investment Summary Prompt 模板
# 结构化 JSON 指令格式 - 易于维护和修改
# ==========================================

import os

# ==========================================
# AI 模型配置 (从环境变量读取，支持 .env 文件)
# ==========================================
AI_CONFIG = {
    "model": os.environ.get("XAI_MODEL", "grok-4-1-fast-non-reasoning"),
    "system_prompt": os.environ.get(
        "XAI_SYSTEM_PROMPT", "You are Grok, a highly intelligent, helpful AI assistant."
    ),
    "timeout": int(os.environ.get("XAI_TIMEOUT", "120")),
    "max_retries": int(os.environ.get("XAI_MAX_RETRIES", "3")),
}

# 便捷访问
AI_MODEL = AI_CONFIG["model"]
AI_SYSTEM_PROMPT = AI_CONFIG["system_prompt"]
AI_TIMEOUT = AI_CONFIG["timeout"]
AI_MAX_RETRIES = AI_CONFIG["max_retries"]

# ==========================================
# Prompt 指令配置
# ==========================================
PROMPT_INSTRUCTIONS = {
    "meta": {
        "objective": "Generate investment summary (max 5 pages, ~450-600 words)",
        "coverage": [
            "business overview",
            "financial stability",
            "valuation",
            "customer segments",
            "competitive landscape",
            "Buy/Hold/Sell",
        ],
        "disclaimer": "NOT professional investment advice",
    },
    "data_sources": {
        "required": [
            "Company reports (10-K, 10-Q, SEC filings)",
            "MD&A statements, earnings transcripts",
            "Industry reports (McKinsey, Deloitte, EY)",
            "Analyst notes (Piper Sandler, Goldman Sachs)",
        ],
        "rules": [
            "Use ONLY real, accessible URLs (NO placeholders or guessed URLs)",
            "Verify URL structure and domain validity",
            "Versify the URL response is 200 OK",
            "Versify the URL is not a 404 Not Found",
            "Versify the URL is not a 403 Forbidden",
            "Versify the URL is not a 401 Unauthorized",
            "Versify the URL is not a 400 Bad Request",
            "Versify the URL is not a 500 Internal Server Error",
            "Versify the URL is not a 503 Service Unavailable",
            "Versify the URL is not a 502 Bad Gateway",
            "Use most updated data",
            "Must be the exact same sources you have used in the analysis",
            "Do not use any other sources that are not in the analysis",
            "When Doing the analysis, must using the source that you have verified",
        ],
    },
    "constraints": {
        "liquidity": "Current ratio < 1.3 = unhealthy (except cash businesses)",
        "recommendation": "Focus on ONE action with pros/cons",
    },
    "sections": {
        "2_business_overview": {
            "format": "1 paragraph + REQUIRED JSON block",
            "narrative": {
                "scope": "Operations, divisions, products, key financials",
                "product_utility": "2-sentence explanation per product",
                "strengths": ["Technology", "Brand", "Efficiency"],
                "challenges": ["Market Pressures", "Risks"],
                "time_frame": "FY or YTD; specify fiscal year-end",
                "divisions": "Sales % + gross margin for each",
            },
            "json_schema": {
                "fiscal_year": "string",
                "key_metrics": {
                    "total_revenue": "XX.XB CNY",
                    "operating_income": "X.XB CNY",
                    "net_income": "X.XB CNY",
                    "operating_margin": "X.X%",
                },
                "divisions": [
                    {
                        "name": "str",
                        "description": "str",
                        "sales_pct": "XX%",
                        "gross_margin": "XX%",
                        "profit_pct": "XX%",
                    }
                ],
            },
            "json_rules": ["Include ALL divisions", "Use null for unknowns", "REQUIRED"],
        }
    },
}


def build_prompt(
    company_name: str, ticker: str, date: str, stock_price: str, currency: str, market_cap: str
) -> str:
    """构建完整的 prompt 字符串"""

    return f"""{company_name}
{ticker}
As of today [{date}]
Stock Price (Previous Close): {stock_price} {currency}
Market Cap: {market_cap} {currency}

=== INVESTMENT SUMMARY GENERATION INSTRUCTIONS ===

**Objective:** Create a concise investment summary (max 5 pages, ~450-600 words) covering business overview, financial stability, valuation, customer segments, competitive landscape, and Buy/Hold/Sell recommendation.

**Data Sources Required:**
- Company websites, annual/quarterly reports (10-K, 10-Q, SEC filings)
- MD&A statements, earnings transcripts, investor conferences
- Regulatory publications, industry reports (McKinsey, Deloitte, EY)
- Industry-specific ratios vs median
- Analyst notes (Piper Sandler, Goldman Sachs, etc.)
- Provide links to sources used

**Constraints:**
- Current ratio < 1.3 = unhealthy liquidity (except cash businesses like McDonald's, JD.com)
- Focus on ONE recommended action with pros/cons
- This is NOT professional investment advice

---

## SECTION 1: Header
Title: "Investment Summary - [Company Name]"
Include: Date, stock price (previous close), market cap, recommended action (Buy/Hold/Sell), industry name(s)

---

## SECTION 2: Business Overview

**Format:** 1 paragraph narrative + REQUIRED structured data block

**Narrative Requirements:**
- Summarize operations, major divisions, products/services, key financials (FY sales, operating income, margins)
- Include 2-sentence explanation of each product's use to major customer segments
- Highlight strengths (Technology, Brand, Efficiency) and challenges (Market Pressures, Risks)
- Use FY data or YTD; specify fiscal year-end
- For each division: include sales % of total, gross profit margin, and % of operating profit (profit_pct)

**⚠️ CRITICAL - JSON BLOCK PLACEMENT RULES:**
1. **This JSON block MUST ONLY appear IMMEDIATELY after the Business Overview narrative paragraph**
2. **DO NOT output this JSON block in any other section (especially NOT in Section 6: Key Financials)**
3. **DO NOT repeat financial data in JSON format anywhere else**
4. **All other sections must use their specified format (bullet points, paragraphs, etc.)**

**You MUST output this structured JSON block after the Business Overview narrative:**

```business_overview_data
{{
  "fiscal_year": "2024",
  "key_metrics": {{
    "total_revenue": "XX.XB CNY",
    "operating_income": "X.XB CNY",
    "net_income": "X.XB CNY",
    "operating_margin": "X.X%"
  }},
  "divisions": [
    {{"name": "Division 1", "description": "products/services", "sales_pct": "XX%", "gross_margin": "XX%", "profit_pct": "XX%"}},
    {{"name": "Division 2", "description": "products/services", "sales_pct": "XX%", "gross_margin": "XX%", "profit_pct": "XX%"}}
  ]
}}
```

**Rules for JSON block:**
- Replace ALL values with actual researched data
- Include ALL major divisions (not just 2)
- Use null for unknown values
- This block is REQUIRED for data extraction

---

## SECTION 3: Business Performance (bullet points)
- (a) Sales growth past 5 years + next year forecast
- (b) Profit growth past 5 years + next year forecast
- (c) Operating cash flow increase
- (d) Market share and industry ranking

---

## SECTION 4: Industry Context (bullet points, for each industry)
- (a) Product cycle maturity
- (b) Market size and CAGR
- (c) Company's market share and ranking
- (d) 3-year avg sales growth vs industry average
- (e) 3-year avg EPS growth vs industry average
- (f) Debt-to-total assets vs industry average
- (g) Industry cycle phase (expansion/slowing)
- (h) Industry-specific metrics (NOT P/E ratios):
  - Banking: CAR, loan-to-deposit, NIM, NII
  - Semiconductor: Book-to-bill, die size, Yield
  - Airline: Loading factor, breakeven loading factor
  - Offshore drilling: Rig count, day rate

---

## SECTION 5: Financial Stability and Debt Levels (1 paragraph)
Assess: operating cash flow, dividend coverage, capex, liquidity (cash, current ratio)
Evaluate debt: total debt, D/E ratio, debt-to-assets, interest coverage, Altman Z Score vs industry
Highlight problems OR confirm prudent management

---

## SECTION 6: Key Financials and Valuation (bullet points)
**Sales/Profitability:**
- FY sales + YoY change + forecast
- Divisional performance
- Operating margin trends
- Forward guidance (sales, EPS, YoY)

**Valuation Metrics:**
- P/E (TTM vs industry/historical)
- PEG, dividend yield
- 52-week range position

**Financial Ratios:**
- Common debt ratios with risk highlights

**Industry-Specific Metrics:**
- 3 industry-specific metrics
- Company values vs industry average
- Observations and implications

---

## SECTION 7: Big Trends and Big Events (bullet points)
For each business segment: industry trends/events + effects on company

---

## SECTION 8: Customer Segments and Demand Trends (bullet points)
- Major segments by sales (currency, %)
- 2-3 year growth projections per segment + drivers
- Customer complaints + substitutes + switching speed

---

## SECTION 9: Competitive Landscape (bullet points)
- Industry dynamics: CR4, margins, capacity utilization, CAGR, cycle stage
- Key competitors: market shares, operating margins
- Moats: technology, network effects, switching costs, scale, licenses, supply chain, brands
- Top battlefront and company's positioning

---

## SECTION 10: Risks and Anomalies (bullet points)
Unusual findings + concerns + potential resolution

---

## SECTION 11: Forecast and Outlook (bullet points)
Management forecasts, product line growth/decline, reasons, recent earnings surprise

---

## SECTION 12: Leading Investment Firms and Views (bullet points)
- Top firms' ratings + target prices (% upside/downside)
- Consensus rating + average target range

---

## SECTION 13: Recommended Action: [Buy/Hold/Sell]
Select ONE action. Provide:
- Pros (bullet points)
- Cons (bullet points)

---

## SECTION 14: Industry Ratio and Metric Analysis
Important industry ratios: (a) company values, (b) vs industry avg, (c) trends

---

## SECTION 15: Key Takeaways (1 paragraph each)
- Company position, strengths, risks, recommendation rationale
- Monitorable factors for future opportunities
- Any missed key points

---

## SECTION 16: Sources

**⚠️ CRITICAL - FIXED FORMAT REQUIRED:**

List all sources used in THIS EXACT FORMAT (one per line):
```
Source Title | https://example.com/full-url
```

**Example:**
```
Company Annual Report 2024 | https://company.com/investor-relations/annual-report-2024
Goldman Sachs Analyst Note | https://goldmansachs.com/research/company-analysis
McKinsey Industry Report | https://mckinsey.com/industries/report-2025
SEC/CSRC Filings | https://sec.gov/cgi-bin/browse-edgar?company=TICKER
Industry Association Data | https://industry-association.org/data/2025
```

**Rules:**
- ONLY use existing, accessible URLs.
- DO NOT use placeholders or guessed URLs.
- Verify the URL structure (e.g., proper SEC filing links, official IR pages).
- If a specific direct link is unavailable, use the company's main Investor Relations page.
- Format: `Title | URL` (pipe separator)
- One source per line
- Include diverse source types: company filings, analyst reports, industry reports
- Must be the exact same sources you have used in the analysis
- Do not use any other sources that are not in the analysis
---

**Output Format:** Markdown with bullet points for sections 3-12. Sources in Section 16 with fixed format.
"""


# 为了向后兼容，创建一个 PROMPT_TEMPLATE 格式化字符串
# 使用位置参数: {0}=company, {1}=ticker, {2}=date, {3}=price, {4}=currency, {5}=mcap, {6}=currency
PROMPT_TEMPLATE = """{0}
{1}
As of today [{2}]
Stock Price (Previous Close): {3} {4}
Market Cap: {5} {6}

=== INVESTMENT SUMMARY GENERATION INSTRUCTIONS ===

**Objective:** Create a concise investment summary (max 5 pages, ~450-600 words) covering business overview, financial stability, valuation, customer segments, competitive landscape, and Buy/Hold/Sell recommendation.

**Data Sources Required:**
- Company websites, annual/quarterly reports (10-K, 10-Q, SEC filings)
- MD&A statements, earnings transcripts, investor conferences
- Regulatory publications, industry reports (McKinsey, Deloitte, EY)
- Industry-specific ratios vs median
- Analyst notes (Piper Sandler, Goldman Sachs, etc.)
- Provide links to sources used

**Constraints:**
- Current ratio < 1.3 = unhealthy liquidity (except cash businesses like McDonald's, JD.com)
- Focus on ONE recommended action with pros/cons
- This is NOT professional investment advice

---

## SECTION 1: Header
Title: "Investment Summary - [Company Name]"
Include: Date, stock price (previous close), market cap, recommended action (Buy/Hold/Sell), industry name(s)

---

## SECTION 2: Business Overview

**Format:** 1 paragraph narrative + REQUIRED structured data block

**Narrative Requirements:**
- Summarize operations, major divisions, products/services, key financials (FY sales, operating income, margins)
- Include 2-sentence explanation of each product's use to major customer segments
- Highlight strengths (Technology, Brand, Efficiency) and challenges (Market Pressures, Risks)
- Use FY data or YTD; specify fiscal year-end
- For each division: include sales % of total, gross profit margin, and % of operating profit (profit_pct)

**⚠️ CRITICAL - JSON BLOCK PLACEMENT RULES:**
1. **This JSON block MUST ONLY appear IMMEDIATELY after the Business Overview narrative paragraph**
2. **DO NOT output this JSON block in any other section (especially NOT in Section 6: Key Financials)**
3. **DO NOT repeat financial data in JSON format anywhere else**
4. **All other sections must use their specified format (bullet points, paragraphs, etc.)**

**You MUST output this structured JSON block after the Business Overview narrative:**

```business_overview_data
{{
  "fiscal_year": "2024",
  "key_metrics": {{
    "total_revenue": "XX.XB CNY",
    "operating_income": "X.XB CNY",
    "net_income": "X.XB CNY",
    "operating_margin": "X.X%"
  }},
  "divisions": [
    {{"name": "Division 1", "description": "products/services", "sales_pct": "XX%", "gross_margin": "XX%", "profit_pct": "XX%"}},
    {{"name": "Division 2", "description": "products/services", "sales_pct": "XX%", "gross_margin": "XX%", "profit_pct": "XX%"}}
  ]
}}
```

**Rules for JSON block:**
- Replace ALL values with actual researched data
- Include ALL major divisions (not just 2)
- Use null for unknown values
- This block is REQUIRED for data extraction

---

## SECTION 3: Business Performance (bullet points)
- (a) Sales growth past 5 years + next year forecast
- (b) Profit growth past 5 years + next year forecast
- (c) Operating cash flow increase
- (d) Market share and industry ranking

---

## SECTION 4: Industry Context (bullet points, for each industry)
- (a) Product cycle maturity
- (b) Market size and CAGR
- (c) Company's market share and ranking
- (d) 3-year avg sales growth vs industry average
- (e) 3-year avg EPS growth vs industry average
- (f) Debt-to-total assets vs industry average
- (g) Industry cycle phase (expansion/slowing)
- (h) Industry-specific metrics (NOT P/E ratios):
  - Banking: CAR, loan-to-deposit, NIM, NII
  - Semiconductor: Book-to-bill, die size, Yield
  - Airline: Loading factor, breakeven loading factor
  - Offshore drilling: Rig count, day rate

---

## SECTION 5: Financial Stability and Debt Levels (1 paragraph)
Assess: operating cash flow, dividend coverage, capex, liquidity (cash, current ratio)
Evaluate debt: total debt, D/E ratio, debt-to-assets, interest coverage, Altman Z Score vs industry
Highlight problems OR confirm prudent management

---

## SECTION 6: Key Financials and Valuation (bullet points)
**Sales/Profitability:**
- FY sales + YoY change + forecast
- Divisional performance
- Operating margin trends
- Forward guidance (sales, EPS, YoY)

**Valuation Metrics:**
- P/E (TTM vs industry/historical)
- PEG, dividend yield
- 52-week range position

**Financial Ratios:**
- Common debt ratios with risk highlights

**Industry-Specific Metrics:**
- 3 industry-specific metrics
- Company values vs industry average
- Observations and implications

---

## SECTION 7: Big Trends and Big Events (bullet points)
For each business segment: industry trends/events + effects on company

---

## SECTION 8: Customer Segments and Demand Trends (bullet points)
- Major segments by sales (currency, %)
- 2-3 year growth projections per segment + drivers
- Customer complaints + substitutes + switching speed

---

## SECTION 9: Competitive Landscape (bullet points)
- Industry dynamics: CR4, margins, capacity utilization, CAGR, cycle stage
- Key competitors: market shares, operating margins
- Moats: technology, network effects, switching costs, scale, licenses, supply chain, brands
- Top battlefront and company's positioning

---

## SECTION 10: Risks and Anomalies (bullet points)
Unusual findings + concerns + potential resolution

---

## SECTION 11: Forecast and Outlook (bullet points)
Management forecasts, product line growth/decline, reasons, recent earnings surprise

---

## SECTION 12: Leading Investment Firms and Views (bullet points)
- Top firms' ratings + target prices (% upside/downside)
- Consensus rating + average target range

---

## SECTION 13: Recommended Action: [Buy/Hold/Sell]
Select ONE action. Provide:
- Pros (bullet points)
- Cons (bullet points)

---

## SECTION 14: Industry Ratio and Metric Analysis
Important industry ratios: (a) company values, (b) vs industry avg, (c) trends

---

## SECTION 15: Key Takeaways (1 paragraph each)
- Company position, strengths, risks, recommendation rationale
- Monitorable factors for future opportunities
- Any missed key points

---

## SECTION 16: Sources

**⚠️ CRITICAL - FIXED FORMAT REQUIRED:**

List all sources used in THIS EXACT FORMAT (one per line):
```
Source Title | https://example.com/full-url
```

**Example:**
```
Company Annual Report 2024 | https://company.com/investor-relations/annual-report-2024
Goldman Sachs Analyst Note | https://goldmansachs.com/research/company-analysis
McKinsey Industry Report | https://mckinsey.com/industries/report-2025
SEC/CSRC Filings | https://sec.gov/cgi-bin/browse-edgar?company=TICKER
Industry Association Data | https://industry-association.org/data/2025
```

**Rules:**
- ONLY use existing, accessible URLs.
- DO NOT use placeholders or guessed URLs.
- Verify the URL structure (e.g., proper SEC filing links, official IR pages)
- Verify the URL response is 200 OK
- Verify the URL is not a 404 Not Found
- Verify the URL is not a 403 Forbidden
- Verify the URL is not a 401 Unauthorized
- Verify the URL is not a 400 Bad Request
- Verify the URL is not a 500 Internal Server Error
- Verify the URL is not a 503 Service Unavailable
- Verify the URL is not a 502 Bad Gateway
- Format: `Title | URL` (pipe separator)
- One source per line
- Include diverse source types: company filings, analyst reports, industry reports
- Must be the exact same sources you have used in the analysis
- Do not use any other sources that are not in the analysis
- When Doing the analysis, must using the source that you have verified

---

**Output Format:** Markdown with bullet points for sections 3-12. Sources in Section 16 with fixed format.
"""
