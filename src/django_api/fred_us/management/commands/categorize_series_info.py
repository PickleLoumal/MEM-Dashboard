"""
Django管理命令: 为Series Info进行Dashboard组件分类
基于component card对所有FRED US指标进行分类
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import models
from fred_us.models import FredUsSeriesInfo


class Command(BaseCommand):
    help = '为Series Info进行Dashboard组件分类'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示分类计划，不实际更新数据库'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='显示详细的分类过程'
        )

    def handle(self, *args, **options):
        """处理命令执行"""
        try:
            self.stdout.write(
                self.style.HTTP_INFO("FRED US Series Info Dashboard组件分类工具")
            )
            self.stdout.write("=" * 70)
            
            # 获取分类映射
            categorization_map = self._get_categorization_map()
            
            # 显示分类计划
            self._show_categorization_plan(categorization_map, options['verbose'])
            
            # 如果是dry-run，只显示计划
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING("\n这是预览模式，没有实际更新数据库。")
                )
                return
            
            # 执行分类更新
            results = self._update_categories(categorization_map)
            
            # 显示结果
            self._show_results(results)
            
        except Exception as e:
            raise CommandError(f'分类更新失败: {e}')

    def _get_categorization_map(self):
        """获取指标到Dashboard组件的分类映射"""
        return {
            # Consumer/Household Debts 消费者/家庭债务
            'Consumer_Household_Debts': {
                'display_name': 'Consumer/Household Debts',
                'description': '消费者和家庭债务相关指标',
                'indicators': [
                    'HDTGPDUSQ163N',    # Household Debt-to-GDP Ratio
                    'TDSP',             # Household Debt Service Ratio
                    'MDOAH',            # Mortgage Debt Outstanding
                    'RCCCBBALTOT',      # Credit Card Debt Balances
                    'SLOASM',           # Student Loans Outstanding
                    'TOTALSL',          # Total Consumer Credit
                    'DTCOLNVHFNM',      # Total Household Debt (Consumer Motor Vehicle Loans)
                    'TOTALGOV',         # Total Consumer Credit Owned by Federal Government
                ]
            },
            
            # Government Debts 政府债务
            'Government_Debts': {
                'display_name': 'Government Debts',
                'description': '政府债务相关指标',
                'indicators': [
                    'FYGFD',            # Gross Federal Debt
                    'FYGFGDQ188S',      # Federal Debt Held by the Public as Percent of GDP
                    'FYOIGDA188S',      # Federal Outlays: Interest as Percent of GDP
                ]
            },
            
            # Government Deficit Financing 政府赤字融资
            'Government_Deficit_Financing': {
                'display_name': 'Government Deficit Financing',
                'description': '政府赤字融资相关指标',
                'indicators': [
                    'GFDEBTN',          # Federal Debt: Total Public Debt
                    'GFDEGDQ188S',      # Federal Debt: Total Public Debt as Percent of GDP
                    'MTSDS133FMS',      # Federal Surplus or Deficit
                    'W006RC1Q027SBEA',  # Federal Tax Receipts
                    'FYONET',           # Federal Net Outlays
                    'FGEXPND',          # Federal Current Expenditures
                    'FGRECPT',          # Federal Current Receipts
                    'EXCSRESNW',        # Excess Reserves
                ]
            },
            
            # International Finance 国际金融
            'International_Finance': {
                'display_name': 'International Finance',
                'description': '国际金融和外国投资指标',
                'indicators': [
                    'B235RC1Q027SBEA',  # Federal government current tax receipts: Customs duties
                    'BOGZ1FL263061130Q', # Rest of the World; Treasury Securities Held by Foreign Official Institutions
                ]
            },
            
            # Trade Deficits 贸易赤字
            'Trade_Deficits': {
                'display_name': 'Trade Deficits',
                'description': '贸易赤字和国际收支指标',
                'indicators': [
                    'BOPGSTB',          # Trade Balance: Goods and Services
                    'IEABC',            # Balance on current account
                    'NETEXP',           # Net Exports of Goods and Services
                    'EXPGSC1',          # Real Exports of Goods and Services
                    'IMPGSC1',          # Real imports of goods and services
                ]
            },
            
            # Private Sector Corporate Debts 私营部门企业债务
            'Private_Sector_Corporate_Debts': {
                'display_name': 'Private Sector Corporate Debts',
                'description': '私营部门企业债务和信用指标',
                'indicators': [
                    'BCNSDODNS',        # Nonfinancial Corporate Business; Debt Securities and Loans
                    'AAA',              # Moody's Seasoned Aaa Corporate Bond Yield
                    'BAA',              # Moody's Seasoned Baa Corporate Bond Yield
                    'BAMLH0A0HYM2',     # ICE BofA US High Yield Index Option-Adjusted Spread
                    'NCBCMDPMVCE',      # Nonfinancial Corporate Business; Debt as a Percentage of Market Value
                    'USREC',            # NBER based Recession Indicators
                ]
            },
            
            # Money Supply 货币供应量
            'Money_Supply': {
                'display_name': 'Money Supply',
                'description': '货币供应量和货币政策指标',
                'indicators': [
                    'FEDFUNDS',         # Federal Funds Rate
                    'M1SL',             # M1 Money Stock
                    'M2SL',             # M2 Money Stock
                    'M2V',              # Velocity of M2 Money Stock
                    'BOGMBASE',         # Monetary Base: Total
                    'WALCL',            # Fed Total Assets
                    'RRPONTSYD',        # Overnight Reverse Repurchase Agreements
                    'IORB',             # Interest Rate on Reserve Balances
                ]
            },
            
            # Interest Rates 利率
            'Interest_Rates': {
                'display_name': 'Interest Rates',
                'description': '利率和债券收益率指标',
                'indicators': [
                    'DGS10',            # 10-Year Treasury Constant Maturity Rate
                    'DGS2',             # 2-Year Treasury Constant Maturity Rate
                    'TB3MS',            # 3-Month Treasury Bill
                    'MORTGAGE30US',     # 30-Year Fixed Rate Mortgage
                ]
            },
            
            # Inflation 通胀
            'Inflation': {
                'display_name': 'Inflation',
                'description': '通胀和价格指数',
                'indicators': [
                    'CPIAUCSL',         # Consumer Price Index
                    'PCEPI',            # Personal Consumption Expenditures Price Index
                    'FPCPITOTLZGUSA',   # Inflation, consumer prices for the United States
                ]
            },
            
            # Banking Credit 银行信贷
            'Banking_Credit': {
                'display_name': 'Banking & Credit',
                'description': '银行业和信贷相关指标',
                'indicators': [
                    'TOTLL',            # Loans and Leases in Bank Credit
                    'DRTSCIS',          # Net Percentage of Domestic Banks Tightening Standards
                    'WPC',              # Assets: Liquidity and Credit Facilities: Primary Credit
                ]
            },
            
            # Economic Activity 经济活动
            'Economic_Activity': {
                'display_name': 'Economic Activity',
                'description': '经济活动和劳动力市场指标',
                'indicators': [
                    'UNRATE',           # Unemployment Rate
                    'HOUST',            # Housing Starts
                    'LNU00024230',      # Population Level - 55 Yrs. & over
                ]
            }
        }

    def _show_categorization_plan(self, categorization_map, verbose=False):
        """显示分类计划"""
        self.stdout.write("\n分类计划:")
        self.stdout.write("-" * 50)
        
        total_indicators = 0
        for category_key, category_info in categorization_map.items():
            indicator_count = len(category_info['indicators'])
            total_indicators += indicator_count
            
            self.stdout.write(
                f"\n{category_info['display_name']} ({indicator_count}个指标)"
            )
            self.stdout.write(f"  {category_info['description']}")
            
            if verbose:
                for series_id in category_info['indicators']:
                    try:
                        info = FredUsSeriesInfo.objects.get(series_id=series_id)
                        title = info.title[:60] + "..." if len(info.title) > 60 else info.title
                        self.stdout.write(f"    • {series_id}: {title}")
                    except FredUsSeriesInfo.DoesNotExist:
                        self.stdout.write(f"    • {series_id}: [未找到记录]")
        
        # 检查是否有未分类的指标
        all_categorized = set()
        for category_info in categorization_map.values():
            all_categorized.update(category_info['indicators'])
        
        all_existing = set(FredUsSeriesInfo.objects.values_list('series_id', flat=True))
        uncategorized = all_existing - all_categorized
        
        self.stdout.write(f"\n统计:")
        self.stdout.write(f"  总分类数量: {len(categorization_map)}")
        self.stdout.write(f"  已分类指标: {total_indicators}")
        self.stdout.write(f"  数据库总指标: {len(all_existing)}")
        
        if uncategorized:
            self.stdout.write(
                self.style.WARNING(f"  未分类指标: {len(uncategorized)}个")
            )
            if verbose:
                for series_id in sorted(uncategorized):
                    try:
                        info = FredUsSeriesInfo.objects.get(series_id=series_id)
                        self.stdout.write(f"    • {series_id}: {info.title}")
                    except:
                        pass
        else:
            self.stdout.write(
                self.style.SUCCESS("  ✓ 所有指标都已分类")
            )

    def _update_categories(self, categorization_map):
        """执行分类更新"""
        results = {
            'updated': 0,
            'errors': 0,
            'categories': {},
            'error_details': []
        }
        
        self.stdout.write(f"\n开始更新分类...")
        self.stdout.write("=" * 50)
        
        for category_key, category_info in categorization_map.items():
            category_name = category_info['display_name']
            updated_count = 0
            
            self.stdout.write(f"\n更新分类: {category_name}")
            
            for series_id in category_info['indicators']:
                try:
                    info = FredUsSeriesInfo.objects.get(series_id=series_id)
                    info.category = category_name
                    info.save()
                    
                    updated_count += 1
                    results['updated'] += 1
                    
                    self.stdout.write(f"  ✓ {series_id}")
                    
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
            
            results['categories'][category_name] = updated_count
            self.stdout.write(f"  {category_name}: {updated_count} 个指标已更新")
        
        return results

    def _show_results(self, results):
        """显示更新结果"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.HTTP_INFO("分类更新完成!")
        )
        
        self.stdout.write(f"总计更新: {results['updated']} 个指标")
        if results['errors'] > 0:
            self.stdout.write(
                self.style.ERROR(f"错误数量: {results['errors']}")
            )
        
        self.stdout.write(f"\n按分类统计:")
        for category, count in results['categories'].items():
            self.stdout.write(f"  {category}: {count} 个")
        
        if results['error_details']:
            self.stdout.write(f"\n错误详情:")
            for error in results['error_details'][:10]:  # 只显示前10个错误
                self.stdout.write(f"  • {error}")
            if len(results['error_details']) > 10:
                self.stdout.write(f"  ... 以及其他 {len(results['error_details']) - 10} 个错误")
        
        # 验证最终结果
        self._verify_final_categorization()

    def _verify_final_categorization(self):
        """验证最终的分类结果"""
        self.stdout.write(f"\n验证分类结果:")
        self.stdout.write("-" * 30)
        
        # 统计各分类的数量
        categories = FredUsSeriesInfo.objects.values('category').annotate(
            count=models.Count('series_id')
        ).order_by('-count')
        
        total_categorized = 0
        for cat in categories:
            category_name = cat['category'] or '未分类'
            count = cat['count']
            total_categorized += count
            
            status = "✓" if cat['category'] else "✗"
            self.stdout.write(f"  {status} {category_name}: {count} 个指标")
        
        total_indicators = FredUsSeriesInfo.objects.count()
        uncategorized_count = FredUsSeriesInfo.objects.filter(
            models.Q(category__isnull=True) | models.Q(category='')
        ).count()
        
        self.stdout.write(f"\n总计: {total_indicators} 个指标")
        if uncategorized_count == 0:
            self.stdout.write(
                self.style.SUCCESS("✓ 所有指标都已正确分类!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"✗ 仍有 {uncategorized_count} 个指标未分类")
            )
