from django.apps import AppConfig


class StocksConfig(AppConfig):
    """股票应用配置"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "stocks"
    verbose_name = "CSI 300 Stock Scores"

    def ready(self):
        """应用启动时执行"""
        # 这里可以添加初始化逻辑
