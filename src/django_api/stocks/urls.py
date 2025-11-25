from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    # Stock list endpoint - 读取数据库中的股票列表
    path('list/', views.stock_list, name='stock-list'),
    
    # Intraday data endpoint - 分时数据（1分钟K线）
    path('intraday/', views.intraday_data, name='intraday-data'),
    
    # Historical data endpoint - 历史数据（日K线，带技术指标）
    path('historical/', views.historical_data, name='historical-data'),
    path('top-picks/', views.top_picks, name='top-picks'),
    path('top-picks-fast/', views.top_picks_with_sparklines, name='top-picks-fast'),
    path('score/generate/', views.generate_stock_score, name='generate-score'),
    path('score/generate-all/', views.generate_all_scores, name='generate-all-scores'),
    
    # Fund flow page - 资金流向页面
    path('fund-flow/', views.fund_flow_page, name='fund-flow-page'),
    
    # Lightweight Charts endpoint - TradingView风格图表生成
    path('chart/lightweight/', views.lightweight_chart, name='lightweight-chart'),
]
