from django.contrib import admin
from .models import FredJpIndicator, FredJpSeriesInfo


@admin.register(FredJpSeriesInfo)
class FredJpSeriesInfoAdmin(admin.ModelAdmin):
    """日本FRED 系列信息管理"""
    list_display = ('series_id', 'title', 'category', 'units', 'frequency', 'last_updated')
    list_filter = ('category', 'frequency', 'seasonal_adjustment', 'last_updated')
    search_fields = ('series_id', 'title', 'notes')
    readonly_fields = ('last_updated',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('series_id', 'title', 'category', 'units')
        }),
        ('技术信息', {
            'fields': ('frequency', 'seasonal_adjustment', 'notes')
        }),
        ('时间戳', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )


@admin.register(FredJpIndicator)
class FredJpIndicatorAdmin(admin.ModelAdmin):
    """日本FRED 指标数据管理"""
    list_display = ('series_id', 'indicator_name', 'value', 'date', 'unit', 'frequency', 'indicator_type')
    list_filter = ('indicator_type', 'frequency', 'unit', 'date', 'created_at')
    search_fields = ('series_id', 'indicator_name', 'indicator_type')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('指标信息', {
            'fields': ('series_id', 'indicator_name', 'indicator_type')
        }),
        ('数据', {
            'fields': ('date', 'value', 'unit', 'frequency')
        }),
        ('元数据', {
            'fields': ('source', 'metadata')
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # 优化性能
    list_per_page = 50
    list_max_show_all = 200
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related()
