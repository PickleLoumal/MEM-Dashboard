# ==========================================
# Prompt 模板段落常量
# 位置参数: {0}=company, {1}=ticker, {2}=date,
#          {3}=price, {4}=currency, {5}=mcap, {6}=currency
# ==========================================

# 头部：公司信息 + 基础指令
SECTION_HEADER = """{0}
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


**Constraints:**
- Current ratio < 1.3 = unhealthy liquidity (except cash businesses like McDonald's, JD.com)
- Focus on ONE recommended action with pros/cons
- This is NOT professional investment advice

---

## SECTION 1: Header
Title: "Investment Summary - [Company Name]"
Include: Date, stock price (previous close), market cap, recommended action (Buy/Hold/Sell), industry name(s)

---

"""

# Section 2: Business Overview
SECTION_BUSINESS_OVERVIEW = """## SECTION 2: Business Overview

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
    "total_revenue_yoy": "+X.X%",
    "operating_income": "X.XB CNY",
    "operating_income_yoy": "+X.X%",
    "net_income": "X.XB CNY",
    "net_income_yoy": "+X.X%",
    "operating_margin": "X.X%",
    "operating_margin_yoy": "-X.Xpp",
    "net_interest_margin": "X.X%",
    "net_interest_margin_yoy": "-X.Xbps"
  }},
  "divisions": [
    {{"name": "Division 1", "description": "products/services", "sales_pct": "XX%", "gross_margin": "XX%", "profit_pct": "XX%"}},
    {{"name": "Division 2", "description": "products/services", "sales_pct": "XX%", "gross_margin": "XX%", "profit_pct": "XX%"}}
  ]
}}
```

**Note for Banks:** Include net_interest_margin (NIM) instead of operating_margin. For non-financial companies, include operating_margin.

**Rules for JSON block:**
- Replace ALL values with actual researched data
- Include ALL major divisions (not just 2)
- Include YoY (Year-over-Year) changes for key metrics where available
- For YoY: use "+X.X%" for positive, "-X.X%" for negative, "pp" suffix for percentage point changes
- Use null for unknown values
- This block is REQUIRED for data extraction

---

"""

# Section 3-6: Performance & Financials
SECTION_PERFORMANCE_FINANCIALS = """## SECTION 3: Business Performance (bullet points)
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

"""

# Section 7-9: Trends & Competition
SECTION_TRENDS_COMPETITION = """## SECTION 7: Big Trends and Big Events (bullet points)
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

"""

# Section 10-12: Risks & Analyst Views
SECTION_RISKS_ANALYSTS = """## SECTION 10: Risks and Anomalies (bullet points)
For each risk, include:
- **[HIGH/MEDIUM/LOW]** Risk description + potential impact + mitigation
- Prioritize risks by severity (HIGH risks first)
- Include both internal (company-specific) and external (market/regulatory) risks
- Mention any unusual findings or anomalies in financial statements

---

## SECTION 11: Forecast and Outlook (bullet points)
Management forecasts, product line growth/decline, reasons, recent earnings surprise

---

## SECTION 12: Leading Investment Firms and Views (bullet points)
- Top firms' ratings + target prices (% upside/downside)
- Consensus rating + average target range

**You MUST include this structured summary at the END of Section 12:**

```analyst_consensus
{{
  "consensus_rating": "Buy|Hold|Sell",
  "buy_pct": XX,
  "hold_pct": XX,
  "sell_pct": XX,
  "target_price_low": "XX.XX CNY",
  "target_price_high": "XX.XX CNY",
  "target_price_avg": "XX.XX CNY",
  "upside_pct": "+XX.X%"
}}
```

---

"""

# Section 13-15: Recommendation & Takeaways
SECTION_RECOMMENDATION_TAKEAWAYS = """## SECTION 13: Recommended Action: [Buy/Hold/Sell]
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

"""

# Section 16: Sources (handled via Live Search citations - no AI output needed)
SECTION_SOURCES = """## SECTION 16: Sources

Note: Source URLs are automatically captured from Live Search. You do not need to output URLs.
Simply ensure your analysis references real, verifiable data sources.

---

**Output Format:** Markdown with bullet points for sections 3-12.
"""


__all__ = [
    "SECTION_BUSINESS_OVERVIEW",
    "SECTION_HEADER",
    "SECTION_PERFORMANCE_FINANCIALS",
    "SECTION_RECOMMENDATION_TAKEAWAYS",
    "SECTION_RISKS_ANALYSTS",
    "SECTION_SOURCES",
    "SECTION_TRENDS_COMPETITION",
]

