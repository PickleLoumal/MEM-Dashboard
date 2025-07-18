from django.contrib import admin
from .models import FredIndicator, FredSeriesInfo


@admin.register(FredSeriesInfo)
class FredSeriesInfoAdmin(admin.ModelAdmin):
    """FRED 系列信息管理"""
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


@admin.register(FredIndicator)
class FredIndicatorAdmin(admin.ModelAdmin):
    """FRED 指标数据管理"""
    list_display = ('series_id', 'indicator_name', 'value', 'date', 'unit', 'frequency', 'indicator_type')
    list_filter = ('frequency', 'indicator_type', 'date', 'created_at')
    search_fields = ('series_id', 'indicator_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('指标信息', {
            'fields': ('series_id', 'indicator_name', 'indicator_type')
        }),
        ('数据信息', {
            'fields': ('value', 'date', 'unit', 'frequency')
        }),
        ('技术信息', {
            'fields': ('source', 'metadata'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
