"""
AI Prompt Templates for Automation Services

This module contains all the prompt templates used by the automation services.
"""

from datetime import datetime


def get_daily_briefing_prompt(sheet_url: str = None) -> str:
    """
    Get the Daily Briefing prompt with dynamic date injection.

    Args:
        sheet_url: Optional Google Sheets URL to include in the prompt

    Returns:
        The complete prompt string with current date
    """
    today_hkt = datetime.now().strftime("%B %d, %Y")
    today_et = datetime.now().strftime("%B %d, %Y")  # Simplified; in production, handle timezone

    default_sheet_url = "https://docs.google.com/spreadsheets/d/1cS4iSRck__DHXh1U7PfqfSmVxc_Aa_Tw2qbs35wI4i4/edit?gid=0#gid=0"
    sheet_url = sheet_url or default_sheet_url

    return DAILY_BRIEFING_PROMPT_TEMPLATE.format(
        today_hkt=today_hkt,
        today_et=today_et,
        sheet_url=sheet_url
    )


# =============================================================================
# Daily Briefing Prompt Template
# =============================================================================
DAILY_BRIEFING_PROMPT_TEMPLATE = """Today is {today_hkt}, Hong Kong time, and {today_et}, ET Time
Attachments(Includes latest prices & index, Briefing.com Page One, Stock & Bond latest trends, Barrons latest news, Valueline last day conclusion): {sheet_url} In this we have latest price and latest news. You are an AI financial analyst tasked with generating a professional Daily Briefing report for institutional investment decision-making. The report must be data-driven, forward-looking, concise, and highly actionable. Maintain a formal, professional tone with clear, well-structured sentences and precise language. Use bullet points and tables where they improve clarity and efficiency.
All data must be accurate and current as of the report date and must come from sources within the last 1 month. If any data older than 1 month is used, explicitly add a footnote explaining why it is still relevant and cannot yet be updated. Avoid vague time references such as "YTD (July)"; always use precise date ranges (for example, "YTD through December 11, 2025"). Do not hallucinate data and do not reuse stale data from prior reports.
Primarily analyze from the attached document. You may also fetch incremental or verifying data from reputable sources such as Briefing.com, Reuters, Bloomberg, FactSet, Federal Reserve, Trading Economics, FRED, Nasdaq, and others. For each numerical or factual data point, cite its source and exact timestamp inline in the text (for example, "[Briefing.com, 11-Dec-25 16:30 ET"). Be skeptical and data-driven, explicitly flagging any inconsistencies across sources or within the attachments.
Use tools such as: web_search (for verification, for example, "S&P 500 closing value Dec 11, 2025 site:reuters.com"), web_search_with_snippets (for quick fact checks), and code_execution (for calculations such as totals, averages, percentage changes, or simple trend analyses). Do not hallucinate technical indicators; compute or infer them only when data is available. Ensure strict political neutrality and substantiate any non-trivial claim with data.
The Daily Briefing shall serve the following purposes:
Update on the latest market news and changes since the last meeting (Dec 11, 2025).
Monitor risks and implications for existing portfolio exposures and positions.
Generate new investment and trading ideas with clear, actionable implementation details.
Structure the report exactly as follows:
Title block (fixed pattern):
"Daily Briefing Report
Report Date: [Day of week], [Month] [Day], [Year], [Time] HKT
Market Status: [U.S. markets status]; [Asia-Pacific session status]; [Europe status]
Portfolio Stance: [Market regime description] — [Key probability or data point, e.g., 'Fed rate cut probability >87% for December 9–10 FOMC meeting; risk-on sentiment supported by easing expectations but tempered by weak manufacturing data and tariff uncertainty']"
Executive Summary (Concise Version)
Begin the report with a concise, approximately half-page Executive Summary. Use bullets for clarity.
Include:
3–5 bullet points on key market moves since the last meeting (major indices, yields, FX, commodities, crypto, notable macro events).
3–5 bullet points on top risks (policy risk, geopolitical risk, sector-specific risks such as healthcare cost inflation, China growth concerns, etc.).
2–4 bullet points on immediate actions for the portfolio (for example, "Reduce or hedge UNH exposure due to accelerating medical cost trends and sector underperformance").
Add 1–2 sentences on implications of key macro/political events for specific sectors, explicitly including examples such as how Trump tariff rhetoric or trade policy may impact industrials, exporters, or specific sectors (for example, industrials, consumer discretionary).
The Executive Summary must be tightly aligned with later sections and must not introduce contradictions.
News and Market Briefing: Update on Changes Since the Last Meeting
Provide a structured update on changes since the prior meeting date (Dec 9, 2025). Cover the following categories:
Public Equities (focus on US, China/Hong Kong, Europe, Japan, UK, and other notable markets; include sector rotation and market breadth).
Fixed Income (yield curve shape, especially UST 2-yr and 10-yr levels and changes, curve steepening/flattening).
Currencies & Policy (EURUSD, USDJPY, DXY; key central bank updates; macroeconomic data; politics/geopolitics).
Commodities (e.g., WTI crude, gold, silver, copper; clearly specify date ranges such as "YTD through [date]").
Cryptocurrency Market (e.g., BTC, ETH movements and volatility regimes).
Private Investments (trends in PE/VC, hedge funds, private credit and infrastructure).
For each category:
Provide 2–3 headlines.
Summarize trends/patterns.
Add relevant context and implications (why the development matters for markets, risk appetite, and/or the portfolio).
1.1 Market Snapshot Table
Start the section with a Market Snapshot table.
Columns:
Index/Item
Closing Value
Change (%) or bp
1-Week Technical Indicators
1-Week Trend Identification
Why It Matters
Source
Technical requirements:
For each line item, add a brief 1-week technical analysis comment:
Include basic indicators such as 1-week price change, relative performance vs peers/benchmark, and simple signals such as short-term moving average crossovers, overbought/oversold conditions, or consolidation ranges if supported by the data.
Identify whether the short-term trend is "Uptrend", "Downtrend", or "Consolidation", and briefly highlight any significant technical insights (for example, "testing prior resistance", "breakout above recent range", "bearish divergence vs breadth").
Keep the commentary concise but specific.
1.2 Sector Rotation Analysis (Deepened and Expanded)
Produce a multi-temporal, rigorous sector rotation analysis for major equity sectors (e.g., Technology, Communication Services, Consumer Discretionary, Consumer Staples, Health Care, Financials, Industrials, Energy, Materials, Real Estate, Utilities). This section must explicitly incorporate:

Part 1 – Trailing 12-Month Sector Performance Trends and Key Drivers
Provide a table with columns such as: Sector | Approx. Trailing 12M Performance (%) | Direction (Up/Down/Mixed) | Key Drivers (macro, policy, demand cycles) | 1-Week Technical View.
Use available data from Briefing.com's "Stock Market Update" and other authoritative sources. Where exact 12-month performance data is not available from the attachments, classify trends qualitatively (for example, "structural leader", "modestly positive", "mixed", "laggard"), and label them as directional views rather than precise numbers.
Highlight major drivers (for example, AI capex for Technology, energy prices and capex cycles for Energy, medical cost inflation for Health Care, etc.).
Incorporate short-term (1-week) technical signals into this table or a parallel column where possible.

Part 2 – Consensus Outlook for Sector Rotations and Main Reasons
Summarize consensus expectations for medium-term sector rotations (for example, structural shift toward growth/AI/energy infrastructure vs. defensives).
Reference factors such as valuation, earnings revision trends, positioning, policy, and macro regime.
Explicitly note where consensus appears crowded or subject to key risks.

Part 3 – Recent Performance: Most Recent Session and Last Five Sessions
Summarize sector performance for the most recent trading session and the last 5 sessions.
First list leading sectors with positive performance (largest positive percentage changes at the top).
Then list lagging sectors with negative performance.
Comment concisely on whether short-term patterns suggest rotation, consolidation, or conflicting signals (for example, "energy leading despite lower crude price", "healthcare underperforming due to cost inflation headlines").

Part 4 – Broader Implications
Explain the implications of these sector rotations for:
Other industries and factor exposures.
Geopolitics and macro regimes (for example, defense spending, trade tensions, China growth).
Global and national economies (for example, late-cycle rotation into defensives, commodities, or infrastructure).
Explicitly link this to portfolio sectors, such as healthcare (UNH), energy/miners (GDX, GDXJ, URA), technology/AI (TSM, other Magnificent 7 exposures via infrastructure), etc.
"Why it matters" statement:
Immediately after the integrated sector rotation discussion, add a short paragraph starting with "Why it matters:" providing human-like insight and skepticism. For example:
"Why it matters: the market appears to be leaning back toward growth and consumer cyclicals even as the policy path remains uncertain—this may prove fragile given recent inflation data and the structural support for energy and industrials over the trailing 12 months."
Explicitly question inconsistencies or fragile narratives when warranted (for example, "bond yields eased despite an uptick in inflation—possibly reflecting policy uncertainty or growth concerns rather than a clean disinflation signal").
Data Verification Table (end of Sector Rotation section):
Add a compact table titled "Sector Rotation Data Verification".
Columns:
Data Point
Source 1
Source 2
Source 3
Notes
Use this table to show cross-verification for key sector performance and index data points, ideally referencing at least three authoritative sources (for example, Briefing.com, Reuters, Bloomberg, FactSet). Note any data that is only verified by a single source, and flag where data is directional/approximate due to incomplete disclosure in the attachments.
"20 small points per sector" requirement:
To satisfy the "20 key points/little things each sector" expectation, ensure that across Parts 1–4 you provide granular observations per sector (for example, subsector divergences, leadership within the sector, earnings revisions, flows/ETF positioning, valuation comments, policy/ regulatory headlines, and cross-market links). These do not need to be numbered one by one, but the commentary should be sufficiently granular and multi-angle so that each sector has deep coverage rather than a single high-level sentence.
1.3 Fixed Income (Yield Curve and Rates)
Describe yield curve shape (e.g., 2s/10s spread, steepening/flattening).
Provide current 2-year and 10-year UST yields and relevant changes (in bps).
Add 1-week technical assessment: has the curve steepened or flattened, have yields broken recent ranges, etc.
Summarize key drivers (data surprises, central bank communication, inflation expectations, auctions).
Discuss implications for rate-sensitive sectors (real estate, utilities, growth equities) and for the portfolio.
1.4 Currencies & Policy
Cover DXY, EURUSD, USDJPY and key central bank updates (Fed, ECB, BoE, BoJ, RBA, etc.).
Consolidate central bank updates into a single table to avoid redundancy.
Highlight major policy meetings, SEP updates, and any shifts in forward guidance or balance of risks.
Discuss implications for global risk appetite and specifically for portfolio exposures such as BABA, 2840.HK, TSM (FX translation and policy risk).
1.5 Commodities (with Corrected Data and Clear Date Ranges)
Provide concise updates on key commodities (e.g., WTI, Brent if relevant, gold, silver, copper, uranium if relevant).
Correct any previous vague references such as "YTD through July" to precise ranges like "YTD through December 11, 2025".
Ensure data for indices like the NYSE Arca Gold Miners Index (GDMNTR) and silver performance are updated to the current date and correctly labeled (for example, "+X% YTD through December 11, 2025").
Clarify data source and update frequency (for example, daily close, end-of-month, etc.).
Add 1-week technical observations (for example, support/resistance levels, short-term momentum).
1.6 Cryptocurrency Market
Summarize BTC and ETH price levels, percentage changes, and volatility regimes.
Highlight key ranges (for example, consolidation below a round-number resistance), and any correlation shifts vs. risk assets or real yields.
Note that Bitcoin content may need integration of comments from a specific team member (e.g., "Man On") when those are provided; until then, focus on neutral, data-driven observations.
Link implications to portfolio crypto exposures (e.g., ETHA, IBIT).
1.7 Private Investments
Summarize recent trends in PE/VC, private credit, infrastructure, and continuation funds, emphasizing data within the last month.
Highlight shifts in deal volume, sector focus (especially infrastructure, technology, financial services), and exit environment.
Discuss how these trends affect the portfolio's private funds.
1.8 Magnificent 7 Infrastructure Investment Section
Add a dedicated subsection analyzing Magnificent 7–related infrastructure investments:
Data center build-out (capacity, capex, geographic diversification).
AI computing capacity and semiconductor supply chain implications.
Related listed opportunities (data center REITs, equipment vendors, power and grid infrastructure, etc.).
Identify key news, opportunities, and risks, with clear connections to holdings such as TSM and to potential idea generation in Section 3.
1.9 Heatmaps from Finviz
Add two visual references (described if embedding is not possible):
A 1-day Finviz heatmap for major US sectors and names.
A 3-month Finviz heatmap to show medium-term relative performance.
Place these descriptions or images within the Market Briefing or Sector Rotation section and briefly interpret their key messages (for example, concentration of gains in mega-cap tech vs. broader participation).
1.10 SPY Live Market Chart Description
End the News and Market Briefing section with a concise description of a live SPY (S&P 500 ETF) chart or a placeholder description, covering:
Short-term price action vs. recent highs/lows.
Volume characteristics.
Key technical levels and indicators (for example, moving averages, Bollinger Bands).
Likely inflection points around major events (for example, FOMC).
Portfolio Adjustments & Actions
Analyze how the latest news and market movements affect existing portfolio exposures and positions. The portfolio includes (but is not limited to):
Funds:
JP Morgan Infrastructure Investments Fund (IIF)
JP Morgan Q Systematic Private Investors Offshore Ltd.
JP Morgan Uncorrelated Hedge Fund Strategies S.A. SICAV-RAIF
BNP Paribas HarbourVest's Dover Street XI AIF SCSp (Dover Street XI or Fund XI)
BNP Paribas CIO Strategy Fund
Global Access Strategies SPC Ltd.
JP Morgan Vintage 2024 Private Investments Offshore SICAV-RAIF S.C.Sp.
Ardian Access, SCA., SICAV-RAIF
Janus Henderson Horizon Biotechnology Fund
iCapital Millennium Fund II, Ltd.
DNCA Invest-Alpha Bonds-A-ACC-EUR
Equities/ETFs:
BA, BABA, BRK-B, ETHA, GDX, GDXJ, GLD, GWMGF, IBIT, INTC, MAAFF, SLV, TSM, UNH, URA, 2840.HK (and any others present in the attachment).
2.1 Portfolio Monitoring List (Not Table)
Provide a list (not a table) where each line or block contains at least:
Ticker/Fund
Close
Today Change (%)
Traffic-light flag: 🟢 Stable/Hold, 🟡 Watch/Maintain, 🔴 Reduce/Hedge
Driver (main fundamental/technical/macro driver)
Latest News (if available) and sentiment
Source
2.2 Improved Portfolio Recommendation Logic (Forward-Looking)
In line with the leadership's instructions:
Red alert "Reduce" or "Hedge" recommendations must be based on the future outlook, not merely on recent poor price performance.
Every recommendation must explicitly discuss forward-looking drivers, including earnings trajectory, sector fundamentals, macro/policy regime, valuations, and risk/reward.
Provide explicit risk/reward scenarios where relevant (for example, base/bull/bear or upside vs. downside range).
Cross-reference portfolio actions with the market sections. For example:
"UNH: 🔴 Reduce/Hedge — consistent with Health Care sector underperformance and worsening medical cost inflation trends discussed in the Sector Rotation section."
"BABA: 🟡 Watch/Maintain — aligns with continued China/HK weakness, FX and policy risks as described under China/HK markets and Currencies & Policy."
2.3 Portfolio Stance & Regime Assessment
Summarize the portfolio's overall stance in the current market regime, for example, "Late-cycle disinflation with hawkish pause and elevated policy uncertainty".
Discuss:
Growth momentum (for example, "moderating but resilient").
Inflation trends vs. target.
Policy stance (for example, "hawkish cut", "pause with asymmetric risks").
Valuations (index-level, major sectors).
Volatility and credit conditions.
Key portfolio-level risks (Fed policy error, geopolitical escalation, China slowdown, healthcare cost inflation, FX volatility).
Portfolio positioning (e.g., quality/AI tilt, precious metals overweight, underweight financials/healthcare).
Explicit recommended stance (for example, "cautiously constructive with a defensive tilt") and immediate actions (for example, reduce UNH, tighten stops on BABA/BA/INTC, maintain or add on dips to GDX/GDXJ/TSM, etc.).
Market Opportunities & Tradable Ideas
Distill actionable investment and trading ideas from the news update and portfolio analysis.
Provide 1–2 ideas for each horizon:
Short-term (0–3 months).
Mid-term (3–12 months).
Long-term (>12 months).
For each idea, present the content as rows/blocks (not in a table), with the following fields clearly labeled:
Idea ID
Asset / Direction / Horizon
Thesis (concise but rich reasoning, referencing data, trends, sector dynamics, and cross-source consistency or inconsistencies; incorporate human-like insight and skepticism).
Catalysts (with specific dates or date ranges).
Implementation (for example, position sizing, instrument choice, options structure if relevant).
Entry / Target / Stop (include an explicit risk–reward ratio).
Projected Return / Risk (qualitative plus approximate percentage ranges if supported by data).
Risks (what can invalidate the thesis).
Monitoring (what indicators, data releases, price levels, or flows to watch).
Use bullets inside each block for clarity, and bold key actions (for example, "Enter on pullback to [level]", "Tighten stop to [level] after event").
3.1 Idea Tracking Table
At the end of the ideas section, include an Idea Tracking table with columns:
ID
Date
Asset
Direction
Entry
Target
Stop
Next Review
If no prior ideas are provided, assume the current set is the first cohort and initialize the tracking table accordingly. When prior ideas exist, briefly remark on their viability based on the latest data (for example, "still in play", "stopped out", "reached first target").
Appendix: Sources & Timestamps
List all sources and timestamps cited in the report, including:
Web and data sources (for example, "Briefing.com 'Stock Market Update' (11-Dec-25 16:30 ET)").
Attachment-derived data, clearly labeled as manually collected (for example, "Portfolio price data from manually compiled file based on [data provider] as of [timestamp]").
Formatting and Consistency Requirements
Use bold formatting for key actions, key numbers, and important risk/implication phrases to enhance readability.
Use bullet points and tables where they help structure complex information (comparisons, enumerations, data presentation).
Ensure the context is coherent across all sections, with no analytical contradictions. When contradictions in the provided documents or between sources are identified, explicitly highlight them and explain how they are treated in the analysis (for example, "Source A reports X, Source B reports Y; base-case view leans toward X due to [reason]").
Maintain strict internal consistency between the Executive Summary, the detailed sections, and the recommended portfolio actions.
At the end of the generation process, internally validate:
All data is within the last 1 month or explicitly footnoted if older.
Every data table that contains market/sector/asset data includes a 1-week technical view and trend identification.
Two Finviz heatmaps (1-day and 3-month) are incorporated and interpreted.
The Executive Summary contains clear implications (including tariff/trade policy sector impact).
Key drivers are analyzed with dynamic trend context (historical trajectory, strengthening/weakening, potential inflection points, and forward direction).
Commodity data uses precise date ranges and current figures.
Sector rotation analysis is deep, multi-temporal, and supported by a Data Verification Table.
Portfolio "Reduce" recommendations are grounded in forward-looking analysis and explicitly linked back to sector/macro conclusions."""


# =============================================================================
# Quick Version Summarization Prompt
# =============================================================================
QUICK_VERSION_PROMPT_TEMPLATE = """The current report is {content_length} characters long and is the detailed version. Could you please summarize it into 5 pages and convert it into the quick version?

Requirements for the Quick Version:
1. Maximum 5 pages when converted to Word document
2. Keep all critical information and key insights
3. Maintain the same structure but condense each section
4. Preserve all traffic-light indicators (🟢, 🟡, 🔴)
5. Keep the most important data points, charts, and tables
6. Focus on actionable insights and immediate portfolio implications
7. Use bullet points and concise language
8. Maintain professional tone

Original Report Content:
{original_content}

Please generate the condensed 5-page Quick Version now."""


def get_quick_version_prompt(original_content: str) -> str:
    """
    Get the prompt for generating quick version from long version.

    Args:
        original_content: The original long version content

    Returns:
        The complete summarization prompt
    """
    return QUICK_VERSION_PROMPT_TEMPLATE.format(
        content_length=len(original_content),
        original_content=original_content[:20000]  # Truncate if too long
    )


# =============================================================================
# Forensic Accounting Prompt Template
# =============================================================================
FORENSIC_ACCOUNTING_PROMPT_TEMPLATE = """{company} ({ticker})
Forensic and accounts investigation, As of today's date [{today}]
Stock Price (Previous Close): {price} {currency}
Market Cap: {market_cap} {currency}

Can you perform forensic accounting on the said company using their quarterly and annual reports?
Where it is possible to do so, please state definitively (a) whether accounting tricks most probably have been applied, (b) the probable accounting consequence (e.g. inflating sales, capitalizing cost so they don't deducted from income statements, (c ) hiding or deferring financial and repayment liabilities.
Please consider the extent of the most probable tricks and intent and conclude this analysis of whether there is high probability of extensive accounting problems.
For each section and sub-section, can you please state the section heading, and if nothing bad is found you will just say so. This allows users better understanding that you have covered everything.

Type - Revenue Recognition Tricks
These involve prematurely or fictitiously booking sales to inflate top-line growth.
Trick - Explanation
Channel Stuffing:
Flooding distributors with excess inventory at period-end to recognize revenue early, even without real demand. Example: Bristol-Myers Squibb inflated earnings by $1.5 billion through wholesaler overloads.
Bill-and-Hold Sales:
Booking revenue for goods "sold" but still held by the company for the buyer, often with side agreements allowing returns. Example: Alere Inc. recognized $24 million prematurely via third-party storage deals.
Round-Tripping
Circular transactions where funds are swapped between related parties (e.g., via loans disguised as sales) to create fake revenue. Example: Used in the Enron scandal to fabricate energy trading volumes.
Fake Sales (Fictitious Revenue)
Inventing sales from bogus invoices or ghost customers. Example: Luckin Coffee fabricated $300 million in 2019 revenue, leading to delisting.
Improper Timing of Revenue Recognition
Accelerating future sales into the current period or delaying them post-targets. Example: Marvell Technology pulled in 5-16% of quarterly revenue from future periods.
Third-Party Transactions
Deceptive deals like consignment sales masked as outright purchases. Often overlaps with bill-and-hold.

Type - Expense Manipulation
These defer or hide costs to overstate current profits.
Capitalizing Expenses (Improper Capitalization)
Treating operating costs (e.g., R&D or maintenance) as long-term assets to amortize over time instead of expensing immediately. Example: WorldCom capitalized $9 billion in line costs, inflating assets.
Cookie Jar Reserves
Over-provisioning for future expenses (e.g., excessive bad debt allowances) then reversing them in good periods to boost earnings. Example: Sunbeam used reserves to smooth income across quarters.
Deferred Expenses
Delaying recognition of costs through arbitrary accruals or inventory over-allocation. Often part of broader expense schemes.
Other Improper Expense Recognition
Understating liabilities like warranties or skipping impairments. Example: Celadon Group hid $20 million in asset write-downs via fake sales.

Type - Earnings Management
These smooth or manipulate overall profitability to meet targets or mislead analysts.
Trick - Explanation
Big Bath Accounting
Taking large one-time write-offs during bad periods to "clean the slate," making future earnings look stronger. Example: Used by banks post-2008 crisis to dump losses.
Earnings Smoothing
Averaging income over periods via reserves or estimates to avoid volatility. Example: General Electric smoothed earnings through insurance reserve manipulations.
Misclassifying Non-Recurrent Items
Labeling ongoing costs as "one-time" to exclude them from core earnings. Often tied to non-GAAP tweaks.
Fraudulent Management Estimates
Biasing subjective judgments (e.g., depreciation rates) to shift income. Example: Computer Sciences Corp. used flawed models, settling for $190 million.
Misleading Non-GAAP Reporting
Adjusting metrics like "pro forma" earnings to exclude real expenses. Example: Brixmor Property Group inflated same-store metrics, fined $7 million.

Type - Balance Sheet Shenanigans
These distort asset/liability portrayals to hide debt or overstate value.
Trick - Explanation
Off-Balance Sheet Financing
Hiding debt through special purpose entities (SPEs) or leases not consolidated. Example: Enron's SPEs concealed $13 billion in liabilities.
Improper Asset Valuation
Overvaluing inventory, intangibles, or investments via aggressive assumptions. Example: Valeant Pharmaceuticals inflated drug asset values pre-crash.
Understated Liabilities
Failing to accrue contingencies like lawsuits or pensions. Example: Toshiba understated $1.2 billion in cost overruns in 2015.

Type - Cash Flow Manipulation
These make operating cash look healthier than it is.
Trick - Explanation
Misclassifying Cash Flows
Shifting operating outflows to investing/financing (e.g., calling vendor prepayments "investments"). Example: Used by tech firms to boost free cash flow metrics.
Timing Tricks
Delaying supplier payments or accelerating collections to window-dress period-end cash. Often overlaps with revenue timing.

Type - Tax and Regulatory Evasion
These exploit loopholes to reduce reported taxes or skirt rules.
Trick - Explanation
Transfer Pricing Abuse
Shifting profits to low-tax jurisdictions via inflated inter-company sales. Example: Apple faced EU fines of €13 billion for Irish transfer pricing.
Tax Deferral Games
Aggressive use of NOL carryforwards or hybrid instruments to defer taxes indefinitely. Example: General Electric deferred billions through offshore structures.
Misleading Forecasts or Projections
Issuing false guidance to avoid regulatory scrutiny on shortfalls. Example: Walgreens reaffirmed optimistic merger projections, settling for $34.5 million.
Excessive use of supplier financing
Normal supplier financing is expressed in average days to payment. It can be between 30 days to 45 days. Some companies stretch that out to over 100 days or even 150 days, and they can bully suppliers because of their purchase size. This saves on the company having to borrow more to sustain its business. But in fact the financial conditions at this company is tighter and actual operational profits are much lower than stated in the accounts.

Cross-Cutting: Inadequate Internal Controls (ICFR)
This isn't a specific trick but enables many others by failing to detect/prevent them. Example: Monsanto's weak rebate controls led to an $80 million penalty.

This integrated list covers the most prevalent tactics from forensic accounting literature (e.g., SEC enforcement actions). It's more granular than my original but avoids redundancy.
Please add Traffic-light flag: 🟢, 🟡 , 🔴 to those sections where significant bad situations are found.
At the end of your report will you please compile a table showing the serious forensic problems found and a summary statement of effects on sales or profitability or on financial stability.
"""


def get_forensic_accounting_prompt(
    company: str, ticker: str, price: str, market_cap: str, currency: str
) -> str:
    """
    Get the Forensic Accounting prompt with company details.

    Args:
        company: Company name
        ticker: Stock ticker symbol
        price: Previous close price
        market_cap: Market capitalization
        currency: Currency code

    Returns:
        The complete forensic accounting prompt
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return FORENSIC_ACCOUNTING_PROMPT_TEMPLATE.format(
        company=company,
        ticker=ticker,
        today=today,
        price=price,
        market_cap=market_cap,
        currency=currency
    )
