"""
US FRED Data Fetcher
美国FRED数据获取器 - 基于通用基类实现
"""

import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from fred_common.base_fetcher import BaseFredDataFetcher
from .models import FredUsIndicator, FredUsSeriesInfo

logger = logging.getLogger(__name__)


class UsFredDataFetcher(BaseFredDataFetcher):
    """美国FRED数据获取器 - 继承基础类实现美国特定功能"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.country = 'US'
        logger.info("美国FRED数据获取器初始化完成")
    
    def save_series_info(self, series_id: str, series_info: Dict) -> bool:
        """保存系列信息到美国FRED数据库"""
        try:
            series_obj, created = FredUsSeriesInfo.objects.update_or_create(
                series_id=series_id,
                defaults={
                    'title': series_info.get('title', ''),
                    'category': series_info.get('category_name', ''),
                    'units': series_info.get('units', ''),
                    'frequency': series_info.get('frequency', ''),
                    'seasonal_adjustment': series_info.get('seasonal_adjustment', ''),
                    'notes': series_info.get('notes', '')
                }
            )
            
            action = "创建" if created else "更新"
            logger.info(f"成功{action}美国系列信息: {series_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存美国系列信息失败 {series_id}: {e}")
            return False
    
    def save_observations(self, series_id: str, observations: List[Dict]) -> int:
        """保存观测数据到美国FRED数据库 - 实现基类抽象方法"""
        saved_count = 0
        indicator_mapping = self.get_indicator_mapping()
        indicator_type = indicator_mapping.get(series_id, 'unknown')
        indicator_name = f"US {indicator_type.replace('_', ' ').title()}"
        
        try:
            for observation in observations:
                date = observation.get('date')
                value = observation.get('value')
                
                if date and value and value != '.':
                    try:
                        indicator_obj, created = FredUsIndicator.objects.update_or_create(
                            series_id=series_id,
                            date=date,
                            defaults={
                                'indicator_name': indicator_name,
                                'indicator_type': indicator_type,
                                'value': float(value),
                                'source': 'FRED',
                                'metadata': {
                                    'country': self.country,
                                    'original_series_id': series_id
                                }
                            }
                        )
                        
                        if created:
                            saved_count += 1
                            
                    except (ValueError, TypeError) as e:
                        logger.warning(f"跳过无效数据点 {series_id} {date}: {value} - {e}")
                        continue
                        
            logger.info(f"成功保存美国观测数据: {series_id}, 新增 {saved_count} 条记录")
            return saved_count
            
        except Exception as e:
            logger.error(f"保存美国观测数据失败 {series_id}: {e}")
            return 0
    
    def get_indicator_mapping(self) -> Dict[str, str]:
        """获取美国经济指标映射"""
        return {
            # 核心经济指标
            'UNRATE': 'unemployment_rate',
            'CPIAUCNS': 'cpi_all_items', 
            'CPILFESL': 'cpi_core',
            'GDP': 'gross_domestic_product',
            'GDPC1': 'real_gdp',
            'GDPPOT': 'potential_gdp',
            
            # 利率和货币政策
            'FEDFUNDS': 'federal_funds_rate',
            'DGS10': '10_year_treasury',
            'DGS2': '2_year_treasury',
            'TB3MS': '3_month_treasury',
            
            # 消费者和家庭债务指标
            'HDTGPDUSQ163N': 'household_debt_to_gdp',
            'TDSP': 'debt_service_ratio',
            'MDOAH': 'mortgage_debt_outstanding',
            'RCCCBBALTOT': 'credit_card_balances',
            'SLOASM': 'student_loans',
            'TOTALSL': 'consumer_credit_total',
            'DTCOLNVHFNM': 'household_debt_total',
            
            # 消费和零售
            'RSXFS': 'retail_sales',
            'PCE': 'personal_consumption',
            'PSAVERT': 'personal_saving_rate',
            
            # 就业市场
            'PAYEMS': 'nonfarm_payrolls',
            'CIVPART': 'labor_participation_rate',
            'EMRATIO': 'employment_population_ratio',
            
            # 制造业和工业
            'INDPRO': 'industrial_production',
            'NAPM': 'ism_manufacturing',
            'HOUST': 'housing_starts',
            
            # 通胀和价格
            'DCOILWTICO': 'oil_price_wti',
            'GOLDAMGBD228NLBM': 'gold_price',
            
            # 贸易和国际
            'BOPGSTB': 'trade_balance',
            'EXUSEU': 'usd_eur_exchange_rate',
            'EXJPUS': 'jpy_usd_exchange_rate',
        }
    
    def get_supported_indicators(self) -> List[str]:
        """获取支持的美国经济指标列表"""
        return list(self.get_indicator_mapping().keys())
    
    def get_indicator_categories(self) -> Dict[str, List[str]]:
        """获取按类别分组的美国经济指标"""
        return {
            'labor_market': ['UNRATE', 'PAYEMS', 'CIVPART', 'EMRATIO'],
            'inflation': ['CPIAUCNS', 'CPILFESL', 'DCOILWTICO', 'GOLDAMGBD228NLBM'],
            'economic_growth': ['GDP', 'GDPC1', 'GDPPOT', 'INDPRO'],
            'monetary_policy': ['FEDFUNDS', 'DGS10', 'DGS2', 'TB3MS'],
            'household_debt': ['HDTGPDUSQ163N', 'TDSP', 'MDOAH', 'RCCCBBALTOT', 'SLOASM', 'TOTALSL', 'DTCOLNVHFNM'],
            'consumption': ['RSXFS', 'PCE', 'PSAVERT'],
            'manufacturing': ['NAPM', 'HOUST'],
            'trade': ['BOPGSTB', 'EXUSEU', 'EXJPUS']
        }
    
    def validate_indicator(self, indicator_name: str) -> bool:
        """验证指标是否支持"""
        supported = self.get_supported_indicators()
        return indicator_name in supported
    
    def get_latest_data_summary(self) -> Dict[str, Any]:
        """获取美国最新数据摘要"""
        try:
            from django.db.models import Max
            
            # 获取每个指标的最新值
            latest_data = {}
            for series_id in self.get_supported_indicators():
                latest_record = FredUsIndicator.objects.filter(
                    series_id=series_id
                ).order_by('-date').first()
                
                if latest_record:
                    latest_data[series_id] = {
                        'value': float(latest_record.value),
                        'date': latest_record.date.isoformat(),
                        'indicator_name': latest_record.indicator_name,
                        'indicator_type': latest_record.indicator_type
                    }
            
            summary = {
                'country': self.country,
                'total_indicators': len(latest_data),
                'last_updated': FredUsIndicator.objects.aggregate(
                    Max('updated_at')
                ).get('updated_at__max'),
                'indicators': latest_data
            }
            
            logger.info(f"生成美国数据摘要: {len(latest_data)} 个指标")
            return {'success': True, 'data': summary}
            
        except Exception as e:
            logger.error(f"获取美国数据摘要失败: {e}")
            return {'success': False, 'error': str(e)}

# 工厂函数（推荐使用）
def get_us_fred_fetcher() -> UsFredDataFetcher:
    """获取美国FRED数据获取器实例"""
    return UsFredDataFetcher()
