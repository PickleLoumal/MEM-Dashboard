"""
FRED Utilities - 通用工具函数
为FRED数据处理提供通用的工具函数
"""

import logging
import re
import time
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from .constants import (
    DEFAULT_DATE_FORMAT,
    DISPLAY_DATE_FORMAT,
    FREQUENCY_DISPLAY,
    MAX_SERIES_ID_LENGTH,
    MAX_VALID_YEAR,
    MIN_VALID_YEAR,
    UNIT_MAPPING,
)

logger = logging.getLogger(__name__)


def format_date(date_input: str | datetime, output_format: str = DISPLAY_DATE_FORMAT) -> str:
    """格式化日期显示"""
    try:
        if isinstance(date_input, str):
            # 尝试解析字符串日期
            date_obj = datetime.strptime(date_input, DEFAULT_DATE_FORMAT).replace(tzinfo=UTC)
        elif isinstance(date_input, datetime):
            date_obj = date_input
        else:
            raise ValueError(f"Unsupported date type: {type(date_input)}")

        return date_obj.strftime(output_format)
    except (ValueError, TypeError) as e:
        logger.warning(f"Date formatting error: {e}")
        return str(date_input)


def calculate_yoy_change(
    current_value: float | Decimal, previous_value: float | Decimal
) -> float | None:
    """计算同比变化率"""
    try:
        current = float(current_value)
        previous = float(previous_value)

        if previous == 0:
            return None

        change = ((current - previous) / previous) * 100
        return round(change, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def calculate_period_change(
    current_value: float | Decimal, previous_value: float | Decimal
) -> float | None:
    """计算期间变化率（通用）"""
    return calculate_yoy_change(current_value, previous_value)


def validate_series_id(series_id: str) -> bool:
    """验证FRED系列ID格式"""
    if not series_id or not isinstance(series_id, str):
        return False

    if len(series_id) > MAX_SERIES_ID_LENGTH:
        return False

    # FRED系列ID通常由字母、数字和少数特殊字符组成
    pattern = r"^[A-Z0-9_.-]+$"
    return bool(re.match(pattern, series_id.upper()))


def clean_numeric_value(value: str | float | int | Decimal) -> float | None:
    """清理并转换数值"""
    if value is None or value in {".", ""}:
        return None

    try:
        # 如果已经是数值类型
        if isinstance(value, (int, float)):
            return float(value)

        # 如果是Decimal类型
        if isinstance(value, Decimal):
            return float(value)

        # 如果是字符串，清理并转换
        if isinstance(value, str):
            # 移除常见的非数值字符
            cleaned = re.sub(r"[,\s$%]", "", value.strip())

            # 处理负号和括号表示的负数
            if cleaned.startswith("(") and cleaned.endswith(")"):
                cleaned = "-" + cleaned[1:-1]

            return float(cleaned)

        return None
    except (ValueError, InvalidOperation, TypeError):
        return None


def format_numeric_value(
    value: float | int | Decimal, unit: str | None = None, decimal_places: int = 2
) -> str:
    """格式化数值显示"""
    try:
        num_value = float(value)

        # 根据单位类型格式化
        if unit:
            unit_lower = unit.lower()
            if "percent" in unit_lower or "%" in unit_lower:
                return f"{num_value:.{decimal_places}f}%"
            if "billion" in unit_lower:
                return f"{num_value:,.1f}B"
            if "million" in unit_lower:
                return f"{num_value:,.1f}M"
            if "thousand" in unit_lower:
                return f"{num_value:,.1f}K"

        # 默认格式化
        if abs(num_value) >= 1000000:
            return f"{num_value:,.1f}M"
        if abs(num_value) >= 1000:
            return f"{num_value:,.1f}K"
        return f"{num_value:,.{decimal_places}f}"

    except (ValueError, TypeError):
        return str(value)


def validate_date_range(start_date: str, end_date: str) -> bool:
    """验证日期范围"""
    try:
        start = datetime.strptime(start_date, DEFAULT_DATE_FORMAT).replace(tzinfo=UTC)
        end = datetime.strptime(end_date, DEFAULT_DATE_FORMAT).replace(tzinfo=UTC)

        # 检查年份范围
        if start.year < MIN_VALID_YEAR or end.year > MAX_VALID_YEAR:
            return False

        # 检查日期顺序
        if start > end:
            return False

        # 检查范围不能超过100年
        return not (end - start).days > 365 * 100
    except ValueError:
        return False


def get_formatted_date_range(days_back: int = 365) -> tuple[str, str]:
    """生成格式化的日期范围"""
    end_date = datetime.now(tz=UTC)
    start_date = end_date - timedelta(days=days_back)

    return (start_date.strftime(DEFAULT_DATE_FORMAT), end_date.strftime(DEFAULT_DATE_FORMAT))


def parse_frequency(frequency: str) -> str:
    """解析并标准化频率"""
    if not frequency:
        return ""

    freq_lower = frequency.lower()

    # 标准化频率名称
    if freq_lower in ["a", "annual", "yearly"]:
        return "Annual"
    if freq_lower in ["q", "quarterly"]:
        return "Quarterly"
    if freq_lower in ["m", "monthly"]:
        return "Monthly"
    if freq_lower in ["w", "weekly"]:
        return "Weekly"
    if freq_lower in ["d", "daily"]:
        return "Daily"
    return frequency.capitalize()


def get_frequency_display(frequency: str) -> str:
    """获取频率的显示名称"""
    standardized = parse_frequency(frequency)
    return FREQUENCY_DISPLAY.get(standardized, standardized)


def normalize_unit(unit: str) -> str:
    """标准化单位名称"""
    if not unit:
        return ""

    return UNIT_MAPPING.get(unit, unit)


def safe_divide(numerator: float | int, denominator: float | int) -> float | None:
    """安全除法，避免除零错误"""
    try:
        if denominator == 0:
            return None
        return float(numerator) / float(denominator)
    except (ValueError, TypeError):
        return None


def calculate_growth_rate(values: list[float | int], periods: int = 1) -> list[float | None]:
    """计算增长率序列"""
    if not values or len(values) < periods + 1:
        return []

    growth_rates: list[float | None] = [None] * periods  # 前几个值没有足够的历史数据

    for i in range(periods, len(values)):
        current = values[i]
        previous = values[i - periods]

        if current is not None and previous is not None and previous != 0:
            rate = ((current - previous) / previous) * 100
            growth_rates.append(round(rate, 2))
        else:
            growth_rates.append(None)

    return growth_rates


def detect_outliers(values: list[float | int], threshold: float = 3.0) -> list[bool]:
    """检测异常值（使用标准差方法）"""
    if not values or len(values) < 3:
        return [False] * len(values)

    # 过滤掉None值计算统计量
    numeric_values = [v for v in values if v is not None]
    if len(numeric_values) < 3:
        return [False] * len(values)

    mean_val = sum(numeric_values) / len(numeric_values)
    variance = sum((x - mean_val) ** 2 for x in numeric_values) / len(numeric_values)
    std_dev = variance**0.5

    if std_dev == 0:
        return [False] * len(values)

    # 标记异常值
    outliers = []
    for value in values:
        if value is None:
            outliers.append(False)
        else:
            z_score = abs(value - mean_val) / std_dev
            outliers.append(z_score > threshold)

    return outliers


def clean_text(text: str, max_length: int | None = None) -> str:
    """清理文本内容"""
    if not text:
        return ""

    # 移除多余空白
    cleaned = " ".join(text.split())

    # 截断长度
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[: max_length - 3] + "..."

    return cleaned


def build_error_response(error_type: str, message: str, **kwargs) -> dict[str, Any]:
    """构建标准错误响应"""
    response = {
        "success": False,
        "error": error_type,
        "message": message,
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }
    response.update(kwargs)
    return response


def build_success_response(data: Any, **kwargs) -> dict[str, Any]:
    """构建标准成功响应"""
    response = {"success": True, "data": data, "timestamp": datetime.now(tz=UTC).isoformat()}
    response.update(kwargs)
    return response


def chunk_list(items: list[Any], chunk_size: int) -> Generator[list[Any]]:
    """将列表分块处理"""
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """重试装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (2**attempt))  # 指数退避
                        continue
                    break

            if last_exception:
                logger.error(
                    f"Function {func.__name__} failed after {max_attempts} attempts: {last_exception}"
                )
                raise last_exception
            raise RuntimeError(f"Function {func.__name__} failed after {max_attempts} attempts")

        return wrapper

    return decorator
