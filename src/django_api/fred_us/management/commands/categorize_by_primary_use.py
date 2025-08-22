"""
Django管理命令: 基于主要用途对前端指标进行分类
为每个指标选择一个主要分类，基于实际前端component cards使用情况
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import models
from fred_us.models import FredUsSeriesInfo


class Command(BaseCommand):
    help = '基于主要用途对前端指标进行分类'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示分类计划，不实际更新数据库'
        )
        parser.add_argument(
            '--mark-unused',
            action='store_true',
            help='将前端未使用的指标标记为Unused'
        )

    def handle(self, *args, **options):
        """处理命令执行"""
        try:
            self.stdout.write(
                self.style.HTTP_INFO("基于主要用途的前端指标分类工具")
            )
            self.stdout.write("=" * 60)
            
            # 获取主要用途分类映射
            primary_mapping = self._get_primary_use_mapping()
            
            # 显示分类计划
            self._show_categorization_plan(primary_mapping, options['mark_unused'])
            
            # 如果是dry-run，只显示计划
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING("\n这是预览模式，没有实际更新数据库。")
                )
                return
            
            # 执行分类更新
            results = self._update_primary_categories(primary_mapping, options['mark_unused'])
            
            # 显示结果
            self._show_results(results)
            
        except Exception as e:
            raise CommandError(f'分类更新失败: {e}')

    def _get_primary_use_mapping(self):
        """获取基于主要用途的指标分类映射"""
        # 基于前端使用频率和逻辑关联度确定主要分类
        return {
            # Trade Deficits - 8个指标
            'BOPGSTB': 'Trade Deficits',        # Trade Balance: Goods and Services
            'IEABC': 'Trade Deficits',          # Balance on current account
            'BOGZ1FL263061130Q': 'Trade Deficits', # Rest of the World; Treasury Securities
            'B235RC1Q027SBEA': 'Trade Deficits', # Federal government current tax receipts: Customs duties
            'NETEXP': 'Trade Deficits',         # Net Exports of Goods and Services
            'IMPGSC1': 'Trade Deficits',        # Real imports of goods and services
            'EXPGSC1': 'Trade Deficits',        # Real Exports of Goods and Services
            'MTSDS133FMS': 'Trade Deficits',    # Federal Surplus or Deficit (主要在Trade Deficits中使用)
            
            # Government Debts - 7个指标
            'GFDEBTN': 'Government Debts',      # Federal Debt: Total Public Debt
            'LNU00024230': 'Government Debts',  # Population Level - 55 Yrs. & over
            'FYGFD': 'Government Debts',        # Gross Federal Debt
            'FYOIGDA188S': 'Government Debts',  # Federal Outlays: Interest as Percent of GDP
            'FYGFGDQ188S': 'Government Debts',  # Federal Debt Held by the Public as Percent of GDP
            'TOTALGOV': 'Government Debts',     # Total Consumer Credit Owned by Federal Government
            
            # Government Deficit Financing - 4个指标 (去除重复)
            'W006RC1Q027SBEA': 'Government Deficit Financing', # Federal government current tax receipts
            'FYONET': 'Government Deficit Financing',          # Federal Net Outlays
            'FGEXPND': 'Government Deficit Financing',         # Federal Government: Current Expenditures
            'FGRECPT': 'Government Deficit Financing',         # Federal Government Current Receipts
            'EXCSRESNW': 'Government Deficit Financing',       # Excess Reserves
            
            # Private Sector Corporate Debts - 8个指标
            'USREC': 'Private Sector Corporate Debts',         # NBER based Recession Indicators
            'FPCPITOTLZGUSA': 'Private Sector Corporate Debts', # Inflation, consumer prices
            'BAMLH0A0HYM2': 'Private Sector Corporate Debts',  # ICE BofA US High Yield Index
            'WPC': 'Private Sector Corporate Debts',           # Assets: Liquidity and Credit Facilities
            'BCNSDODNS': 'Private Sector Corporate Debts',     # Nonfinancial Corporate Business; Debt Securities
            'AAA': 'Private Sector Corporate Debts',           # Moody's Seasoned Aaa Corporate Bond Yield
            'BAA': 'Private Sector Corporate Debts',           # Moody's Seasoned Baa Corporate Bond Yield
            'NCBCMDPMVCE': 'Private Sector Corporate Debts',   # Nonfinancial Corporate Business; Debt as Percentage
            
            # Consumer/Household Debts - 7个指标
            'HDTGPDUSQ163N': 'Consumer/Household Debts',       # Household Debt to GDP
            'TDSP': 'Consumer/Household Debts',                # Household Debt Service Payments
            'MDOAH': 'Consumer/Household Debts',               # Mortgage Debt Outstanding
            'RCCCBBALTOT': 'Consumer/Household Debts',         # Large Bank Consumer Credit Card Balances
            'SLOASM': 'Consumer/Household Debts',              # Student Loans Owned and Securitized
            'TOTALSL': 'Consumer/Household Debts',             # Total Consumer Credit Owned and Securitized
            'DTCOLNVHFNM': 'Consumer/Household Debts',         # Consumer Motor Vehicle Loans
            
            # Interest Rates - 9个指标 (包含重复指标的主要分类)
            'FEDFUNDS': 'Interest Rates',       # Federal Funds Effective Rate (主要用途)
            'MORTGAGE30US': 'Interest Rates',   # 30-Year Fixed Rate Mortgage Average
            'PCEPI': 'Interest Rates',          # Personal Consumption Expenditures: Chain-type Price Index
            'GFDEGDQ188S': 'Interest Rates',    # Federal Debt: Total Public Debt as Percent of GDP (主要在Interest Rates中显示)
            'DGS10': 'Interest Rates',          # Market Yield on U.S. Treasury Securities at 10-Year
            'DGS2': 'Interest Rates',           # Market Yield on U.S. Treasury Securities at 2-Year
            'TB3MS': 'Interest Rates',          # 3-Month Treasury Bill Secondary Market Rate
            'CPIAUCSL': 'Interest Rates',       # Consumer Price Index (主要在Interest Rates中显示)
            
            # Money Supply - 7个指标
            'M2SL': 'Money Supply',             # M2 Money Stock
            'WALCL': 'Money Supply',            # Assets: Total Assets
            'DRTSCIS': 'Money Supply',          # Net Percentage of Domestic Banks Tightening Standards
            'TOTLL': 'Money Supply',            # Loans and Leases in Bank Credit
            'IORB': 'Money Supply',             # Interest Rate on Reserve Balances
            'RRPONTSYD': 'Money Supply',        # Overnight Reverse Repurchase Agreements
            'M1SL': 'Money Supply',             # M1 Money Stock
            
            # 前端未使用的指标 - 标记为Unused (如果启用mark-unused选项)
            'BOGMBASE': 'Unused',               # Monetary Base: Total
            'HOUST': 'Unused',                  # New Privately-Owned Housing Units Started
            'M2V': 'Unused',                    # Velocity of M2 Money Stock
            'UNRATE': 'Unused',                 # Unemployment Rate
        }

    def _show_categorization_plan(self, primary_mapping, mark_unused=False):
        """显示分类计划"""
        self.stdout.write("\n基于主要用途的分类计划:")
        self.stdout.write("-" * 50)
        
        # 按分类分组
        categories = {}
        for series_id, category in primary_mapping.items():
            if not mark_unused and category == 'Unused':
                continue
            if category not in categories:
                categories[category] = []
            categories[category].append(series_id)
        
        for category, indicators in categories.items():
            self.stdout.write(f"\n{category} ({len(indicators)}个指标):")
            for series_id in indicators:
                try:
                    info = FredUsSeriesInfo.objects.get(series_id=series_id)
                    title = info.title[:60] + "..." if len(info.title) > 60 else info.title
                    self.stdout.write(f"  • {series_id}: {title}")
                except FredUsSeriesInfo.DoesNotExist:
                    self.stdout.write(f"  • {series_id}: [未找到记录]")
        
        # 统计信息
        total_db = FredUsSeriesInfo.objects.count()
        frontend_indicators = [sid for sid, cat in primary_mapping.items() if cat != 'Unused']
        unused_indicators = [sid for sid, cat in primary_mapping.items() if cat == 'Unused']
        
        self.stdout.write(f"\n统计信息:")
        self.stdout.write(f"  数据库总指标: {total_db}")
        self.stdout.write(f"  前端使用指标: {len(frontend_indicators)}")
        if mark_unused:
            self.stdout.write(f"  标记为Unused: {len(unused_indicators)}")
        
        # 检查多重分类的解决方案
        self.stdout.write(f"\n多重分类指标的主要用途分配:")
        multi_use_indicators = {
            'FEDFUNDS': ['Consumer/Household Debts', 'Interest Rates', 'Money Supply'],
            'GFDEGDQ188S': ['Government Debts', 'Government Deficit Financing', 'Interest Rates'],
            'MTSDS133FMS': ['Government Debts', 'Government Deficit Financing', 'Trade Deficits'],
            'PCEPI': ['Interest Rates'],
            'CPIAUCSL': ['Interest Rates'],
        }
        
        for series_id, components in multi_use_indicators.items():
            primary = primary_mapping.get(series_id, 'Unknown')
            self.stdout.write(f"  • {series_id}: 出现在 {components} → 主要分类: {primary}")

    def _update_primary_categories(self, primary_mapping, mark_unused=False):
        """更新主要用途分类"""
        results = {
            'updated': 0,
            'marked_unused': 0,
            'errors': 0,
            'categories': {},
            'error_details': []
        }
        
        self.stdout.write(f"\n开始更新主要用途分类...")
        self.stdout.write("=" * 50)
        
        for series_id, category in primary_mapping.items():
            # 如果不标记unused且category是Unused，跳过
            if not mark_unused and category == 'Unused':
                continue
                
            try:
                info = FredUsSeriesInfo.objects.get(series_id=series_id)
                
                if category == 'Unused':
                    info.category = None  # 清除分类
                    results['marked_unused'] += 1
                    status_msg = f"  ○ {series_id} -> [清除分类]"
                else:
                    info.category = category
                    results['updated'] += 1
                    status_msg = f"  ✓ {series_id} -> {category}"
                
                info.save()
                
                if category not in results['categories']:
                    results['categories'][category] = 0
                results['categories'][category] += 1
                
                self.stdout.write(status_msg)
                
            except FredUsSeriesInfo.DoesNotExist:
                error_msg = f"指标不存在: {series_id}"
                results['errors'] += 1
                results['error_details'].append(error_msg)
                self.stdout.write(
                    self.style.ERROR(f"  ✗ {series_id}: 未找到")
                )
            except Exception as e:
                error_msg = f"更新失败 {series_id}: {str(e)}"
                results['errors'] += 1
                results['error_details'].append(error_msg)
                self.stdout.write(
                    self.style.ERROR(f"  ✗ {series_id}: {str(e)}")
                )
        
        return results

    def _show_results(self, results):
        """显示更新结果"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.HTTP_INFO("主要用途分类更新完成!")
        )
        
        self.stdout.write(f"前端指标更新: {results['updated']} 个")
        if results['marked_unused'] > 0:
            self.stdout.write(f"未使用指标标记: {results['marked_unused']} 个")
        if results['errors'] > 0:
            self.stdout.write(
                self.style.ERROR(f"错误数量: {results['errors']}")
            )
        
        self.stdout.write(f"\n按分类统计:")
        for category, count in results['categories'].items():
            if category:
                self.stdout.write(f"  {category}: {count} 个")
            else:
                self.stdout.write(f"  [未分类]: {count} 个")
        
        if results['error_details']:
            self.stdout.write(f"\n错误详情:")
            for error in results['error_details'][:5]:
                self.stdout.write(f"  • {error}")
        
        # 验证最终结果
        self._verify_final_categorization()

    def _verify_final_categorization(self):
        """验证最终的分类结果"""
        self.stdout.write(f"\n验证最终分类结果:")
        self.stdout.write("-" * 30)
        
        # 统计各分类的数量
        categories = FredUsSeriesInfo.objects.exclude(
            models.Q(category__isnull=True) | models.Q(category='')
        ).values('category').annotate(
            count=models.Count('series_id')
        ).order_by('-count')
        
        categorized_count = 0
        for cat in categories:
            category_name = cat['category']
            count = cat['count']
            categorized_count += count
            self.stdout.write(f"  ✓ {category_name}: {count} 个指标")
        
        # 统计未分类的数量
        uncategorized_count = FredUsSeriesInfo.objects.filter(
            models.Q(category__isnull=True) | models.Q(category='')
        ).count()
        
        total_indicators = FredUsSeriesInfo.objects.count()
        
        self.stdout.write(f"\n总计: {total_indicators} 个指标")
        self.stdout.write(f"已分类: {categorized_count} 个")
        self.stdout.write(f"未分类: {uncategorized_count} 个")
        
        if categorized_count == 49:  # 前端使用的指标数量
            self.stdout.write(
                self.style.SUCCESS("✓ 所有前端指标都已正确分类!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠️ 预期49个前端指标，实际分类了{categorized_count}个")
            )

