import io
import logging
import subprocess
import sys
from contextlib import redirect_stdout
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from csi300.models import CSI300Company
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import StockScore
from .services import VWAPCalculationService

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:  # pragma: no cover - optional dependency in Django runtime
    from scripts.active import daily_score_calculator_db as score_calculator
except Exception as exc:  # pragma: no cover
    logger.warning("Unable to import scoring script: %s", exc)
    score_calculator = None


def _run_scoring_subprocess(symbol: str):
    """Fallback to running the scoring script via subprocess when import fails."""
    script_path = PROJECT_ROOT / "scripts" / "active" / "daily_score_calculator_db.py"
    if not script_path.exists():
        msg = f"Scoring script not found at {script_path}"
        raise RuntimeError(msg)

    cmd = [
        sys.executable,
        str(script_path),
        "--symbol",
        symbol,
        "--batch-size",
        "1",
        "--fetch-workers",
        "1",
    ]
    process = subprocess.run(cmd, check=False, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if process.returncode != 0:
        raise RuntimeError(process.stderr or process.stdout or "Scoring process failed")
    logs = process.stdout.splitlines()
    summary = {
        "total": 1,
        "successful": 1,
        "failed": 0,
        "symbols": [symbol],
        "calculation_date": datetime.now(tz=UTC).date().isoformat(),
    }
    return summary, logs


@extend_schema(
    responses={
        200: inline_serializer(
            name="StockListResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "count": drf_serializers.IntegerField(),
                "stocks": drf_serializers.ListField(child=drf_serializers.DictField()),
                "error": drf_serializers.CharField(required=False),
            },
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def stock_list(request):
    """获取股票列表 - 从CSI300 Company表读取"""
    try:
        # 从CSI300Company表读取所有有ticker的公司
        companies = CSI300Company.objects.filter(ticker__isnull=False).exclude(ticker="")

        stock_list = []
        for company in companies:
            stock_list.append(
                {
                    "symbol": company.ticker,
                    "name": company.name,
                    "exchange": "SSE/SZSE",  # 上交所/深交所
                    "sector": company.im_sector or "",
                    "industry": company.industry or "",
                }
            )

        return Response({"success": True, "count": len(stock_list), "stocks": stock_list})

    except Exception as e:
        logger.exception("Error fetching stock list")
        return Response(
            {"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="symbol",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Stock ticker symbol",
            required=True,
        )
    ],
    responses={
        200: inline_serializer(
            name="IntradayDataResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "symbol": drf_serializers.CharField(required=False),
                "data": drf_serializers.ListField(
                    child=drf_serializers.DictField(), required=False
                ),
                "error": drf_serializers.CharField(required=False),
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def intraday_data(request):
    """获取分时数据（1分钟K线）"""
    try:
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response(
                {"success": False, "error": "Symbol parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = CSI300Company.objects.get(ticker=symbol)
            company_name = company.name
            market = "CN"  # CSI300都是中国市场

            # 从数据库获取价格信息
            company_data = {
                "previous_close": company.previous_close,
                "open": company.price_local_currency,
                "price_52w_high": company.price_52w_high,
                "price_52w_low": company.price_52w_low,
                "last_trade_date": company.last_trade_date,
            }
        except CSI300Company.DoesNotExist:
            return Response(
                {"success": False, "error": f"Symbol {symbol} not found in CSI300 database"},
                status=status.HTTP_404_NOT_FOUND,
            )

        df = VWAPCalculationService.get_intraday_data(symbol, market)
        result = VWAPCalculationService.format_intraday_response(
            df, symbol, company_name, company_data
        )

        return Response(result)

    except Exception as e:
        logger.exception("Error fetching intraday data for {symbol}")
        return Response(
            {"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="symbol",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Stock ticker symbol",
            required=True,
        ),
        OpenApiParameter(
            name="days",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Number of days",
            required=False,
        ),
        OpenApiParameter(
            name="interval",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Data interval",
            required=False,
        ),
        OpenApiParameter(
            name="period",
            type=str,
            location=OpenApiParameter.QUERY,
            description="YFinance period",
            required=False,
        ),
    ],
    responses={
        200: inline_serializer(
            name="HistoricalDataResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "symbol": drf_serializers.CharField(required=False),
                "data": drf_serializers.ListField(
                    child=drf_serializers.DictField(), required=False
                ),
                "error": drf_serializers.CharField(required=False),
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def historical_data(request):
    """获取历史数据（支持不同时间间隔的K线数据）"""
    try:
        symbol = request.query_params.get("symbol")
        days = int(request.query_params.get("days", 30))
        interval = request.query_params.get("interval", "1d")  # 默认日线
        period = request.query_params.get("period", None)  # 可选：直接指定yfinance period

        if not symbol:
            return Response(
                {"success": False, "error": "Symbol parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = CSI300Company.objects.get(ticker=symbol)
            company_name = company.name

            # 从数据库获取价格信息（与 intraday_data 保持一致）
            company_data = {
                "previous_close": company.previous_close,
                "open": company.price_local_currency,
                "price_52w_high": company.price_52w_high,
                "price_52w_low": company.price_52w_low,
                "last_trade_date": company.last_trade_date,
            }
        except CSI300Company.DoesNotExist:
            return Response(
                {"success": False, "error": f"Symbol {symbol} not found in CSI300 database"},
                status=status.HTTP_404_NOT_FOUND,
            )

        logger.info(
            f"Historical data request: symbol={symbol}, days={days}, interval={interval}, period={period}"
        )
        df = VWAPCalculationService.get_historical_data(symbol, days, interval, period)
        result = VWAPCalculationService.format_historical_response(
            df, symbol, company_name, company_data
        )

        return Response(result)

    except Exception as e:
        logger.exception("Error fetching historical data for {symbol}")
        return Response(
            {"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    responses={
        200: inline_serializer(
            name="FundFlowPageResponse",
            fields={
                "message": drf_serializers.CharField(),
            },
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def fund_flow_page(request):
    """Fund Flow页面 - 重定向到现有的HTML页面"""
    from pathlib import Path

    from django.http import FileResponse

    html_path = Path(__file__).resolve().parents[3] / "csi300-app" / "fund-flow.html"

    return FileResponse(html_path.open("rb"), content_type="text/html")


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="symbol",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Stock ticker symbol",
            required=True,
        ),
        OpenApiParameter(
            name="type",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Chart type: intraday, cmf, obv",
            required=False,
        ),
    ],
    responses={
        200: inline_serializer(
            name="LightweightChartResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "symbol": drf_serializers.CharField(required=False),
                "company_name": drf_serializers.CharField(required=False),
                "chart_type": drf_serializers.CharField(required=False),
                "data": drf_serializers.ListField(
                    child=drf_serializers.DictField(), required=False
                ),
                "message": drf_serializers.CharField(required=False),
                "error": drf_serializers.CharField(required=False),
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def lightweight_chart(request):
    """
    生成TradingView Lightweight Charts图表
    使用lightweight-charts-python库（仿照Databento示例）
    """
    try:
        symbol = request.query_params.get("symbol")
        chart_type = request.query_params.get("type", "intraday")  # intraday, cmf, obv

        if not symbol:
            return Response(
                {"success": False, "error": "Symbol parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = CSI300Company.objects.get(ticker=symbol)
            company_name = company.name
        except CSI300Company.DoesNotExist:
            return Response(
                {"success": False, "error": f"Symbol {symbol} not found in CSI300 database"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 尝试导入lightweight-charts，如果未安装则返回错误信息
        try:
            from lightweight_charts import Chart
        except ImportError:
            return Response(
                {
                    "success": False,
                    "error": "lightweight-charts-python not installed. Run: pip install lightweight-charts",
                    "install_command": "pip install lightweight-charts",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 根据图表类型获取数据
        if chart_type == "intraday":
            df = VWAPCalculationService.get_intraday_data(symbol, "CN")
        else:
            df = VWAPCalculationService.get_historical_data(symbol, 30)

        if df is None or df.empty:
            return Response(
                {"success": False, "error": f"No data available for {symbol}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 创建图表（遵循Databento示例中的11行代码模式）
        chart = Chart(toolbox=True)

        # 设置基础数据
        chart.set(df)

        # 根据图表类型添加指标
        if chart_type == "intraday" and "vwap" in df.columns:
            # 计算VWAP（如果还没有）
            if "pvt" not in df.columns:
                df["pvt"] = df["close"] * df["volume"]
                df["vwap"] = df["pvt"].cumsum() / df["volume"].cumsum()

            # 创建VWAP线（遵循Databento示例）
            vwap_df = pd.DataFrame({"vwap": df["vwap"]}, index=df.index)
            line = chart.create_line(name="VWAP", color="#2563eb", width=2)
            line.set(vwap_df)

        # lightweight-charts-python不直接支持HTML导出
        # 我们需要返回一个简单的消息，提示前端直接使用JSON数据

        # 返回数据让前端使用JavaScript的lightweight-charts库渲染
        chart_data = {
            "success": True,
            "symbol": symbol,
            "company_name": company_name,
            "chart_type": chart_type,
            "data": df.to_dict("records"),
            "message": "Chart data ready. Use TradingView Lightweight Charts JavaScript library on frontend.",
        }

        return Response(chart_data)

    except Exception as e:
        logger.exception("Error generating lightweight chart for {symbol}")
        import traceback

        logger.exception("Exception occurred")
        return Response(
            {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc() if request.user.is_staff else None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="limit",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Number of results",
            required=False,
        ),
        OpenApiParameter(
            name="direction",
            type=str,
            location=OpenApiParameter.QUERY,
            description="buy or sell",
            required=False,
        ),
    ],
    responses={
        200: inline_serializer(
            name="TopPicksWithSparklinesResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "picks": drf_serializers.ListField(
                    child=drf_serializers.DictField(), required=False
                ),
                "calculation_date": drf_serializers.CharField(required=False),
                "direction": drf_serializers.CharField(required=False),
                "count": drf_serializers.IntegerField(required=False),
                "error": drf_serializers.CharField(required=False),
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def top_picks_with_sparklines(request):
    """
    Optimized endpoint: returns top picks WITH sparkline data in one request.
    Reduces frontend API calls from 10+ to 1.
    """
    try:
        limit = int(request.query_params.get("limit", 5))
        direction = (request.query_params.get("direction") or "buy").lower()

        # Get latest calculation date
        latest_date = StockScore.objects.aggregate(latest=Max("calculation_date"))["latest"]

        if not latest_date:
            return Response({"success": False, "error": "No score data available"})

        # Get scores
        scores_qs = StockScore.objects.filter(calculation_date=latest_date)
        if direction == "sell":
            scores_qs = scores_qs.order_by("total_score")[:limit]
        else:
            scores_qs = scores_qs.order_by("-total_score")[:limit]

        picks = []
        symbols = [score.ticker for score in scores_qs]

        # Batch fetch historical data for all symbols
        sparklines = {}
        for symbol in symbols:
            try:
                hist_data = VWAPCalculationService.get_historical_data(
                    symbol=symbol, days=25, interval="1d", period=None
                )

                if hist_data is None or hist_data.empty:
                    sparklines[symbol] = []
                    continue

                recent_rows = hist_data.tail(25)
                sparkline_points = []

                for _, row in recent_rows.iterrows():
                    close_value = row.get("Close")
                    if close_value is None or pd.isna(close_value):
                        continue

                    date_value = (
                        row.get("Date_Str")
                        or row.get("Timestamp")
                        or row.get("Date")
                        or row.get("date")
                    )

                    if isinstance(date_value, (int, float)):
                        date_value = pd.to_datetime(date_value, errors="coerce")

                    if hasattr(date_value, "strftime"):
                        date_str = date_value.strftime("%Y-%m-%d")
                    elif isinstance(date_value, str):
                        date_str = date_value.split(" ")[0]
                    else:
                        continue

                    try:
                        sparkline_points.append({"date": date_str, "close": float(close_value)})
                    except (TypeError, ValueError):
                        continue

                sparklines[symbol] = sparkline_points if len(sparkline_points) >= 2 else []
            except Exception as e:
                logger.warning(f"Failed to get sparkline for {symbol}: {e}")
                sparklines[symbol] = []

        # Build response
        for score in scores_qs:
            pick = {
                "symbol": score.ticker,
                "name": score.company_name,
                "total_score": float(score.total_score),
                "last_close": float(score.last_close) if score.last_close else None,
                "sparkline": sparklines.get(score.ticker, []),
                "last_trading_date": score.last_trading_date.isoformat()
                if score.last_trading_date
                else None,
            }
            picks.append(pick)

        return Response(
            {
                "success": True,
                "picks": picks,
                "calculation_date": latest_date.isoformat(),
                "direction": direction,
                "count": len(picks),
            }
        )

    except Exception as e:
        logger.exception("Error in top_picks_with_sparklines")
        return Response(
            {"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="limit",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Number of results",
            required=False,
        ),
        OpenApiParameter(
            name="direction",
            type=str,
            location=OpenApiParameter.QUERY,
            description="buy or sell",
            required=False,
        ),
    ],
    responses={
        200: inline_serializer(
            name="TopPicksResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "calculation_date": drf_serializers.CharField(required=False, allow_null=True),
                "picks": drf_serializers.ListField(child=drf_serializers.DictField()),
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def top_picks(request):
    """Return today's top scoring stocks to power the dashboard cards."""
    try:
        limit = int(request.query_params.get("limit", 5))
        limit = max(1, min(limit, 12))
    except (TypeError, ValueError):
        limit = 5

    latest_date = StockScore.objects.aggregate(latest=Max("calculation_date"))["latest"]
    if not latest_date:
        return Response({"success": True, "calculation_date": None, "picks": []})

    direction = (request.query_params.get("direction") or "buy").lower()
    scores_qs = StockScore.objects.filter(calculation_date=latest_date)
    if direction == "sell":
        scores_qs = scores_qs.order_by("total_score")
    else:
        scores_qs = scores_qs.order_by("-total_score")

    picks = []
    for score in scores_qs[:limit]:
        sparkline = []
        try:
            df = VWAPCalculationService.get_historical_data(score.ticker, 90, "1d")
            if df is not None and not df.empty:
                df_tail = df.tail(25)
                sparkline = []
                for _, row in df_tail.iterrows():
                    close_value = row.get("Close") if hasattr(row, "get") else row["Close"]
                    if close_value is None:
                        continue
                    date_value = None
                    if hasattr(row, "get"):
                        date_value = row.get("Date") or row.get("date") or row.get("Date_Str")
                    else:
                        date_value = row["Date"]
                    if hasattr(date_value, "strftime"):
                        date_value = date_value.strftime("%Y-%m-%d")
                    sparkline.append({"date": date_value, "close": float(close_value)})
        except Exception as exc:  # pragma: no cover - best-effort sparkline
            logger.debug("Sparkline fetch failed for %s: %s", score.ticker, exc)

        picks.append(
            {
                "symbol": score.ticker,
                "name": score.company_name,
                "total_score": float(score.total_score) if score.total_score is not None else 0.0,
                "recommended_action": score.recommended_action or "",
                "last_close": float(score.last_close) if score.last_close is not None else None,
                "signal_date": score.signal_date.isoformat() if score.signal_date else None,
                "sparkline": sparkline,
            }
        )

    return Response(
        {
            "success": True,
            "calculation_date": latest_date.isoformat(),
            "picks": picks,
        }
    )


@extend_schema(
    request=inline_serializer(
        name="GenerateStockScoreRequest",
        fields={
            "symbol": drf_serializers.CharField(required=True),
        },
    ),
    responses={
        200: inline_serializer(
            name="GenerateStockScoreResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "summary": drf_serializers.DictField(required=False),
                "logs": drf_serializers.ListField(
                    child=drf_serializers.CharField(), required=False
                ),
                "score": drf_serializers.DictField(required=False),
                "company": drf_serializers.DictField(required=False),
                "error": drf_serializers.CharField(required=False),
            },
        )
    },
)
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def generate_stock_score(request):
    """Trigger a lightweight scoring run for a single ticker."""
    symbol = (request.data.get("symbol") or request.POST.get("symbol") or "").strip().upper()
    if not symbol:
        return Response(
            {"success": False, "error": "Symbol is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        company = CSI300Company.objects.get(ticker=symbol)
    except CSI300Company.DoesNotExist:
        return Response(
            {"success": False, "error": f"Symbol {symbol} not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    logs = []
    summary = None
    if score_calculator is not None:
        buffer = io.StringIO()
        try:
            with redirect_stdout(buffer):
                summary = score_calculator.calculate_all_scores(
                    batch_size=1,
                    limit=1,
                    fetch_workers=1,
                    symbols=[symbol],
                )
        except Exception as exc:
            logger.exception("On-demand scoring failed for %s", symbol)
            return Response(
                {"success": False, "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        logs = [line for line in buffer.getvalue().splitlines() if line.strip()]
    else:
        try:
            summary, logs = _run_scoring_subprocess(symbol)
        except Exception as exc:
            logger.exception("Subprocess scoring failed for %s", symbol)
            return Response(
                {"success": False, "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    latest_score = VWAPCalculationService.get_latest_stock_score(symbol)

    return Response(
        {
            "success": True,
            "summary": summary or {},
            "logs": logs[-60:],
            "score": latest_score,
            "company": {
                "symbol": symbol,
                "name": company.name,
            },
        }
    )


@extend_schema(
    request=None,  # No request body required
    responses={
        200: inline_serializer(
            name="GenerateAllScoresResponse",
            fields={
                "success": drf_serializers.BooleanField(),
                "message": drf_serializers.CharField(required=False),
                "status": drf_serializers.CharField(required=False),
                "estimated_time": drf_serializers.CharField(required=False),
                "error": drf_serializers.CharField(required=False),
            },
        )
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def generate_all_scores(request):
    """Trigger scoring calculation for all stocks."""
    try:
        script_path = PROJECT_ROOT / "scripts" / "active" / "daily_score_calculator_db.py"
        if not script_path.exists():
            return Response(
                {"success": False, "error": f"Scoring script not found at {script_path}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Run the script with optimized parameters
        cmd = [
            sys.executable,
            str(script_path),
            "--batch-size",
            "50",
            "--fetch-workers",
            "10",
        ]

        logger.info(f"Starting score generation: {' '.join(cmd)}")

        # Run asynchronously in background (non-blocking)
        import threading

        def run_script():
            try:
                result = subprocess.run(
                    cmd,
                    check=False,
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 分钟超时
                )

                if result.returncode == 0:
                    logger.info("✅ Score generation completed successfully")
                    logger.info(f"Output: {result.stdout[-500:]}")  # 最后 500 字符
                else:
                    logger.error(f"❌ Score generation failed with code {result.returncode}")
                    logger.error(f"Error: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.exception("❌ Score generation timeout after 10 minutes")
            except Exception:
                logger.exception("❌ Error running score generation")

                logger.exception("Exception occurred")

        thread = threading.Thread(target=run_script, daemon=True)
        thread.start()

        return Response(
            {
                "success": True,
                "message": "Score generation started in background. Check server logs for progress.",
                "status": "processing",
                "estimated_time": "3-5 minutes for 250 stocks",
            }
        )

    except Exception as exc:
        logger.exception("Error triggering score generation")

        logger.exception("Exception occurred")
        return Response(
            {"success": False, "error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
