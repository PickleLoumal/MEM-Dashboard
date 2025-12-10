"""
Django Admin Configuration for US FRED Economic Indicators
美国FRED经济指标Django管理界面配置
"""

from django.contrib import admin

from .models import FredUsIndicator, FredUsIndicatorConfig, FredUsSeriesInfo


@admin.register(FredUsSeriesInfo)
class FredUsSeriesInfoAdmin(admin.ModelAdmin):
    """美国FRED系列信息管理界面"""

    list_display = ("series_id", "title", "category", "units", "frequency", "last_updated")
    list_filter = ("category", "frequency", "units")
    search_fields = ("series_id", "title", "category")
    readonly_fields = ("series_id", "last_updated")
    ordering = ("series_id",)

    fieldsets = (
        ("基本信息", {"fields": ("series_id", "title", "category")}),
        (
            "技术信息",
            {"fields": ("units", "frequency", "seasonal_adjustment"), "classes": ("collapse",)},
        ),
        ("说明", {"fields": ("notes", "last_updated"), "classes": ("collapse",)}),
    )


@admin.register(FredUsIndicator)
class FredUsIndicatorAdmin(admin.ModelAdmin):
    """美国FRED指标数据管理界面"""

    list_display = (
        "series_id",
        "indicator_name",
        "indicator_type",
        "date",
        "value",
        "source",
        "updated_at",
    )
    list_filter = ("indicator_type", "source", "frequency", "date")
    search_fields = ("series_id", "indicator_name", "indicator_type")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"
    ordering = ("-date", "series_id")
    list_per_page = 50

    fieldsets = (
        ("指标信息", {"fields": ("series_id", "indicator_name", "indicator_type")}),
        ("数据信息", {"fields": ("date", "value", "unit", "frequency")}),
        ("元数据", {"fields": ("source", "metadata"), "classes": ("collapse",)}),
        ("时间戳", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related()


@admin.register(FredUsIndicatorConfig)
class FredUsIndicatorConfigAdmin(admin.ModelAdmin):
    """美国FRED指标配置管理界面"""

    list_display = (
        "series_id",
        "name",
        "category",
        "auto_fetch",
        "fetch_frequency",
        "priority",
        "is_active",
        "fetch_status",
        "last_fetch_time",
    )
    list_filter = (
        "auto_fetch",
        "fetch_frequency",
        "priority",
        "is_active",
        "fetch_status",
        "category",
    )
    search_fields = ("series_id", "name", "category", "description")
    readonly_fields = ("last_fetch_time", "created_at", "updated_at")
    ordering = ("priority", "series_id")
    list_per_page = 50

    fieldsets = (
        ("基本信息", {"fields": ("series_id", "name", "category", "description")}),
        ("自动抓取配置", {"fields": ("auto_fetch", "fetch_frequency", "priority", "is_active")}),
        ("抓取状态", {"fields": ("fetch_status", "last_fetch_time"), "classes": ("collapse",)}),
        ("高级配置", {"fields": ("additional_config",), "classes": ("collapse",)}),
        ("时间戳", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["enable_auto_fetch", "disable_auto_fetch", "reset_fetch_status"]

    def enable_auto_fetch(self, request, queryset):
        """启用自动抓取"""
        updated = queryset.update(auto_fetch=True, is_active=True)
        self.message_user(request, f"{updated} 个指标已启用自动抓取")

    enable_auto_fetch.short_description = "启用选中指标的自动抓取"

    def disable_auto_fetch(self, request, queryset):
        """禁用自动抓取"""
        updated = queryset.update(auto_fetch=False)
        self.message_user(request, f"{updated} 个指标已禁用自动抓取")

    disable_auto_fetch.short_description = "禁用选中指标的自动抓取"

    def reset_fetch_status(self, request, queryset):
        """重置抓取状态"""
        updated = queryset.update(fetch_status="pending", last_fetch_time=None)
        self.message_user(request, f"{updated} 个指标的抓取状态已重置")

    reset_fetch_status.short_description = "重置选中指标的抓取状态"
