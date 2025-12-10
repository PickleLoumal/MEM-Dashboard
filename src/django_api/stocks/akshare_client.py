import logging
from datetime import datetime

import akshare as ak
import pandas as pd

logger = logging.getLogger(__name__)

# Mapping of application intervals to AkShare period strings
MINUTE_PERIOD_MAP = {
    "1m": "1",
    "2m": "1",  # closest available period
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "60m": "60",
}


def normalize_symbol(symbol: str) -> str | None:
    """Convert Yahoo-style ticker (e.g., 600519.SS) to AkShare symbol (e.g., sz600519)."""
    if not symbol:
        return None

    parts = symbol.upper().split(".")
    if len(parts) != 2:
        logger.error("Unsupported symbol format for AkShare: %s", symbol)
        return None

    code, suffix = parts
    prefix_map = {
        "SS": "sh",
        "SH": "sh",
        "SZ": "sz",
    }

    prefix = prefix_map.get(suffix)
    if not prefix:
        logger.error("AkShare client does not support suffix '%s' (symbol: %s)", suffix, symbol)
        return None

    return f"{prefix}{code}"


def get_minute_data(symbol: str, interval: str = "1m", adjust: str = "") -> pd.DataFrame:
    """Fetch intraday minute data using AkShare and return a cleaned DataFrame."""
    ak_symbol = normalize_symbol(symbol)
    if not ak_symbol:
        return pd.DataFrame()

    period = MINUTE_PERIOD_MAP.get(interval, "1")
    try:
        df_raw = ak.stock_zh_a_minute(symbol=ak_symbol, period=period, adjust=adjust)
    except Exception:  # pragma: no cover - upstream network issues
        logger.exception("AkShare minute data request failed for %s", symbol)
        return pd.DataFrame()

    if df_raw is None or df_raw.empty:
        return pd.DataFrame()

    df_raw = df_raw.rename(
        columns={
            "day": "Datetime",
            "open": "Open",
            "close": "Close",
            "high": "High",
            "low": "Low",
            "volume": "Volume",
        }
    )

    df_raw["Datetime"] = pd.to_datetime(df_raw["Datetime"], errors="coerce")
    df_raw = df_raw.dropna(subset=["Datetime"])
    df_raw = df_raw.sort_values("Datetime")

    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    df_raw = df_raw.dropna(subset=["Open", "High", "Low", "Close"])
    df_raw = df_raw[df_raw["Volume"].fillna(0) >= 0]

    latest_date = df_raw["Datetime"].dt.date.max()
    if pd.notna(latest_date):
        df_raw = df_raw[df_raw["Datetime"].dt.date == latest_date]

    df_raw = df_raw.set_index("Datetime")
    df_raw = df_raw[~df_raw.index.duplicated(keep="first")]
    df_raw["Volume"] = df_raw["Volume"].fillna(0).round().astype(int)

    return df_raw[["Open", "High", "Low", "Close", "Volume"]]


def get_daily_data(symbol: str, start: datetime, end: datetime, adjust: str = "") -> pd.DataFrame:
    """Fetch daily data via AkShare, with Tencent fallback when necessary."""
    ak_symbol = normalize_symbol(symbol)
    if not ak_symbol:
        return pd.DataFrame()

    start_str = start.strftime("%Y%m%d") if isinstance(start, datetime) else str(start)
    end_str = end.strftime("%Y%m%d") if isinstance(end, datetime) else str(end)

    df_raw = pd.DataFrame()

    try:
        df_raw = ak.stock_zh_a_hist(
            symbol=ak_symbol,
            period="daily",
            start_date=start_str,
            end_date=end_str,
            adjust=adjust,
        )
    except Exception as exc:  # pragma: no cover - upstream failure
        logger.debug("stock_zh_a_hist failed for %s: %s; trying Tencent fallback.", symbol, exc)

    if df_raw is None or df_raw.empty:
        try:
            df_raw = ak.stock_zh_a_hist_tx(
                symbol=ak_symbol,
                start_date=start_str,
                end_date=end_str,
            )
        except Exception:  # pragma: no cover
            logger.exception("AkShare daily data request failed for %s", symbol)
            return pd.DataFrame()

    if df_raw is None or df_raw.empty:
        return pd.DataFrame()

    if "日期" in df_raw.columns:
        df_raw = df_raw.rename(
            columns={
                "日期": "Date",
                "开盘": "Open",
                "最高": "High",
                "最低": "Low",
                "收盘": "Close",
                "成交量": "Volume",
            }
        )
    else:
        df_raw = df_raw.rename(
            columns={
                "date": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
        )
        if "Volume" not in df_raw or df_raw["Volume"].isna().all():
            df_raw["Volume"] = df_raw.get("amount", 0)

    df_raw["Date"] = pd.to_datetime(df_raw["Date"], errors="coerce")
    df_raw = df_raw.dropna(subset=["Date"])
    df_raw = df_raw.sort_values("Date")

    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    df_raw = df_raw.dropna(subset=["Open", "High", "Low", "Close"])
    df_raw["Volume"] = df_raw["Volume"].fillna(0).round().astype(int)

    return df_raw[["Date", "Open", "High", "Low", "Close", "Volume"]]
