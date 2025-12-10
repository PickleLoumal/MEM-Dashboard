"""
FRED Constants - 常量定义
定义FRED API和数据处理中使用的常量
"""

# FRED API配置
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
DEFAULT_TIMEOUT = 30  # 默认超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数

# 日期格式
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DISPLAY_DATE_FORMAT = "%b %Y"
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

# 支持的频率
SUPPORTED_FREQUENCIES = ["Annual", "Quarterly", "Monthly", "Weekly", "Daily"]

# 频率映射
FREQUENCY_MAPPING = {"a": "Annual", "q": "Quarterly", "m": "Monthly", "w": "Weekly", "d": "Daily"}

# 频率显示名称
FREQUENCY_DISPLAY = {
    "Annual": "年度",
    "Quarterly": "季度",
    "Monthly": "月度",
    "Weekly": "周度",
    "Daily": "日度",
}

# 单位映射
UNIT_MAPPING = {
    "Billions of Dollars": "Billions",
    "Millions of Dollars": "Millions",
    "Thousands of Dollars": "Thousands",
    "Percent": "Percent",
    "Index": "Index",
    "Rate": "Rate",
    "Ratio": "Ratio",
    "Number": "Number",
}

# 数据验证常量
MIN_VALID_YEAR = 1900
MAX_VALID_YEAR = 2100
MAX_DECIMAL_PLACES = 4
MAX_SERIES_ID_LENGTH = 50

# 错误消息
ERROR_MESSAGES = {
    "INVALID_SERIES_ID": "Invalid series ID format",
    "MISSING_API_KEY": "FRED API key not configured",
    "NETWORK_ERROR": "Network connection error",
    "RATE_LIMITED": "API rate limit exceeded",
    "DATA_NOT_FOUND": "No data available for the specified series",
    "INVALID_DATE_RANGE": "Invalid date range specified",
    "PARSING_ERROR": "Error parsing response data",
}

# HTTP状态码
HTTP_STATUS = {
    "OK": 200,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "NOT_FOUND": 404,
    "RATE_LIMITED": 429,
    "SERVER_ERROR": 500,
}

# 缓存设置
CACHE_TIMEOUT = {
    "SERIES_INFO": 3600 * 24,  # 24小时
    "LATEST_DATA": 3600 * 6,  # 6小时
    "HISTORICAL_DATA": 3600 * 12,  # 12小时
}

# 数据库相关常量
DB_TABLE_PREFIX = "fred"
DB_SCHEMA = "public"

# 默认查询限制
DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 1000

# 支持的国家代码
SUPPORTED_COUNTRIES = {"US": "United States", "JP": "Japan"}

# API响应字段
REQUIRED_SERIES_FIELDS = ["id", "title", "units", "frequency"]

REQUIRED_OBSERVATION_FIELDS = ["date", "value"]

# 数据质量检查
DATA_QUALITY = {
    "MIN_OBSERVATIONS": 10,
    "MAX_MISSING_RATIO": 0.3,  # 最大缺失值比例30%
    "OUTLIER_THRESHOLD": 3.0,  # 异常值检测阈值（标准差倍数）
}

# 日志级别
LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
