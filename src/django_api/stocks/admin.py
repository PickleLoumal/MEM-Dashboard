from django.contrib import admin

from .models import ScoreCalculationLog, StockScore


@admin.register(StockScore)
class StockScoreAdmin(admin.ModelAdmin):
    list_display = ('calculation_date', 'ticker', 'total_score', 'recommended_action', 'last_trading_date')
    list_filter = ('calculation_date', 'recommended_action')
    search_fields = ('ticker', 'company_name')
    ordering = ('-calculation_date', 'ticker')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('buy_score', 'buy_reasons', 'sell_score', 'sell_reasons')


@admin.register(ScoreCalculationLog)
class ScoreCalculationLogAdmin(admin.ModelAdmin):
    list_display = ('calculation_date', 'status', 'total_stocks', 'successful_stocks', 'failed_stocks', 'start_time', 'end_time')
    list_filter = ('status',)
    search_fields = ('calculation_date',)
    ordering = ('-calculation_date',)
