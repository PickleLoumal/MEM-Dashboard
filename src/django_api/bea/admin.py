from django.contrib import admin

from .models import BeaIndicator, BeaIndicatorConfig, BeaSeriesInfo


@admin.register(BeaSeriesInfo)
class BeaSeriesInfoAdmin(admin.ModelAdmin):
    """BEA 系列信息管理"""

    list_display = (
        "series_id",
        "title",
        "category",
        "frequency",
        "units",
        "table_name",
        "last_updated",
    )
    list_filter = ("category", "frequency", "last_updated")
    search_fields = ("series_id", "title", "line_description")
    readonly_fields = ("last_updated",)

    fieldsets = (
        ("基本信息", {"fields": ("series_id", "title", "category", "units")}),
        (
            "技术信息",
            {
                "fields": (
                    "frequency",
                    "table_name",
                    "line_number",
                    "line_description",
                    "dataset_name",
                )
            },
        ),
        ("其他", {"fields": ("notes", "last_updated"), "classes": ("collapse",)}),
    )


@admin.register(BeaIndicator)
class BeaIndicatorAdmin(admin.ModelAdmin):
    """BEA 指标数据管理"""

    list_display = ("series_id", "indicator_name", "time_period", "value", "date", "indicator_type")
    list_filter = ("indicator_type", "date", "created_at", "frequency")
    search_fields = ("series_id", "indicator_name", "time_period")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "date"

    fieldsets = (
        ("指标信息", {"fields": ("series_id", "indicator_name", "indicator_type")}),
        ("数据信息", {"fields": ("time_period", "value", "date", "unit", "frequency")}),
        (
            "技术信息",
            {
                "fields": ("table_name", "line_number", "dataset_name", "source", "metadata"),
                "classes": ("collapse",),
            },
        ),
        ("时间戳", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    # 添加自定义过滤器
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(BeaIndicatorConfig)
class BeaIndicatorConfigAdmin(admin.ModelAdmin):
    """BEA 指标配置管理"""

    list_display = (
        "series_id",
        "name",
        "category",
        "priority",
        "is_active",
        "auto_fetch",
        "updated_at",
    )
    list_filter = ("category", "is_active", "auto_fetch", "frequency")
    search_fields = ("series_id", "name", "description")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本配置", {"fields": ("series_id", "name", "description", "category", "api_endpoint")}),
        (
            "BEA API 配置",
            {
                "fields": (
                    "table_name",
                    "line_description",
                    "line_number",
                    "units",
                    "frequency",
                    "years",
                    "dataset_name",
                )
            },
        ),
        ("系统配置", {"fields": ("priority", "is_active", "auto_fetch", "fallback_value")}),
        (
            "元数据",
            {"fields": ("created_by", "updated_by", "additional_config"), "classes": ("collapse",)},
        ),
        ("时间戳", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# 自定义 admin 站点标题
admin.site.site_header = "MEM Dashboard Administration"
admin.site.site_title = "MEM Dashboard"
admin.site.index_title = "Economic Indicator Data Management"
