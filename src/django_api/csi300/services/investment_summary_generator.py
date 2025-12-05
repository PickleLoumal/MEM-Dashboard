"""
Investment Summary Generator Service

用于生成 CSI300 公司的投资摘要。
可以从 Django views 调用，也可以作为独立脚本运行。
"""

import os
import datetime
import random
import re
import asyncio
import json
import textwrap
from decimal import Decimal, InvalidOperation
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, List

# Django 异步适配器
from asgiref.sync import sync_to_async

# XAI SDK 配置 (从环境变量读取，不再硬编码)
XAI_API_KEY = os.environ.get("XAI_API_KEY")
if not XAI_API_KEY:
    import warnings
    warnings.warn(
        "XAI_API_KEY environment variable is not set. "
        "Please configure it in your .env file for Investment Summary generation to work.",
        UserWarning
    )

from xai_sdk import Client
from xai_sdk.chat import user, system

# Yahoo Finance API 配置
import yfinance as yf

# 导入结构化 Prompt 模板和 AI 配置
from .prompt_template import PROMPT_TEMPLATE, AI_MODEL, AI_SYSTEM_PROMPT, AI_TIMEOUT, AI_MAX_RETRIES

# Django Models (延迟导入以避免循环依赖)
from ..models import CSI300Company, CSI300InvestmentSummary

# ==========================================
# 优化 1: 预编译正则表达式 (模块级别，只编译一次)
# ==========================================
# Section 正则表达式 - 必须匹配标题格式（以 # 开头或在行首作为独立标题）
# 使用 (?:^|\n)#+?\s* 或 (?:^|\n) 来确保匹配的是标题，而不是段落中的普通文本
# 注意：AI 可能返回 "## SECTION 2: Business Overview" 或 "## Business Overview" 格式
# 所以正则需要支持可选的 "SECTION X: " 前缀
SECTION_PREFIX = r'(?:SECTION\s*\d+\s*:\s*)?'  # 匹配可选的 "SECTION 2: " 前缀
SECTION_PATTERNS = {
    'recommended_action': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Recommended Action.*?(Buy|Hold|Sell)', re.IGNORECASE | re.DOTALL),
    'recommended_action_section': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Recommended Action.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'business_overview': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Business Overview.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'business_performance': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Business Performance.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'industry_context': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Industry context.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'financial_stability': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Financial Stability.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'key_financials': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Key Financials.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'big_trends': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Big Trends.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'customer_segments': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Customer Segments.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'competitive_landscape': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Competitive Landscape.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'risks_anomalies': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Risks and anomalies.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'forecast_outlook': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Forecast and outlook.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'investment_firms': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Leading Investment Firms.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'industry_ratio': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Industry Ratio.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
    'key_takeaways': re.compile(rf'(?:^|\n)#+?\s*{SECTION_PREFIX}Key Takeaways.*?(?=\n#|\Z)', re.IGNORECASE | re.DOTALL),
}
HEADER_CLEANUP_PATTERN = re.compile(r'^#+.*?\n')

# Django 环境由 Django 框架自动管理
# CSI300Company, CSI300InvestmentSummary 已在顶部导入

# ==========================================
# 2. 工具类与辅助函数
# ==========================================

def safe_decimal(value):
    if value is None:
        return Decimal('0')
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0')


def extract_ai_content_sections(content):
    """从AI返回的Markdown内容中提取各个部分 (使用预编译正则)"""
    # 统一去除多行字符串的公共缩进，避免因为前置空格导致标题正则 (^|\n)# 无法匹配
    content = textwrap.dedent(content)
    sections = {}
    for key, pattern in SECTION_PATTERNS.items():
        try:
            match = pattern.search(content)
            if match:
                text = match.group(0).strip()
                # 清理前导换行符和 # 标题标记
                text = text.lstrip('\n')
                text = HEADER_CLEANUP_PATTERN.sub('', text).strip()
                if key == 'recommended_action':
                    text = match.group(1)
                sections[key] = text
        except Exception:
            sections[key] = ""
    return sections


# ==========================================
# Business Overview 结构化解析器
# ==========================================
import json

# 预编译 Business Overview 解析正则
BO_PATTERNS = {
    # 匹配 "FY2024" 或 "FY 2024" 等财年格式
    'fiscal_year': re.compile(r'(?:FY\s?(\d{4})|fiscal year[- ]?end[:\s]*([A-Za-z]+\s+\d{1,2}))', re.IGNORECASE),
    # 匹配金额: "185.2B CNY", "$52.4 billion", "CNY 185.2 billion", "sales 47.1B CNY"
    'revenue': re.compile(r'(?:total\s+)?(?:revenue|sales)\s+(?:of\s+)?([^\s,]+(?:\s+(?:CNY|USD|RMB|billion|million|B|M))+|(?:CNY|USD|RMB|\$)\s*[\d.]+\s*(?:billion|million|B|M)?)', re.IGNORECASE),
    'sales_standalone': re.compile(r'(?:^|[;:,]\s*)sales\s+([\d.]+\s*[BMT]?\s*(?:CNY|USD|RMB|billion|million)?)', re.IGNORECASE),
    'operating_income': re.compile(r'operating\s+income\s+(?:of\s+)?([^\s,]+(?:\s+(?:CNY|USD|RMB|billion|million|B|M))+|(?:CNY|USD|RMB|\$)\s*[\d.]+\s*(?:billion|million|B|M)?)', re.IGNORECASE),
    'net_income': re.compile(r'net\s+(?:income|profit)\s+(?:of\s+)?([^\s,]+(?:\s+(?:CNY|USD|RMB|billion|million|B|M))+|(?:CNY|USD|RMB|\$)\s*[\d.]+\s*(?:billion|million|B|M)?)', re.IGNORECASE),
    'nim': re.compile(r'(?:net\s+interest\s+margin|NIM)\s*(?:\(NIM\))?\s*(?:of\s+)?([\d.]+%)', re.IGNORECASE),
    # 匹配利润率: "margins ~9%", "margin 9%", "operating margin of 9%"
    'operating_margin': re.compile(r'(?:operating\s+)?margins?\s+(?:of\s+)?(?:~|about\s+|approximately\s+)?([\d.]+%)', re.IGNORECASE),
    # 匹配业务部门及其贡献 - 更宽泛的模式
    # 模式1: "Retail Banking contributes 55% of sales"
    'division_contribution': re.compile(
        r'([A-Za-z][A-Za-z\s&]+?)\s+contributes?\s+([\d.]+%)\s+(?:of\s+)?(?:total\s+)?sales\s*'
        r'(?:\((?:gross\s+)?(?:profit\s+)?margin\s+([\d.]+%)?(?:,?\s*([\d.]+%)\s+(?:of\s+)?(?:group\s+)?profits?)?\))?',
        re.IGNORECASE
    ),
    # 模式2: "Concrete Machinery (e.g., pumps and mixers, 45% of FY2024 sales, 38% gross margin)"
    'division_parenthesis': re.compile(
        r'([A-Z][A-Za-z\s&]+?)\s*\([^)]*?(\d+%)\s+(?:of\s+)?(?:FY\d{4}\s+)?sales[^)]*?(?:(\d+%)\s+(?:gross\s+)?margin)?[^)]*\)',
        re.IGNORECASE
    ),
    # 模式3: "Division X (35% of sales, 32% margin)"
    'division_simple': re.compile(
        r'([A-Z][A-Za-z\s&]+?)\s*\((\d+%)\s+(?:of\s+)?sales(?:,\s*(\d+%)\s+margin)?\)',
        re.IGNORECASE
    ),
    # 匹配业务部门定义: "Retail Banking (focuses on personal loans, wealth management)"
    'division_def': re.compile(r'([A-Z][A-Za-z\s&]+?)\s*\((?:e\.g\.,?\s*)?([^)]+)\)', re.IGNORECASE),
}


def parse_business_overview_to_json(raw_text: str, company_name: str = "") -> str:
    """
    将 Business Overview 原始文本解析为结构化 JSON 字符串。
    优先提取 AI 生成的 ```business_overview_data``` 代码块，
    如果没有则回退到正则表达式解析。
    """
    if not raw_text or not raw_text.strip():
        return json.dumps({"raw_text": "", "parsed": None}, ensure_ascii=False)
    
    # 尝试提取 AI 生成的 JSON 代码块
    json_block_pattern = re.compile(r'```business_overview_data\s*\n?(.*?)\n?```', re.DOTALL | re.IGNORECASE)
    json_match = json_block_pattern.search(raw_text)
    
    # 提取纯文本部分（去除 JSON 块）
    clean_text = json_block_pattern.sub('', raw_text).strip()
    
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
                    parsed["divisions"].append({
                        "name": div.get("name", ""),
                        "description": div.get("description", ""),
                        "sales_percentage": div.get("sales_pct"),
                        "gross_profit_margin": div.get("gross_margin"),
                        "profit_percentage": div.get("profit_pct")
                    })
            
            print(f"  📊 成功从 JSON 块提取结构化数据: {len(parsed['key_metrics'])} 指标, {len(parsed['divisions'])} 部门")
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"  ⚠️ JSON 块解析失败，回退到正则: {e}")
            # 回退到正则解析
            parsed = _parse_with_regex(raw_text, company_name)
    else:
        # 没有 JSON 块，使用正则解析
        parsed = _parse_with_regex(raw_text, company_name)
    
    result = {
        "raw_text": clean_text if clean_text else raw_text,
        "parsed": parsed
    }
    
    return json.dumps(result, ensure_ascii=False, indent=None)


def _parse_with_regex(raw_text: str, company_name: str = "") -> dict:
    """使用正则表达式从文本中提取结构化数据（回退方案）"""
    parsed = {
        "company_name": company_name,
        "fiscal_year": None,
        "fiscal_year_end": None,
        "key_metrics": {},
        "divisions": [],
    }
    
    # 提取财年
    fy_match = BO_PATTERNS['fiscal_year'].search(raw_text)
    if fy_match:
        parsed["fiscal_year"] = fy_match.group(1) or None
        parsed["fiscal_year_end"] = fy_match.group(2) or None
    
    # 提取关键财务指标
    revenue_match = BO_PATTERNS['revenue'].search(raw_text)
    if revenue_match:
        parsed["key_metrics"]["total_revenue"] = revenue_match.group(1).strip()
    else:
        sales_match = BO_PATTERNS['sales_standalone'].search(raw_text)
        if sales_match:
            parsed["key_metrics"]["total_revenue"] = sales_match.group(1).strip()
    
    op_income_match = BO_PATTERNS['operating_income'].search(raw_text)
    if op_income_match:
        parsed["key_metrics"]["operating_income"] = op_income_match.group(1).strip()
    
    net_income_match = BO_PATTERNS['net_income'].search(raw_text)
    if net_income_match:
        parsed["key_metrics"]["net_income"] = net_income_match.group(1).strip()
    
    nim_match = BO_PATTERNS['nim'].search(raw_text)
    if nim_match:
        parsed["key_metrics"]["net_interest_margin"] = nim_match.group(1).strip()
    
    margin_match = BO_PATTERNS['operating_margin'].search(raw_text)
    if margin_match:
        parsed["key_metrics"]["operating_margin"] = margin_match.group(1).strip()
    
    # 提取部门数据
    added_divisions = set()
    
    for match in BO_PATTERNS['division_parenthesis'].finditer(raw_text):
        div_name = match.group(1).strip()
        sales_pct = match.group(2)
        margin = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
        
        div_key = div_name.lower()
        if div_key not in added_divisions and len(div_name) > 3:
            parsed["divisions"].append({
                "name": div_name,
                "description": "",
                "sales_percentage": sales_pct,
                "gross_profit_margin": margin,
                "profit_percentage": None
            })
            added_divisions.add(div_key)
    
    return parsed


def format_market_cap(mcap):
    """格式化市值显示"""
    if not mcap:
        return "N/A"
    if mcap >= 1e12:
        return f"{mcap/1e12:.2f}T"
    if mcap >= 1e9:
        return f"{mcap/1e9:.2f}B"
    if mcap >= 1e6:
        return f"{mcap/1e6:.2f}M"
    return f"{mcap:,.0f}"


def get_stock_data_sync(symbol):
    """同步获取股票数据 (将在线程池中运行)"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        last_price = info.get('regularMarketPreviousClose') or info.get('previousClose') or info.get('currentPrice')
        market_cap = info.get('marketCap')
        currency = info.get('currency', 'USD')
        return {
            'last_price': last_price,
            'market_cap': market_cap,
            'currency': currency,
            'success': True
        }
    except Exception:
        return {'last_price': None, 'market_cap': None, 'currency': '', 'success': False}


# ==========================================
# 3. 异步包装器 (Django ORM)
# ==========================================

@sync_to_async
def get_companies_async():
    return list(CSI300Company.objects.all().order_by('ticker', 'name'))


@sync_to_async
def save_summary_to_db_async(company_obj, summary_data):
    try:
        obj, created = CSI300InvestmentSummary.objects.update_or_create(
            company=company_obj,
            defaults=summary_data
        )
        return created
    except Exception as e:
        print(f"❌ [DB Error] {company_obj.name}: {e}")
        return None


# ==========================================
# 4. 两阶段并行处理架构
# ==========================================

async def fetch_all_stock_data(companies, executor):
    """
    阶段1: 并行获取所有公司的 Yahoo 股票数据
    不设并发限制，Yahoo API 通常不限流
    """
    loop = asyncio.get_running_loop()
    tasks = []
    
    for company in companies:
        ticker = company.ticker or ""
        if ticker:
            task = loop.run_in_executor(executor, get_stock_data_sync, ticker)
            tasks.append((company, task))
        else:
            tasks.append((company, None))
    
    print(f"📈 正在并行获取 {len(tasks)} 家公司的股票数据...")
    
    # 收集结果
    stock_data_map = {}
    success_count = 0
    
    for company, task in tasks:
        if task is None:
            stock_data_map[company.id] = {'last_price': None, 'market_cap': None, 'currency': '', 'success': False}
        else:
            try:
                result = await task
                stock_data_map[company.id] = result
                if result.get('success'):
                    success_count += 1
            except Exception:
                stock_data_map[company.id] = {'last_price': None, 'market_cap': None, 'currency': '', 'success': False}
    
    print(f"✅ 股票数据获取完成: {success_count}/{len(companies)} 成功")
    return stock_data_map


async def process_company_ai(
    ai_semaphore, 
    executor, 
    client, 
    company_obj, 
    stock_data, 
    template, 
    today,
    today_date,
    max_retries=AI_MAX_RETRIES
):
    """
    阶段2: 处理单个公司的 AI 调用 (股票数据已预获取)
    只对 AI 调用加信号量，DB 操作不加锁
    """
    loop = asyncio.get_running_loop()
    start_time = datetime.datetime.now()
    company_name = company_obj.name
    ticker = company_obj.ticker or ""
    
    result = {
        'company': company_name,
        'ticker': ticker,
        'status': 'failed',
        'message': '',
        'duration': 0,
    }

    # 准备股票数据文本
    stock_price_text = "N/A"
    market_cap_text = "N/A"
    currency = ""
    
    if stock_data and stock_data.get('last_price') is not None:
        stock_price_text = f"{stock_data['last_price']:.2f}"
        currency = stock_data.get('currency', '')
        market_cap_text = format_market_cap(stock_data.get('market_cap'))

    # 准备 Prompt
    prompt = template.format(company_name, ticker, today, stock_price_text, currency, market_cap_text, currency)

    # AI 调用 (带信号量限制并发)
    ai_content = None
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                # 优化 5: 指数退避 + 随机抖动
                wait_s = (2 ** attempt) + random.uniform(0, 1)
                print(f"🔄 [Retry {attempt}] {company_name}: 等待 {wait_s:.1f}s...")
                await asyncio.sleep(wait_s)

            # 优化 4: 只对 AI 调用加信号量
            async with ai_semaphore:
                def call_xai():
                    chat = client.chat.create(model=AI_MODEL)
                    chat.append(system(AI_SYSTEM_PROMPT))
                    chat.append(user(prompt))
                    return chat.sample()

                response = await loop.run_in_executor(executor, call_xai)
            
            if response and response.content and len(response.content.strip()) > 100:
                ai_content = response.content
                break
            else:
                print(f"⚠️ [AI Empty] {company_name}: 返回内容为空")
        except Exception as e:
            print(f"❌ [AI Error] {company_name} (Attempt {attempt+1}): {e}")

    if not ai_content:
        result['message'] = "AI Generation Failed"
        result['duration'] = (datetime.datetime.now() - start_time).total_seconds()
        print(f"🚫 [Failed] {company_name}")
        return result

    # 解析并写入数据库 (不加锁，快速操作)
    try:
        ai_sections = extract_ai_content_sections(ai_content)
        
        # 诊断日志：打印 AI 内容解析结果
        print(f"📊 [Parse] {company_name}: AI response length = {len(ai_content)}")
        print(f"📊 [Parse] {company_name}: Extracted sections = {list(ai_sections.keys())}")
        for key, val in ai_sections.items():
            print(f"   - {key}: {len(val) if val else 0} chars")
        
        stock_price_value = stock_data.get('last_price') if stock_data else None
        if stock_price_value is None:
            stock_price_value = getattr(company_obj, 'previous_close', 0)
        
        market_cap_display = "" if market_cap_text == "N/A" else f"{currency} {market_cap_text}".strip()

        # 解析 Business Overview 为结构化 JSON
        raw_business_overview = ai_sections.get('business_overview', '') or ''
        structured_business_overview = parse_business_overview_to_json(raw_business_overview, company_name)
        
        summary_data = {
            'report_date': today_date,
            'stock_price_previous_close': safe_decimal(stock_price_value),
            'market_cap_display': market_cap_display,
            'recommended_action': (ai_sections.get('recommended_action', '') or '')[:50],
            'recommended_action_detail': ai_sections.get('recommended_action_section', '') or '',
            'business_overview': structured_business_overview,  # 现在存储 JSON 字符串
            'business_performance': ai_sections.get('business_performance', '') or '',
            'industry_context': ai_sections.get('industry_context', '') or '',
            'financial_stability': ai_sections.get('financial_stability', '') or '',
            'key_financials_valuation': ai_sections.get('key_financials', '') or '',
            'big_trends_events': ai_sections.get('big_trends', '') or '',
            'customer_segments': ai_sections.get('customer_segments', '') or '',
            'competitive_landscape': ai_sections.get('competitive_landscape', '') or '',
            'risks_anomalies': ai_sections.get('risks_anomalies', '') or '',
            'forecast_outlook': ai_sections.get('forecast_outlook', '') or '',
            'investment_firms_views': ai_sections.get('investment_firms', '') or '',
            'industry_ratio_analysis': ai_sections.get('industry_ratio', '') or '',
            'tariffs_supply_chain_risks': '',
            'key_takeaways': ai_sections.get('key_takeaways', '') or '',
            'sources': ''
        }

        db_created = await save_summary_to_db_async(company_obj, summary_data)
        
        if db_created is not None:
            result['status'] = 'success'
            result['message'] = 'Created' if db_created else 'Updated'
            print(f"✅ [Done] {company_name} ({result['message']})")
        else:
            result['message'] = "DB Write Failed"

    except Exception as e:
        result['message'] = f"Error: {str(e)}"
        print(f"❌ [Error] {company_name}: {e}")

    result['duration'] = (datetime.datetime.now() - start_time).total_seconds()
    return result


# ==========================================
# 5. 单公司生成接口 (供 Django views 调用)
# ==========================================

async def generate_company_summary_async(company_id: int) -> Dict[str, Any]:
    """
    异步生成单个公司的 Investment Summary
    
    Args:
        company_id: 公司数据库 ID
        
    Returns:
        Dict 包含 status, message, data 等字段
    """
    try:
        # 获取公司对象
        company_obj = await sync_to_async(CSI300Company.objects.get)(id=company_id)
    except CSI300Company.DoesNotExist:
        return {
            'status': 'error',
            'message': f'公司 ID {company_id} 不存在',
            'data': None
        }
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_date = datetime.date.today()
    
    # 初始化资源
    client = Client(
        api_key=XAI_API_KEY,
        timeout=AI_TIMEOUT,
    )
    executor = ThreadPoolExecutor(max_workers=5)
    ai_semaphore = asyncio.Semaphore(1)
    
    # 获取股票数据
    ticker = company_obj.ticker or ""
    stock_data = {}
    if ticker:
        loop = asyncio.get_running_loop()
        stock_data = await loop.run_in_executor(executor, get_stock_data_sync, ticker)
    
    # 调用 AI 生成
    result = await process_company_ai(
        ai_semaphore,
        executor,
        client,
        company_obj,
        stock_data,
        PROMPT_TEMPLATE,
        today,
        today_date
    )
    
    executor.shutdown(wait=False)
    
    if result['status'] == 'success':
        # 获取最新的 summary 数据
        try:
            summary = await sync_to_async(
                lambda: CSI300InvestmentSummary.objects.filter(company=company_obj).first()
            )()
            return {
                'status': 'success',
                'message': result['message'],
                'data': {
                    'company_id': company_id,
                    'company_name': company_obj.name,
                    'ticker': ticker,
                    'duration': result['duration'],
                    'summary_exists': summary is not None
                }
            }
        except Exception as e:
            return {
                'status': 'success',
                'message': result['message'],
                'data': {
                    'company_id': company_id,
                    'company_name': company_obj.name,
                    'ticker': ticker,
                    'duration': result['duration']
                }
            }
    else:
        return {
            'status': 'error',
            'message': result['message'],
            'data': {
                'company_id': company_id,
                'company_name': company_obj.name,
                'duration': result.get('duration', 0)
            }
        }


def generate_company_summary(company_id: int) -> Dict[str, Any]:
    """
    同步接口：生成单个公司的 Investment Summary
    
    Args:
        company_id: 公司数据库 ID
        
    Returns:
        Dict 包含 status, message, data 等字段
    """
    return asyncio.run(generate_company_summary_async(company_id))


# ==========================================
# 6. 批量处理主程序 (独立运行时使用)
# ==========================================

async def main(company_id: Optional[int] = None, 
               company_name: Optional[str] = None,
               ticker: Optional[str] = None,
               fuzzy: bool = False):
    """
    主程序 - 可处理单个或批量公司
    
    Args:
        company_id: 指定公司 ID
        company_name: 指定公司名称
        ticker: 指定股票代码
        fuzzy: 是否模糊匹配公司名称
    """
    total_start_time = datetime.datetime.now()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_date = datetime.date.today()
    
    # 1. 初始化资源
    client = Client(
        api_key=XAI_API_KEY,
        timeout=AI_TIMEOUT, 
    )
    
    # 2. 获取任务列表
    print("📦 正在从数据库加载公司列表...")
    companies = await get_companies_async()
    companies = [c for c in companies if c.name]  # 过滤无效公司
    
    # 3. 根据参数过滤公司
    if company_id:
        companies = [c for c in companies if c.id == company_id]
        print(f"🔍 按 ID={company_id} 过滤")
    elif ticker:
        companies = [c for c in companies if c.ticker == ticker]
        print(f"🔍 按 Ticker={ticker} 过滤")
    elif company_name:
        if fuzzy:
            companies = [c for c in companies if company_name.lower() in c.name.lower()]
            print(f"🔍 按名称模糊匹配 '{company_name}'")
        else:
            companies = [c for c in companies if c.name == company_name]
            print(f"🔍 按名称精确匹配 '{company_name}'")
    
    if not companies:
        print("❌ 没有找到匹配的公司！")
        return
    
    print(f"📦 将处理 {len(companies)} 家公司:")
    for c in companies[:10]:  # 最多显示前10家
        print(f"   - {c.name} ({c.ticker})")
    if len(companies) > 10:
        print(f"   ... 还有 {len(companies) - 10} 家")
    
    # 4. 配置并发
    AI_CONCURRENCY = 20  # AI 并发数
    executor = ThreadPoolExecutor(max_workers=AI_CONCURRENCY * 2 + 20)
    ai_semaphore = asyncio.Semaphore(AI_CONCURRENCY)

    # 阶段1: 并行获取所有股票数据
    phase1_start = datetime.datetime.now()
    stock_data_map = await fetch_all_stock_data(companies, executor)
    phase1_duration = (datetime.datetime.now() - phase1_start).total_seconds()
    print(f"⏱️ 阶段1耗时: {phase1_duration:.1f}s")

    # 阶段2: 并行调用 AI
    print(f"\n🚀 启动AI处理 (Concurrency={AI_CONCURRENCY})...")
    phase2_start = datetime.datetime.now()
    
    tasks = []
    for company_obj in companies:
        stock_data = stock_data_map.get(company_obj.id, {})
        task = process_company_ai(
            ai_semaphore,
            executor,
            client,
            company_obj,
            stock_data,
            PROMPT_TEMPLATE,
            today,
            today_date
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    phase2_duration = (datetime.datetime.now() - phase2_start).total_seconds()
    
    # 5. 统计与收尾
    success_list = [r for r in results if r['status'] == 'success']
    fail_list = [r for r in results if r['status'] != 'success']
    
    total_duration = (datetime.datetime.now() - total_start_time).total_seconds()
    
    print("\n" + "="*60)
    print(f"📊 处理完成 Summary")
    print("="*60)
    print(f"✅ 成功: {len(success_list)}")
    print(f"❌ 失败: {len(fail_list)}")
    print(f"⏱️ 阶段1 (Yahoo): {phase1_duration:.1f}s")
    print(f"⏱️ 阶段2 (AI+DB): {phase2_duration:.1f}s")
    print(f"⏱️ 总耗时: {total_duration:.1f}s ({total_duration/60:.1f}min)")
    print("="*60)
    
    if fail_list:
        print("\n❌ 失败详情:")
        for f in fail_list:
            print(f"   - {f['company']}: {f['message']}")

    executor.shutdown(wait=False)
    
    return {
        'success': len(success_list),
        'failed': len(fail_list),
        'duration': total_duration,
        'results': results
    }


# ==========================================
# 7. 命令行入口 (独立脚本运行)
# ==========================================

if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path
    
    # 设置 Django 环境
    PROJECT_ROOT = Path(__file__).resolve().parents[4]
    SRC_DIR = PROJECT_ROOT / "src"
    DJANGO_API_DIR = SRC_DIR / "django_api"
    
    for path in (str(SRC_DIR), str(DJANGO_API_DIR)):
        if path not in sys.path:
            sys.path.insert(0, path)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
    
    import django
    django.setup()
    
    # 重新导入 models (Django 已初始化)
    from csi300.models import CSI300Company, CSI300InvestmentSummary
    
    parser = argparse.ArgumentParser(
        description='CSI300 Investment Summary 自动化生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  python investment_summary_generator.py                           # 处理所有公司
  python investment_summary_generator.py --company "ZTE Corp"      # 只处理 ZTE Corp
  python investment_summary_generator.py --ticker "000063.SZ"      # 只处理股票代码 000063.SZ
  python investment_summary_generator.py --id 1086                 # 只处理 ID 为 1086 的公司
  python investment_summary_generator.py --company "ZTE" --fuzzy   # 模糊匹配包含 "ZTE" 的公司
        '''
    )
    parser.add_argument('--company', '-c', type=str, help='公司名称 (精确匹配或模糊匹配)')
    parser.add_argument('--ticker', '-t', type=str, help='股票代码 (精确匹配)')
    parser.add_argument('--id', type=int, help='公司数据库 ID')
    parser.add_argument('--fuzzy', '-f', action='store_true', help='启用模糊匹配 (用于 --company)')
    
    args = parser.parse_args()
    
    asyncio.run(main(
        company_id=args.id,
        company_name=args.company,
        ticker=args.ticker,
        fuzzy=args.fuzzy
    ))
