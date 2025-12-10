"""
Django管理命令: 只对前端component cards中的指标进行分类
基于实际前端使用情况对指标进行分类
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import models

from fred_us.models import FredUsSeriesInfo


class Command(BaseCommand):
    help = "只对前端component cards中的指标进行分类"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="只显示分类计划，不实际更新数据库"
        )
        parser.add_argument("--clear-unused", action="store_true", help="清除不在前端的指标分类")

    def handle(self, *args, **options):
        """处理命令执行"""
        try:
            self.stdout.write(self.style.HTTP_INFO("前端指标分类工具"))
            self.stdout.write("=" * 50)

            # 获取前端指标分类映射
            frontend_mapping = self._get_frontend_mapping()

            # 显示分类计划
            self._show_categorization_plan(frontend_mapping)

            # 如果是dry-run，只显示计划
            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("\n这是预览模式，没有实际更新数据库。"))
                return

            # 执行分类更新
            results = self._update_frontend_categories(frontend_mapping, options["clear_unused"])

            # 显示结果
            self._show_results(results)

        except Exception as e:
            raise CommandError(f"分类更新失败: {e}") from e

    def _get_frontend_mapping(self):
        """获取前端component cards的指标映射"""
        # 基于您提供的实际前端component cards
        return {
            # Consumer/Household Debts - 8个指标
            "HDTGPDUSQ163N": "Consumer/Household Debts",  # Household Debt-to-GDP Ratio (主要分类)
            "TDSP": "Consumer/Household Debts",  # Household Debt Service Ratio
            "MDOAH": "Consumer/Household Debts",  # Mortgage Debt Outstanding
            "RCCCBBALTOT": "Consumer/Household Debts",  # Credit Card Debt Balances
            "SLOASM": "Consumer/Household Debts",  # Student Loans Outstanding
            "TOTALSL": "Consumer/Household Debts",  # Total Consumer Credit
            "DTCOLNVHFNM": "Consumer/Household Debts",  # Total Household Debt
            "FEDFUNDS": "Interest Rates",  # Federal Funds Rate (主要在Interest Rates中)
            # Government Deficit Financing - 8个指标
            "GFDEBTN": "Government Deficit Financing",  # Federal Debt: Total Public Debt
            "GFDEGDQ188S": "Interest Rates",  # Debt-to-GDP Ratio (主要在Interest Rates中)
            "MTSDS133FMS": "Government Deficit Financing",  # Federal Surplus or Deficit
            "W006RC1Q027SBEA": "Government Deficit Financing",  # Federal Tax Receipts
            "FYONET": "Government Deficit Financing",  # Federal Net Outlays
            "FGEXPND": "Government Deficit Financing",  # Federal Current Expenditures
            "FGRECPT": "Government Deficit Financing",  # Federal Current Receipts
            "EXCSRESNW": "Government Deficit Financing",  # Excess Reserves
            # Interest Rates - 8个指标 (部分与上面重复)
            # 'FEDFUNDS': 已在上面设为 Interest Rates
            "MORTGAGE30US": "Interest Rates",  # 30-Year Fixed Mortgage Rate
            "DGS10": "Interest Rates",  # 10-Year Treasury Yield
            "DGS2": "Interest Rates",  # 2-Year Treasury Yield
            "TB3MS": "Interest Rates",  # 3-Month Treasury Bill
            "PCEPI": "Interest Rates",  # PCE Price Index (主要在Interest Rates中)
            "CPIAUCSL": "Interest Rates",  # Consumer Price Index (主要在Interest Rates中)
            # 'GFDEGDQ188S': 已在上面设为 Interest Rates
        }

    def _show_categorization_plan(self, frontend_mapping):
        """显示分类计划"""
        self.stdout.write("\n前端指标分类计划:")
        self.stdout.write("-" * 40)

        # 按分类分组
        categories = {}
        for series_id, category in frontend_mapping.items():
            if category not in categories:
                categories[category] = []
            categories[category].append(series_id)

        for category, indicators in categories.items():
            self.stdout.write(f"\n{category} ({len(indicators)}个指标):")
            for series_id in indicators:
                try:
                    info = FredUsSeriesInfo.objects.get(series_id=series_id)
                    title = info.title[:50] + "..." if len(info.title) > 50 else info.title
                    self.stdout.write(f"  • {series_id}: {title}")
                except FredUsSeriesInfo.DoesNotExist:
                    self.stdout.write(f"  • {series_id}: [未找到记录]")

        # 统计信息
        total_db = FredUsSeriesInfo.objects.count()
        total_frontend = len(frontend_mapping)
        total_unused = total_db - total_frontend

        self.stdout.write("\n统计信息:")
        self.stdout.write(f"  数据库总指标: {total_db}")
        self.stdout.write(f"  前端使用指标: {total_frontend}")
        self.stdout.write(f"  未使用指标: {total_unused}")

        if total_unused > 0:
            self.stdout.write("\n前10个未使用的指标:")
            unused_indicators = FredUsSeriesInfo.objects.exclude(
                series_id__in=frontend_mapping.keys()
            ).order_by("series_id")[:10]

            for info in unused_indicators:
                title = info.title[:40] + "..." if len(info.title) > 40 else info.title
                self.stdout.write(f"  • {info.series_id}: {title}")

            if total_unused > 10:
                self.stdout.write(f"  ... 以及其他 {total_unused - 10} 个")

    def _update_frontend_categories(self, frontend_mapping, clear_unused=False):
        """更新前端指标分类"""
        results = {"frontend_updated": 0, "unused_cleared": 0, "errors": 0, "error_details": []}

        self.stdout.write("\n开始更新前端指标分类...")
        self.stdout.write("=" * 40)

        # 更新前端指标
        for series_id, category in frontend_mapping.items():
            try:
                info = FredUsSeriesInfo.objects.get(series_id=series_id)
                info.category = category
                info.save()

                results["frontend_updated"] += 1
                self.stdout.write(f"  ✓ {series_id} -> {category}")

            except FredUsSeriesInfo.DoesNotExist:
                error_msg = f"指标不存在: {series_id}"
                results["errors"] += 1
                results["error_details"].append(error_msg)
                self.stdout.write(self.style.ERROR(f"  ✗ {series_id}: 未找到"))
            except Exception as e:
                error_msg = f"更新失败 {series_id}: {e!s}"
                results["errors"] += 1
                results["error_details"].append(error_msg)
                self.stdout.write(self.style.ERROR(f"  ✗ {series_id}: {e!s}"))

        # 清除未使用指标的分类
        if clear_unused:
            self.stdout.write("\n清除未使用指标的分类...")
            unused_indicators = FredUsSeriesInfo.objects.exclude(
                series_id__in=frontend_mapping.keys()
            )

            for info in unused_indicators:
                try:
                    info.category = None
                    info.save()
                    results["unused_cleared"] += 1
                    self.stdout.write(f"  ○ {info.series_id} -> [清除分类]")
                except Exception as e:
                    results["errors"] += 1
                    results["error_details"].append(f"清除失败 {info.series_id}: {e!s}")

        return results

    def _show_results(self, results):
        """显示更新结果"""
        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.HTTP_INFO("分类更新完成!"))

        self.stdout.write(f"前端指标更新: {results['frontend_updated']} 个")
        if results["unused_cleared"] > 0:
            self.stdout.write(f"未使用指标清除: {results['unused_cleared']} 个")
        if results["errors"] > 0:
            self.stdout.write(self.style.ERROR(f"错误数量: {results['errors']}"))

        if results["error_details"]:
            self.stdout.write("\n错误详情:")
            for error in results["error_details"][:5]:
                self.stdout.write(f"  • {error}")
            if len(results["error_details"]) > 5:
                self.stdout.write(f"  ... 以及其他 {len(results['error_details']) - 5} 个错误")

        # 验证最终结果
        self._verify_final_categorization()

    def _verify_final_categorization(self):
        """验证最终的分类结果"""
        self.stdout.write("\n验证分类结果:")
        self.stdout.write("-" * 30)

        # 统计各分类的数量
        categories = (
            FredUsSeriesInfo.objects.exclude(
                models.Q(category__isnull=True) | models.Q(category="")
            )
            .values("category")
            .annotate(count=models.Count("series_id"))
            .order_by("-count")
        )

        categorized_count = 0
        for cat in categories:
            category_name = cat["category"]
            count = cat["count"]
            categorized_count += count
            self.stdout.write(f"  ✓ {category_name}: {count} 个指标")

        # 统计未分类的数量
        uncategorized_count = FredUsSeriesInfo.objects.filter(
            models.Q(category__isnull=True) | models.Q(category="")
        ).count()

        total_indicators = FredUsSeriesInfo.objects.count()

        self.stdout.write(f"\n总计: {total_indicators} 个指标")
        self.stdout.write(f"已分类: {categorized_count} 个")
        self.stdout.write(f"未分类: {uncategorized_count} 个")

        if uncategorized_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"✓ {uncategorized_count} 个未使用指标未分类（正确）")
            )
