"""
Investment Summary Generator Core Module

核心生成逻辑 - 包括异步 AI 调用、数据库操作、单公司和批量处理。
"""

import asyncio
import datetime
import logging
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from asgiref.sync import sync_to_async
from xai_sdk import Client
from xai_sdk.chat import system, user

from .parser import (
    extract_ai_content_sections,
    extract_sources_from_key_takeaways,
    parse_business_overview_to_json,
)
from .prompt import AI_MAX_RETRIES, AI_MODEL, AI_SYSTEM_PROMPT, AI_TIMEOUT, PROMPT_TEMPLATE
from .utils import XAI_API_KEY, format_market_cap, get_stock_data_sync, safe_decimal

logger = logging.getLogger(__name__)

# Django Models (延迟导入以避免循环依赖)
try:
    from csi300.models import CSI300Company, CSI300InvestmentSummary
except ImportError:
    CSI300Company = None
    CSI300InvestmentSummary = None


# ==========================================
# 异步包装器 (Django ORM)
# ==========================================


@sync_to_async
def get_companies_async() -> list:
    """异步获取所有公司"""
    return list(CSI300Company.objects.all().order_by("ticker", "name"))


@sync_to_async
def save_summary_to_db_async(company_obj, summary_data: dict) -> bool | None:
    """异步保存摘要到数据库"""
    try:
        _obj, created = CSI300InvestmentSummary.objects.update_or_create(
            company=company_obj, defaults=summary_data
        )
        return created
    except Exception:
        logger.exception("DB Error for {company_obj.name}")
        return None


# ==========================================
# 两阶段并行处理架构
# ==========================================


async def fetch_all_stock_data(companies: list, executor: ThreadPoolExecutor) -> dict[int, dict]:
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

    logger.info(f"Fetching stock data for {len(tasks)} companies in parallel...")

    # 收集结果
    stock_data_map = {}
    success_count = 0

    for company, task in tasks:
        if task is None:
            stock_data_map[company.id] = {
                "last_price": None,
                "market_cap": None,
                "currency": "",
                "success": False,
            }
        else:
            try:
                result = await task
                stock_data_map[company.id] = result
                if result.get("success"):
                    success_count += 1
            except Exception:
                stock_data_map[company.id] = {
                    "last_price": None,
                    "market_cap": None,
                    "currency": "",
                    "success": False,
                }

    logger.info(f"Stock data fetch complete: {success_count}/{len(companies)} successful")
    return stock_data_map


async def process_company_ai(
    ai_semaphore: asyncio.Semaphore,
    executor: ThreadPoolExecutor,
    client: Client,
    company_obj,
    stock_data: dict,
    template: str,
    today: str,
    today_date: datetime.date,
    max_retries: int = AI_MAX_RETRIES,
) -> dict[str, Any]:
    """
    阶段2: 处理单个公司的 AI 调用 (股票数据已预获取)
    只对 AI 调用加信号量，DB 操作不加锁
    """
    loop = asyncio.get_running_loop()
    start_time = datetime.datetime.now(tz=datetime.UTC)
    company_name = company_obj.name
    ticker = company_obj.ticker or ""

    result = {
        "company": company_name,
        "ticker": ticker,
        "status": "failed",
        "message": "",
        "duration": 0,
    }

    # 准备股票数据文本
    stock_price_text = "N/A"
    market_cap_text = "N/A"
    currency = ""

    if stock_data and stock_data.get("last_price") is not None:
        stock_price_text = f"{stock_data['last_price']:.2f}"
        currency = stock_data.get("currency", "")
        market_cap_text = format_market_cap(stock_data.get("market_cap"))

    # 准备 Prompt
    prompt = template.format(
        company_name, ticker, today, stock_price_text, currency, market_cap_text, currency
    )

    # AI 调用 (带信号量限制并发)
    ai_content = None

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                # 指数退避 + 随机抖动
                wait_s = (2**attempt) + random.uniform(0, 1)
                logger.info(f"Retry {attempt} for {company_name}: waiting {wait_s:.1f}s...")
                await asyncio.sleep(wait_s)

            # 只对 AI 调用加信号量
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
            logger.warning(f"AI returned empty content for {company_name}")
        except Exception:
            logger.exception("AI Error for {company_name} (Attempt {attempt + 1})")

    if not ai_content:
        result["message"] = "AI Generation Failed"
        result["duration"] = (datetime.datetime.now(tz=datetime.UTC) - start_time).total_seconds()
        logger.error(f"Failed to generate summary for {company_name}")
        return result

    # 解析并写入数据库
    try:
        ai_sections = extract_ai_content_sections(ai_content)

        logger.debug(f"Parse result for {company_name}: AI response length = {len(ai_content)}")
        logger.debug(f"Extracted sections: {list(ai_sections.keys())}")

        stock_price_value = stock_data.get("last_price") if stock_data else None
        if stock_price_value is None:
            stock_price_value = getattr(company_obj, "previous_close", 0)

        market_cap_display = (
            "" if market_cap_text == "N/A" else f"{currency} {market_cap_text}".strip()
        )

        # 解析 Business Overview 为结构化 JSON
        raw_business_overview = ai_sections.get("business_overview", "") or ""
        structured_business_overview = parse_business_overview_to_json(
            raw_business_overview, company_name
        )

        # Extract sources
        raw_key_takeaways = ai_sections.get("key_takeaways", "") or ""
        raw_sources = ai_sections.get("sources", "") or ""

        if raw_sources:
            cleaned_key_takeaways = raw_key_takeaways
            final_sources = raw_sources
        else:
            cleaned_key_takeaways, extracted_sources = extract_sources_from_key_takeaways(
                raw_key_takeaways
            )
            final_sources = extracted_sources

        summary_data = {
            "report_date": today_date,
            "stock_price_previous_close": safe_decimal(stock_price_value),
            "market_cap_display": market_cap_display,
            "recommended_action": (ai_sections.get("recommended_action", "") or "")[:50],
            "recommended_action_detail": ai_sections.get("recommended_action_section", "") or "",
            "business_overview": structured_business_overview,
            "business_performance": ai_sections.get("business_performance", "") or "",
            "industry_context": ai_sections.get("industry_context", "") or "",
            "financial_stability": ai_sections.get("financial_stability", "") or "",
            "key_financials_valuation": ai_sections.get("key_financials", "") or "",
            "big_trends_events": ai_sections.get("big_trends", "") or "",
            "customer_segments": ai_sections.get("customer_segments", "") or "",
            "competitive_landscape": ai_sections.get("competitive_landscape", "") or "",
            "risks_anomalies": ai_sections.get("risks_anomalies", "") or "",
            "forecast_outlook": ai_sections.get("forecast_outlook", "") or "",
            "investment_firms_views": ai_sections.get("investment_firms", "") or "",
            "industry_ratio_analysis": ai_sections.get("industry_ratio", "") or "",
            "tariffs_supply_chain_risks": "",
            "key_takeaways": cleaned_key_takeaways,
            "sources": final_sources,
        }

        db_created = await save_summary_to_db_async(company_obj, summary_data)

        if db_created is not None:
            result["status"] = "success"
            result["message"] = "Created" if db_created else "Updated"
            logger.info(f"Successfully processed {company_name} ({result['message']})")
        else:
            result["message"] = "DB Write Failed"

    except Exception as e:
        result["message"] = f"Error: {e!s}"
        logger.exception("Error processing {company_name}")

    result["duration"] = (datetime.datetime.now(tz=datetime.UTC) - start_time).total_seconds()
    return result


# ==========================================
# 单公司生成接口 (供 Django views 调用)
# ==========================================


async def generate_company_summary_async(company_id: int) -> dict[str, Any]:
    """
    异步生成单个公司的 Investment Summary

    Args:
        company_id: 公司数据库 ID

    Returns:
        Dict 包含 status, message, data 等字段
    """
    try:
        company_obj = await sync_to_async(CSI300Company.objects.get)(id=company_id)
    except CSI300Company.DoesNotExist:
        return {
            "status": "error",
            "message": f"Company ID {company_id} does not exist",
            "data": None,
        }

    today = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d")
    today_date = datetime.datetime.now(tz=datetime.UTC).date()

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
        ai_semaphore, executor, client, company_obj, stock_data, PROMPT_TEMPLATE, today, today_date
    )

    executor.shutdown(wait=False)

    if result["status"] == "success":
        try:
            summary = await sync_to_async(
                lambda: CSI300InvestmentSummary.objects.filter(company=company_obj).first()
            )()
            return {
                "status": "success",
                "message": result["message"],
                "data": {
                    "company_id": company_id,
                    "company_name": company_obj.name,
                    "ticker": ticker,
                    "duration": result["duration"],
                    "summary_exists": summary is not None,
                },
            }
        except Exception:
            return {
                "status": "success",
                "message": result["message"],
                "data": {
                    "company_id": company_id,
                    "company_name": company_obj.name,
                    "ticker": ticker,
                    "duration": result["duration"],
                },
            }
    else:
        return {
            "status": "error",
            "message": result["message"],
            "data": {
                "company_id": company_id,
                "company_name": company_obj.name,
                "duration": result.get("duration", 0),
            },
        }


def generate_company_summary(company_id: int) -> dict[str, Any]:
    """
    同步接口：生成单个公司的 Investment Summary

    Args:
        company_id: 公司数据库 ID

    Returns:
        Dict 包含 status, message, data 等字段
    """
    return asyncio.run(generate_company_summary_async(company_id))


# ==========================================
# 批量处理主程序
# ==========================================


async def main(
    company_id: int | None = None,
    company_name: str | None = None,
    ticker: str | None = None,
    fuzzy: bool = False,
) -> dict[str, Any]:
    """
    主程序 - 可处理单个或批量公司

    Args:
        company_id: 指定公司 ID
        company_name: 指定公司名称
        ticker: 指定股票代码
        fuzzy: 是否模糊匹配公司名称
    """
    total_start_time = datetime.datetime.now(tz=datetime.UTC)
    today = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d")
    today_date = datetime.datetime.now(tz=datetime.UTC).date()

    # 1. 初始化资源
    client = Client(
        api_key=XAI_API_KEY,
        timeout=AI_TIMEOUT,
    )

    # 2. 获取任务列表
    logger.info("Loading company list from database...")
    companies = await get_companies_async()
    companies = [c for c in companies if c.name]  # 过滤无效公司

    # 3. 根据参数过滤公司
    if company_id:
        companies = [c for c in companies if c.id == company_id]
        logger.info(f"Filtering by ID={company_id}")
    elif ticker:
        companies = [c for c in companies if c.ticker == ticker]
        logger.info(f"Filtering by Ticker={ticker}")
    elif company_name:
        if fuzzy:
            companies = [c for c in companies if company_name.lower() in c.name.lower()]
            logger.info(f"Fuzzy matching name '{company_name}'")
        else:
            companies = [c for c in companies if c.name == company_name]
            logger.info(f"Exact matching name '{company_name}'")

    if not companies:
        logger.error("No matching companies found!")
        return {"success": 0, "failed": 0, "duration": 0, "results": []}

    logger.info(f"Will process {len(companies)} companies")

    # 4. 配置并发
    AI_CONCURRENCY = 20
    executor = ThreadPoolExecutor(max_workers=AI_CONCURRENCY * 2 + 20)
    ai_semaphore = asyncio.Semaphore(AI_CONCURRENCY)

    # 阶段1: 并行获取所有股票数据
    phase1_start = datetime.datetime.now(tz=datetime.UTC)
    stock_data_map = await fetch_all_stock_data(companies, executor)
    phase1_duration = (datetime.datetime.now(tz=datetime.UTC) - phase1_start).total_seconds()
    logger.info(f"Phase 1 duration: {phase1_duration:.1f}s")

    # 阶段2: 并行调用 AI
    logger.info(f"Starting AI processing (Concurrency={AI_CONCURRENCY})...")
    phase2_start = datetime.datetime.now(tz=datetime.UTC)

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
            today_date,
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    phase2_duration = (datetime.datetime.now(tz=datetime.UTC) - phase2_start).total_seconds()

    # 5. 统计与收尾
    success_list = [r for r in results if r["status"] == "success"]
    fail_list = [r for r in results if r["status"] != "success"]

    total_duration = (datetime.datetime.now(tz=datetime.UTC) - total_start_time).total_seconds()

    logger.info("=" * 60)
    logger.info("Processing Summary")
    logger.info("=" * 60)
    logger.info(f"Success: {len(success_list)}")
    logger.info(f"Failed: {len(fail_list)}")
    logger.info(f"Phase 1 (Yahoo): {phase1_duration:.1f}s")
    logger.info(f"Phase 2 (AI+DB): {phase2_duration:.1f}s")
    logger.info(f"Total duration: {total_duration:.1f}s ({total_duration / 60:.1f}min)")
    logger.info("=" * 60)

    if fail_list:
        logger.warning("Failed companies:")
        for f in fail_list:
            logger.warning(f"  - {f['company']}: {f['message']}")

    executor.shutdown(wait=False)

    return {
        "success": len(success_list),
        "failed": len(fail_list),
        "duration": total_duration,
        "results": results,
    }


__all__ = [
    "fetch_all_stock_data",
    "generate_company_summary",
    "generate_company_summary_async",
    "main",
    "process_company_ai",
]
