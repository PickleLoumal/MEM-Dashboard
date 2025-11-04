from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
import pandas as pd

from csi300.models import CSI300Company
from .services import VWAPCalculationService

logger = logging.getLogger(__name__)

@api_view(['GET'])
def stock_list(request):
    """获取股票列表 - 从CSI300 Company表读取"""
    try:
        # 从CSI300Company表读取所有有ticker的公司
        companies = CSI300Company.objects.filter(ticker__isnull=False).exclude(ticker='')
        
        stock_list = []
        for company in companies:
            stock_list.append({
                'symbol': company.ticker,
                'name': company.name,
                'exchange': 'SSE/SZSE',  # 上交所/深交所
                'sector': company.im_sector or '',
                'industry': company.industry or ''
            })
        
        return Response({
            'success': True,
            'count': len(stock_list),
            'stocks': stock_list
        })
    
    except Exception as e:
        logger.error(f"Error fetching stock list: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def intraday_data(request):
    """获取分时数据（1分钟K线）"""
    try:
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response({
                'success': False,
                'error': 'Symbol parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            company = CSI300Company.objects.get(ticker=symbol)
            company_name = company.name
            market = 'CN'  # CSI300都是中国市场
            
            # 从数据库获取价格信息
            company_data = {
                'previous_close': company.previous_close,
                'open': company.price_local_currency,
                'price_52w_high': company.price_52w_high,
                'price_52w_low': company.price_52w_low,
                'last_trade_date': company.last_trade_date
            }
        except CSI300Company.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Symbol {symbol} not found in CSI300 database'
            }, status=status.HTTP_404_NOT_FOUND)
        
        df = VWAPCalculationService.get_intraday_data(symbol, market)
        result = VWAPCalculationService.format_intraday_response(df, symbol, company_name, company_data)
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Error fetching intraday data for {symbol}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def historical_data(request):
    """获取历史数据（支持不同时间间隔的K线数据）"""
    try:
        symbol = request.query_params.get('symbol')
        days = int(request.query_params.get('days', 30))
        interval = request.query_params.get('interval', '1d')  # 默认日线
        period = request.query_params.get('period', None)  # 可选：直接指定yfinance period
        
        if not symbol:
            return Response({
                'success': False,
                'error': 'Symbol parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            company = CSI300Company.objects.get(ticker=symbol)
            company_name = company.name
            
            # 从数据库获取价格信息（与 intraday_data 保持一致）
            company_data = {
                'previous_close': company.previous_close,
                'open': company.price_local_currency,
                'price_52w_high': company.price_52w_high,
                'price_52w_low': company.price_52w_low,
                'last_trade_date': company.last_trade_date
            }
        except CSI300Company.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Symbol {symbol} not found in CSI300 database'
            }, status=status.HTTP_404_NOT_FOUND)
        
        logger.info(f"Historical data request: symbol={symbol}, days={days}, interval={interval}, period={period}")
        df = VWAPCalculationService.get_historical_data(symbol, days, interval, period)
        result = VWAPCalculationService.format_historical_response(df, symbol, company_name, company_data)
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def fund_flow_page(request):
    """Fund Flow页面 - 重定向到现有的HTML页面"""
    from django.http import FileResponse
    import os
    
    html_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        'csi300-app',
        'fund-flow.html'
    )
    
    return FileResponse(open(html_path, 'rb'), content_type='text/html')


@api_view(['GET'])
def lightweight_chart(request):
    """
    生成TradingView Lightweight Charts图表
    使用lightweight-charts-python库（仿照Databento示例）
    """
    try:
        symbol = request.query_params.get('symbol')
        chart_type = request.query_params.get('type', 'intraday')  # intraday, cmf, obv
        
        if not symbol:
            return Response({
                'success': False,
                'error': 'Symbol parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            company = CSI300Company.objects.get(ticker=symbol)
            company_name = company.name
        except CSI300Company.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Symbol {symbol} not found in CSI300 database'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 尝试导入lightweight-charts，如果未安装则返回错误信息
        try:
            from lightweight_charts import Chart
        except ImportError:
            return Response({
                'success': False,
                'error': 'lightweight-charts-python not installed. Run: pip install lightweight-charts',
                'install_command': 'pip install lightweight-charts'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 根据图表类型获取数据
        if chart_type == 'intraday':
            df = VWAPCalculationService.get_intraday_data(symbol, 'CN')
        else:
            df = VWAPCalculationService.get_historical_data(symbol, 30)
        
        if df is None or df.empty:
            return Response({
                'success': False,
                'error': f'No data available for {symbol}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 创建图表（遵循Databento示例中的11行代码模式）
        chart = Chart(toolbox=True)
        
        # 设置基础数据
        chart.set(df)
        
        # 根据图表类型添加指标
        if chart_type == 'intraday' and 'vwap' in df.columns:
            # 计算VWAP（如果还没有）
            if 'pvt' not in df.columns:
                df['pvt'] = df['close'] * df['volume']
                df['vwap'] = df['pvt'].cumsum() / df['volume'].cumsum()
            
            # 创建VWAP线（遵循Databento示例）
            vwap_df = pd.DataFrame({'vwap': df['vwap']}, index=df.index)
            line = chart.create_line(name='VWAP', color='#2563eb', width=2)
            line.set(vwap_df)
        
        # lightweight-charts-python不直接支持HTML导出
        # 我们需要返回一个简单的消息，提示前端直接使用JSON数据
        
        # 返回数据让前端使用JavaScript的lightweight-charts库渲染
        chart_data = {
            'success': True,
            'symbol': symbol,
            'company_name': company_name,
            'chart_type': chart_type,
            'data': df.to_dict('records'),
            'message': 'Chart data ready. Use TradingView Lightweight Charts JavaScript library on frontend.'
        }
        
        return Response(chart_data)
    
    except Exception as e:
        logger.error(f"Error generating lightweight chart for {symbol}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc() if request.user.is_staff else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
