"""
Django Management Command - 获取日本FRED数据
用于测试和调试日本经济指标数据获取功能
"""

import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from fred_jp.config_manager import JapanFredConfigManager
from fred_jp.data_fetcher import JapanFredDataFetcher


class Command(BaseCommand):
    help = "获取日本FRED经济指标数据"

    def add_arguments(self, parser):
        parser.add_argument("--indicator", type=str, help="指标名称 (如: cpi, gdp, unemployment)")
        parser.add_argument(
            "--category", type=str, help="指标类别 (如: inflation, economic_growth)"
        )
        parser.add_argument("--all", action="store_true", help="获取所有指标数据")
        parser.add_argument("--summary", action="store_true", help="获取最新数据摘要")
        parser.add_argument("--limit", type=int, default=12, help="限制记录数 (默认: 12)")
        parser.add_argument("--test-connection", action="store_true", help="测试API连接")
        parser.add_argument("--output-file", type=str, help="输出到JSON文件")
        parser.add_argument("--verbose", action="store_true", help="详细输出")

    def handle(self, *args, **options):
        """处理命令执行"""
        try:
            # 设置日志级别
            if options["verbose"]:
                import logging

                logging.getLogger().setLevel(logging.INFO)

            # 检查API密钥
            if not self._check_api_key():
                return

            # 初始化数据获取器
            with JapanFredDataFetcher() as fetcher:
                # 测试连接
                if options["test_connection"]:
                    self._test_connection(fetcher)
                    return

                # 获取数据摘要
                if options["summary"]:
                    self._get_summary(fetcher, options)
                    return

                # 获取所有指标
                if options["all"]:
                    self._get_all_indicators(fetcher, options)
                    return

                # 按类别获取
                if options["category"]:
                    self._get_category_data(fetcher, options)
                    return

                # 获取单个指标
                if options["indicator"]:
                    self._get_indicator_data(fetcher, options)
                    return

                # 显示可用选项
                self._show_available_options()

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n操作被用户中断"))
        except Exception as e:
            raise CommandError(f"命令执行失败: {e}") from e

    def _check_api_key(self) -> bool:
        """检查API密钥配置"""
        api_key = os.getenv("FRED_API_KEY") or getattr(settings, "FRED_API_KEY", None)

        if not api_key:
            self.stdout.write(
                self.style.ERROR(
                    "错误: 未配置FRED API密钥\n请设置环境变量FRED_API_KEY或在Django settings中配置"
                )
            )
            return False

        self.stdout.write(self.style.SUCCESS(f"API密钥已配置: {api_key[:8]}..."))
        return True

    def _test_connection(self, fetcher):
        """测试API连接"""
        self.stdout.write("正在测试日本FRED API连接...")

        result = fetcher.validate_connection()

        if result.get("connection_valid"):
            self.stdout.write(self.style.SUCCESS("✓ API连接测试成功"))
            self.stdout.write(f"配置信息: {result.get('country_config', {}).get('country')}")
        else:
            self.stdout.write(self.style.ERROR(f"✗ API连接测试失败: {result.get('error')}"))

    def _get_summary(self, fetcher, options):
        """获取数据摘要"""
        self.stdout.write("正在获取日本经济指标最新数据摘要...")

        summary = fetcher.get_latest_data_summary()

        self.stdout.write(
            self.style.SUCCESS(f"✓ 摘要获取完成 - {summary.get('indicators_count', 0)}个指标")
        )

        # 显示摘要
        for indicator, data in summary.get("data", {}).items():
            if "error" in data:
                self.stdout.write(self.style.WARNING(f"  {indicator}: {data['error']}"))
            else:
                self.stdout.write(
                    f"  {indicator}: {data.get('value')} {data.get('unit', '')} "
                    f"({data.get('date')})"
                )

        self._save_output(summary, options)

    def _get_all_indicators(self, fetcher, options):
        """获取所有指标数据"""
        config_manager = JapanFredConfigManager()
        indicators = config_manager.get_all_indicators()

        self.stdout.write(f"正在获取所有日本指标数据 ({len(indicators)}个)...")

        result = fetcher.get_multiple_indicators(indicator_names=indicators, limit=options["limit"])

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ 批量获取完成 - 成功: {result.get('success_count', 0)}, "
                f"失败: {result.get('failure_count', 0)}"
            )
        )

        self._save_output(result, options)

    def _get_category_data(self, fetcher, options):
        """获取类别数据"""
        category = options["category"]

        self.stdout.write(f"正在获取类别 [{category}] 的指标数据...")

        result = fetcher.get_category_indicators(category=category, limit=options["limit"])

        if result.get("success"):
            self.stdout.write(
                self.style.SUCCESS(f"✓ 类别数据获取完成 - 成功: {result.get('success_count', 0)}")
            )
        else:
            self.stdout.write(self.style.ERROR(f"✗ 类别数据获取失败: {result.get('error')}"))
            return

        self._save_output(result, options)

    def _get_indicator_data(self, fetcher, options):
        """获取单个指标数据"""
        indicator = options["indicator"]

        self.stdout.write(f"正在获取指标 [{indicator}] 数据...")

        result = fetcher.get_indicator_data(indicator_name=indicator, limit=options["limit"])

        if result.get("success"):
            self.stdout.write(
                self.style.SUCCESS(f"✓ 指标数据获取完成 - {result.get('data_count', 0)}条记录")
            )

            # 显示基本统计
            stats = result.get("statistics", {})
            if stats:
                self.stdout.write(f"  最新值: {stats.get('latest_value')}")
                self.stdout.write(f"  最新日期: {stats.get('latest_date')}")
                if "yoy_change_percent" in stats:
                    self.stdout.write(f"  年同比: {stats['yoy_change_percent']}%")
        else:
            self.stdout.write(self.style.ERROR(f"✗ 指标数据获取失败: {result.get('error')}"))
            return

        self._save_output(result, options)

    def _show_available_options(self):
        """显示可用选项"""
        config_manager = JapanFredConfigManager()

        self.stdout.write(self.style.HTTP_INFO("可用的日本经济指标:"))
        for indicator in config_manager.get_all_indicators():
            config = config_manager.get_indicator_config(indicator)
            if config:
                self.stdout.write(f"  {indicator}: {config['description']}")
            else:
                self.stdout.write(f"  {indicator}: 配置未找到")

        self.stdout.write(self.style.HTTP_INFO("\n可用的指标类别:"))
        for category in config_manager.get_categories():
            indicators = config_manager.get_indicators_by_category(category)
            self.stdout.write(f"  {category}: {len(indicators)}个指标")

        self.stdout.write(self.style.HTTP_INFO("\n使用示例:"))
        self.stdout.write("  python manage.py fetch_japan_data --indicator cpi")
        self.stdout.write("  python manage.py fetch_japan_data --category inflation")
        self.stdout.write("  python manage.py fetch_japan_data --summary")
        self.stdout.write("  python manage.py fetch_japan_data --test-connection")

    def _save_output(self, data, options):
        """保存输出到文件"""
        if options.get("output_file"):
            try:
                with Path(options["output_file"]).open("w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

                self.stdout.write(self.style.SUCCESS(f"✓ 数据已保存到: {options['output_file']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ 文件保存失败: {e}"))
