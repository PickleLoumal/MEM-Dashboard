"""
Stock Data Services - VWAP and Technical Indicators
Provides calculation services for VWAP, MA, OBV, CMF indicators
Integrates with AkShare for real-time and historical data
"""

import asyncio
import logging
import os
from datetime import UTC, datetime, timedelta
from datetime import time as datetime_time
from io import StringIO

import pandas as pd
from django.core.cache import cache

try:  # Optional dependency for distributed caching
    import redis.asyncio as redis_async  # type: ignore
except ImportError:  # pragma: no cover - redis not installed
    redis_async = None

from .akshare_client import MINUTE_PERIOD_MAP, get_daily_data, get_minute_data
from .models import StockScore

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")
redis_client = None
if redis_async and REDIS_URL:
    try:
        redis_client = redis_async.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=1.5,
        )
    except Exception as exc:  # pragma: no cover - connection issues
        logger.warning("Redis unavailable (%s); falling back to local cache only.", exc)
        redis_client = None
elif not REDIS_URL:
    logger.info("REDIS_URL not configured; Redis caching disabled for stock services.")

FULL_DAILY_LOOKBACK_DAYS = 3650  # ~10 years
FULL_DAILY_CACHE_TIMEOUT = 6 * 3600  # 6 hours
INTRADAY_CACHE_TIMEOUT = 60
INTRADAY_INTERVAL_CACHE_TIMEOUT = 120
DAILY_CACHE_TIMEOUT = 3600


def _determine_lookback_days(requested_days: int, interval: str) -> int:
    """
    Determine how many calendar days of data to request from AkShare to cover the required range.
    """
    if requested_days <= 0:
        requested_days = 1

    if interval in MINUTE_PERIOD_MAP:
        return min(max(requested_days, 5), 30)

    if interval == "1wk":
        return min(max(requested_days * 2, 240), 3650)

    if interval == "1mo":
        return min(max(requested_days * 2, 480), 3650)

    # Default for daily or other intervals
    return min(max(requested_days * 2, 120), 3650)


def _resample_ohlc(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample OHLCV data to a different frequency."""
    resampled = pd.DataFrame()
    resampled["Open"] = df["Open"].resample(rule).first()
    resampled["High"] = df["High"].resample(rule).max()
    resampled["Low"] = df["Low"].resample(rule).min()
    resampled["Close"] = df["Close"].resample(rule).last()
    resampled["Volume"] = df["Volume"].resample(rule).sum()
    resampled = resampled.dropna(subset=["Open", "High", "Low", "Close"])
    return resampled


def _normalize_cached_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.index, pd.Index) and df.index.dtype == object:
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:  # pragma: no cover - best effort conversion
            pass
    for column in ("Timestamp", "Date"):
        if column in df.columns and not pd.api.types.is_datetime64_any_dtype(df[column]):
            try:
                df[column] = pd.to_datetime(df[column])
            except Exception:  # pragma: no cover - best effort conversion
                pass
    return df


async def _cache_get_dataframe(key: str) -> pd.DataFrame | None:
    if redis_client is not None:
        try:
            payload = await redis_client.get(key)
            if payload:
                df = pd.read_json(StringIO(payload), orient="split")
                return _normalize_cached_dataframe(df)
        except Exception as exc:  # pragma: no cover
            logger.debug("Redis get failed for %s: %s", key, exc)

    cached = cache.get(key)
    if cached:
        try:
            df = pd.read_json(StringIO(cached), orient="split")
            return _normalize_cached_dataframe(df)
        except ValueError:
            cache.delete(key)
    return None


async def _cache_set_dataframe(key: str, df: pd.DataFrame, timeout: int) -> None:
    payload = df.to_json(orient="split")
    if redis_client is not None:
        try:
            await redis_client.set(key, payload, ex=timeout)
        except Exception as exc:  # pragma: no cover
            logger.debug("Redis set failed for %s: %s", key, exc)
    cache.set(key, payload, timeout=timeout)


def _run_async(func, *args, **kwargs):
    try:
        return asyncio.run(func(*args, **kwargs))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()


async def _get_full_daily_dataframe(symbol: str) -> pd.DataFrame:
    cache_key = f"akshare:daily-full:{symbol}"
    cached = await _cache_get_dataframe(cache_key)
    if cached is not None and not cached.empty:
        return cached

    end_time = datetime.now(tz=UTC)
    start_time = end_time - timedelta(days=FULL_DAILY_LOOKBACK_DAYS)
    df = await asyncio.to_thread(get_daily_data, symbol, start_time, end_time)
    if df.empty:
        return df
    df["Date"] = pd.to_datetime(df["Date"])
    await _cache_set_dataframe(cache_key, df, timeout=FULL_DAILY_CACHE_TIMEOUT)
    return df


class VWAPCalculationService:
    """VWAP and technical indicators calculation service"""

    @staticmethod
    def get_latest_stock_score(symbol: str) -> dict | None:
        """Fetch latest stored scoring snapshot for a ticker from stock_scores table."""
        if not symbol:
            return None

        try:
            score = (
                StockScore.objects.filter(ticker=symbol)
                .order_by("-calculation_date", "-updated_at")
                .first()
            )
            if not score:
                return None

            def to_float(value):
                if value is None:
                    return None
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None

            return {
                "calculation_date": score.calculation_date.isoformat()
                if score.calculation_date
                else None,
                "total_score": to_float(score.total_score),
                "recommended_action": score.recommended_action or "",
                "recommended_action_detail": score.recommended_action_detail or "",
                "last_trading_date": score.last_trading_date.isoformat()
                if score.last_trading_date
                else None,
                "last_close": to_float(score.last_close),
                "score_components": score.score_components or {},
                "signal_date": score.signal_date.isoformat() if score.signal_date else None,
                "execution_date": score.execution_date.isoformat()
                if score.execution_date
                else None,
                "suggested_position_pct": to_float(score.suggested_position_pct),
                "stop_loss_price": to_float(score.stop_loss_price),
                "take_profit_price": to_float(score.take_profit_price),
            }
        except Exception as exc:
            logger.warning("Unable to fetch stock score for %s: %s", symbol, exc)
            return None

    @staticmethod
    def filter_trading_hours(df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter trading hours: 9:15-11:30, 13:00-15:00 (strict filtering for China market)
        """
        if df.empty:
            return df

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        times = df.index.time
        morning_start = datetime_time(9, 15)
        morning_end = datetime_time(11, 30)
        afternoon_start = datetime_time(13, 0)
        afternoon_end = datetime_time(15, 0)

        mask = ((times >= morning_start) & (times <= morning_end)) | (
            (times >= afternoon_start) & (times <= afternoon_end)
        )

        filtered_df = df[mask].copy()

        if not filtered_df.empty:
            filtered_df = filtered_df[~filtered_df.index.duplicated(keep="first")]

        return filtered_df

    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate VWAP Indicator"""
        df = df.copy()
        df["Typical_Price"] = (df["High"] + df["Low"] + df["Close"]) / 3
        df["TP_Volume"] = df["Typical_Price"] * df["Volume"]
        df["Cumulative_TP_Volume"] = df["TP_Volume"].cumsum()
        df["Cumulative_Volume"] = df["Volume"].cumsum()
        df["VWAP"] = df["Cumulative_TP_Volume"] / df["Cumulative_Volume"]
        return df

    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: list[int] | None = None) -> pd.DataFrame:
        """Calculate Moving Averages"""
        periods = periods or [5, 10]
        df = df.copy()
        for period in periods:
            df[f"MA{period}"] = df["Close"].rolling(window=period).mean()
        return df

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate On-Balance Volume (OBV)"""
        df = df.copy()
        df["OBV"] = 0.0

        for i in range(1, len(df)):
            if df["Close"].iloc[i] > df["Close"].iloc[i - 1]:
                df.loc[df.index[i], "OBV"] = df["OBV"].iloc[i - 1] + df["Volume"].iloc[i]
            elif df["Close"].iloc[i] < df["Close"].iloc[i - 1]:
                df.loc[df.index[i], "OBV"] = df["OBV"].iloc[i - 1] - df["Volume"].iloc[i]
            else:
                df.loc[df.index[i], "OBV"] = df["OBV"].iloc[i - 1]

        df["OBV_MA5"] = df["OBV"].rolling(window=5).mean()
        df["OBV_MA10"] = df["OBV"].rolling(window=10).mean()

        return df

    @staticmethod
    def calculate_cmf(df: pd.DataFrame, period: int = 21) -> pd.DataFrame:
        """Calculate Chaikin Money Flow (CMF)"""
        df = df.copy()

        df["MF_Multiplier"] = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (
            df["High"] - df["Low"]
        )
        df.loc[df["High"] == df["Low"], "MF_Multiplier"] = 0
        df["MF_Volume"] = df["MF_Multiplier"] * df["Volume"]
        df["CMF"] = (
            df["MF_Volume"].rolling(window=period).sum() / df["Volume"].rolling(window=period).sum()
        )

        return df

    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = VWAPCalculationService.calculate_ma(df, [5, 10])
        df = VWAPCalculationService.calculate_obv(df)
        df = VWAPCalculationService.calculate_cmf(df, 21)
        return df

    @staticmethod
    def get_intraday_data(symbol: str, market: str = "CN") -> pd.DataFrame | None:
        try:
            df = _run_async(VWAPCalculationService._get_intraday_async, symbol, market)
            if df is not None and df.empty:
                return None
            return df
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to get intraday data for %s via AkShare", symbol)
            return None

    @staticmethod
    async def _get_intraday_async(symbol: str, market: str) -> pd.DataFrame:
        cache_key = f"akshare:intraday:{symbol}:{market}"
        cached = await _cache_get_dataframe(cache_key)
        if cached is not None and not cached.empty:
            return cached

        df = await asyncio.to_thread(get_minute_data, symbol, "1m")
        if df.empty:
            logger.warning("No intraday data available for %s via AkShare.", symbol)
            return pd.DataFrame()

        df = df[df["Volume"] > 0]

        if market == "CN":
            df = VWAPCalculationService.filter_trading_hours(df)

        if df.empty:
            logger.warning("Intraday data empty after market-hour filtering for %s.", symbol)
            return pd.DataFrame()

        await _cache_set_dataframe(cache_key, df, timeout=INTRADAY_CACHE_TIMEOUT)

        logger.info(
            "Intraday data for %s: %s to %s (%d bars)",
            symbol,
            df.index[0],
            df.index[-1],
            len(df),
        )

        return df

    @staticmethod
    def get_historical_data(
        symbol: str, days: int = 30, interval: str = "1d", period: str | None = None
    ) -> pd.DataFrame | None:
        try:
            df_display = _run_async(
                VWAPCalculationService._get_historical_async,
                symbol,
                days,
                interval,
                period,
            )
            if df_display is not None and df_display.empty:
                return None
            return df_display
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Failed to get historical data for %s via AkShare", symbol)
            return None

    @staticmethod
    async def _get_historical_async(
        symbol: str, days: int, interval: str, period: str | None
    ) -> pd.DataFrame:
        if period:
            logger.info(
                "Ignoring period=%s for %s; using days=%s with AkShare data.",
                period,
                symbol,
                days,
            )

        cache_key = f"akshare:hist:{symbol}:{interval}:{days}:{period or 'none'}"
        cached = await _cache_get_dataframe(cache_key)
        if cached is not None and not cached.empty:
            return cached

        if interval in MINUTE_PERIOD_MAP:
            df = await asyncio.to_thread(get_minute_data, symbol, interval)
            if df.empty:
                logger.warning("No %s minute data available for %s via AkShare.", interval, symbol)
                return pd.DataFrame()
            df = df[df["Volume"] > 0]

            df_full = df.copy()
            if len(df_full) > 21:
                df_full = VWAPCalculationService.calculate_all_indicators(df_full)
            logger.info(
                "Intraday data: %d data points for %s at %s interval",
                len(df_full),
                symbol,
                interval,
            )

            df_display = df_full.reset_index()
            if "Datetime" in df_display.columns:
                df_display = df_display.rename(columns={"Datetime": "Timestamp"})
            elif "index" in df_display.columns:
                df_display = df_display.rename(columns={"index": "Timestamp"})
            df_display["Date_Str"] = df_display["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
            df_display["Trading_Day"] = range(1, len(df_display) + 1)
            await _cache_set_dataframe(
                cache_key, df_display, timeout=INTRADAY_INTERVAL_CACHE_TIMEOUT
            )
            return df_display

        full_df = await _get_full_daily_dataframe(symbol)
        if full_df.empty:
            logger.warning("No historical data available for %s via AkShare.", symbol)
            return pd.DataFrame()

        full_df = full_df.copy()
        full_df["Date"] = pd.to_datetime(full_df["Date"])

        lookback_days = _determine_lookback_days(days, interval)
        cutoff = datetime.now(tz=UTC) - timedelta(days=lookback_days)
        df = full_df[full_df["Date"] >= cutoff].copy()
        if df.empty:
            df = full_df.tail(days * 2 or 60).copy()

        df = df.set_index("Date")

        if interval == "1wk":
            df = _resample_ohlc(df, "W")
        elif interval == "1mo":
            df = _resample_ohlc(df, "M")

        if df.empty:
            logger.warning("Historical data empty after processing for %s.", symbol)
            return pd.DataFrame()

        min_calc_days = 30
        calculation_days = max(min_calc_days, min(days * 2, len(df)))
        df_full = df.tail(calculation_days).copy()
        df_full = VWAPCalculationService.calculate_all_indicators(df_full)
        logger.info("Historical data: %d data points for %s", len(df_full), symbol)

        df_display = df_full.reset_index()
        if "Date" in df_display.columns:
            df_display = df_display.rename(columns={"Date": "Timestamp"})
        elif "index" in df_display.columns:
            df_display = df_display.rename(columns={"index": "Timestamp"})
        df_display["Date_Str"] = df_display["Timestamp"].dt.strftime("%Y-%m-%d")
        df_display["Trading_Day"] = range(1, len(df_display) + 1)

        await _cache_set_dataframe(cache_key, df_display, timeout=DAILY_CACHE_TIMEOUT)
        return df_display

    @staticmethod
    def format_intraday_response(
        df: pd.DataFrame, symbol: str, company_name: str, company_data: dict | None = None
    ) -> dict:
        """
        Format intraday data for API response
        """
        if df is None or df.empty:
            return {"success": False, "message": "No data available", "data": None}

        df = VWAPCalculationService.calculate_vwap(df)
        open_price = float(df["Open"].iloc[0])

        # Use database values if available
        if company_data:
            if company_data.get("previous_close") is not None:
                previous_close = float(company_data["previous_close"])
            else:
                previous_close = open_price  # Fallback

            if company_data.get("open") is not None:
                open_price = float(company_data["open"])
        else:
            previous_close = open_price

        data_points = []
        for idx, row in df.iterrows():
            data_points.append(
                {
                    "time": idx.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "vwap": float(row["VWAP"]),
                }
            )

        latest = df.iloc[-1]
        current_price = float(latest["Close"])

        score_snapshot = VWAPCalculationService.get_latest_stock_score(symbol)

        return {
            "success": True,
            "symbol": symbol,
            "company_name": company_name,
            "previous_close": previous_close,
            "open_price": open_price,
            "current_price": current_price,
            "change": current_price - previous_close,
            "change_pct": (current_price - previous_close) / previous_close * 100
            if previous_close != 0
            else 0,
            "high": float(df["High"].max()),
            "low": float(df["Low"].min()),
            "volume": int(df["Volume"].sum()),
            "day_range": f"{float(df['Low'].min()):.2f} - {float(df['High'].max()):.2f}",
            "data_points": data_points,
            "update_time": datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S"),
            "price_52w_high": company_data.get("price_52w_high") if company_data else None,
            "price_52w_low": company_data.get("price_52w_low") if company_data else None,
            "last_trade_date": str(company_data.get("last_trade_date"))
            if company_data and company_data.get("last_trade_date")
            else None,
            "stock_score": score_snapshot,
        }

    @staticmethod
    def format_historical_response(
        df: pd.DataFrame, symbol: str, company_name: str, company_data: dict | None = None
    ) -> dict:
        """
        Format historical data for API response
        """
        if df is None or df.empty:
            return {"success": False, "message": "No data available", "data": None}

        data_points = []
        for _, row in df.iterrows():
            point = {
                "date": row["Date_Str"],
                "trading_day": int(row["Trading_Day"]),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            }

            if pd.notna(row.get("MA5")):
                point["ma5"] = float(row["MA5"])
            if pd.notna(row.get("MA10")):
                point["ma10"] = float(row["MA10"])
            if pd.notna(row.get("OBV")):
                point["obv"] = float(row["OBV"])
            if pd.notna(row.get("OBV_MA5")):
                point["obv_ma5"] = float(row["OBV_MA5"])
            if pd.notna(row.get("OBV_MA10")):
                point["obv_ma10"] = float(row["OBV_MA10"])
            if pd.notna(row.get("CMF")):
                point["cmf"] = float(row["CMF"])

            data_points.append(point)

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        high_val = float(df["High"].max())
        low_val = float(df["Low"].min())
        day_range = f"{low_val:.2f} - {high_val:.2f}"

        if company_data:
            previous_close = (
                float(company_data["previous_close"])
                if company_data.get("previous_close")
                else float(prev["Close"])
            )
            open_price = (
                float(company_data["open"]) if company_data.get("open") else float(latest["Open"])
            )
        else:
            previous_close = float(prev["Close"])
            open_price = float(latest["Open"])

        score_snapshot = VWAPCalculationService.get_latest_stock_score(symbol)

        return {
            "success": True,
            "symbol": symbol,
            "company_name": company_name,
            "previous_close": previous_close,
            "open_price": open_price,
            "current_price": float(latest["Close"]),
            "latest_close": float(latest["Close"]),
            "change": float(latest["Close"] - previous_close),
            "change_pct": float((latest["Close"] - previous_close) / previous_close * 100)
            if previous_close != 0
            else 0,
            "day_range": day_range,
            "volume": int(df["Volume"].sum()),
            "cmf": float(latest["CMF"]) if pd.notna(latest.get("CMF")) else 0,
            "obv": int(latest["OBV"]) if pd.notna(latest.get("OBV")) else 0,
            "trading_days": len(df),
            "data_points": data_points,
            "price_52w_high": company_data.get("price_52w_high") if company_data else None,
            "price_52w_low": company_data.get("price_52w_low") if company_data else None,
            "last_trade_date": str(company_data.get("last_trade_date"))
            if company_data and company_data.get("last_trade_date")
            else None,
            "stock_score": score_snapshot,
        }
