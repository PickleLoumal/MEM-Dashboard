"""
US FRED Application Configuration
美国FRED经济指标Django应用配置
"""

from django.apps import AppConfig


class FredUsConfig(AppConfig):
    """美国FRED应用配置"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "fred_us"
    verbose_name = "US FRED Economic Indicators"

    def ready(self):
        """应用准备就绪时的初始化"""
        # 这里可以添加信号处理器或其他初始化代码
