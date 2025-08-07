"""
Japan FRED Data Fetcher
日本FRED数据获取器 - 继承基础获取器实现日本特定功能
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fred_common.base_fetcher import BaseFredDataFetcher
from .config_manager import JapanFredConfigManager

logger = logging.getLogger(__name__)


class JapanFredDataFetcher(BaseFredDataFetcher):
    """日本FRED数据获取器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化日本FRED数据获取器
        
        Args:
            api_key: FRED API密钥，如果不提供将使用环境变量
        """
        super().__init__(api_key)
        self.config_manager = JapanFredConfigManager()
        
        logger.info("日本FRED数据获取器已初始化")
    
    def get_default_api_key(self) -> str:
        """获取默认API密钥从环境变量"""
        api_key = os.getenv('FRED_API_KEY')
        if not api_key:
            logger.error("未找到FRED_API_KEY环境变量")
            raise ValueError("FRED API密钥未配置，请设置FRED_API_KEY环境变量")
        return api_key
    
    def get_country_specific_config(self) -> Dict[str, Any]:
        """获取日本特定配置"""
        return {
            'country': 'Japan',
            'country_code': 'JP',
            'timezone': 'Asia/Tokyo',
            'default_currency': 'JPY',
            'fred_series_prefix': 'JPN',
            'api_config': self.config_manager.get_api_info()
        }
    
    def get_indicator_data(self, indicator_name: str, 
                          start_date: Optional[str] = None, 
                          end_date: Optional[str] = None,
                          limit: int = 100) -> Dict[str, Any]:
        """
        获取指定指标的数据
        
        Args:
            indicator_name: 指标名称 (如: 'cpi', 'gdp', 'unemployment')
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 限制记录数
            
        Returns:
            包含数据和元信息的字典
        """
        # 验证指标名称
        if not self.config_manager.validate_indicator(indicator_name):
            logger.error(f"不支持的日本经济指标: {indicator_name}")
            return {
                'success': False,
                'error': f'不支持的指标: {indicator_name}',
                'supported_indicators': self.config_manager.get_all_indicators()
            }
        
        # 获取指标配置
        indicator_config = self.config_manager.get_indicator_config(indicator_name)
        if not indicator_config:
            logger.error(f"无法获取指标配置: {indicator_name}")
            return {
                'success': False,
                'error': f'无法获取指标配置: {indicator_name}'
            }
            
        series_id = indicator_config['series_id']
        
        logger.info(f"开始获取日本指标数据: {indicator_name} ({series_id})")
        
        # 获取系列信息
        series_info = self.get_series_info(series_id)
        if not series_info:
            logger.error(f"无法获取系列信息: {series_id}")
            return {
                'success': False,
                'error': f'无法获取系列信息: {series_id}'
            }
        
        # 获取观测数据
        observations = self.get_series_observations(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if not observations or len(observations) == 0:
            logger.warning(f"数据验证失败或数据不完整: {series_id}")
            return {
                'success': False,
                'error': f'数据验证失败或数据不完整: {series_id}'
            }
        
        # 计算统计信息
        statistics = self._calculate_statistics(observations)
        
        # 格式化数据
        formatted_data = []
        for obs in observations:
            formatted_obs = {
                'date': obs.get('date'),
                'value': obs.get('value'),
                'realtime_start': obs.get('realtime_start'),
                'realtime_end': obs.get('realtime_end'),
                'series_id': series_info.get('id') if series_info else series_id,
                'title': series_info.get('title') if series_info else indicator_config['name'],
                'units': series_info.get('units') if series_info else indicator_config['unit'],
                'frequency': series_info.get('frequency') if series_info else indicator_config['frequency']
            }
            formatted_data.append(formatted_obs)
        
        logger.info(f"成功获取日本指标数据: {indicator_name}, {len(formatted_data)}条记录")
        
        return {
            'success': True,
            'indicator_name': indicator_name,
            'series_id': series_id,
            'country': 'Japan',
            'data_count': len(formatted_data),
            'series_info': series_info,
            'indicator_config': indicator_config,
            'statistics': statistics,
            'data': formatted_data,
            'fetch_time': datetime.now().isoformat()
        }
    
    def get_multiple_indicators(self, indicator_names: List[str], 
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None,
                               limit: int = 100) -> Dict[str, Any]:
        """
        批量获取多个指标数据
        
        Args:
            indicator_names: 指标名称列表
            start_date: 开始日期
            end_date: 结束日期
            limit: 每个指标的记录限制
            
        Returns:
            批量获取结果
        """
        logger.info(f"开始批量获取日本指标数据: {indicator_names}")
        
        results = {}
        success_count = 0
        
        for indicator_name in indicator_names:
            try:
                result = self.get_indicator_data(
                    indicator_name=indicator_name,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit
                )
                
                results[indicator_name] = result
                if result.get('success'):
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"获取指标数据失败 {indicator_name}: {e}")
                results[indicator_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return {
            'batch_success': True,
            'total_indicators': len(indicator_names),
            'success_count': success_count,
            'failure_count': len(indicator_names) - success_count,
            'results': results,
            'fetch_time': datetime.now().isoformat()
        }
    
    def get_category_indicators(self, category: str,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None,
                               limit: int = 100) -> Dict[str, Any]:
        """
        获取指定类别的所有指标数据
        
        Args:
            category: 指标类别 ('inflation', 'economic_growth', etc.)
            start_date: 开始日期
            end_date: 结束日期
            limit: 每个指标的记录限制
            
        Returns:
            类别指标数据
        """
        indicators = self.config_manager.get_indicators_by_category(category)
        
        if not indicators:
            return {
                'success': False,
                'error': f'未找到类别 {category} 的指标',
                'available_categories': self.config_manager.get_categories()
            }
        
        logger.info(f"获取日本{category}类别指标: {indicators}")
        
        return self.get_multiple_indicators(
            indicator_names=indicators,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def get_latest_data_summary(self) -> Dict[str, Any]:
        """
        获取所有指标的最新数据摘要
        
        Returns:
            最新数据摘要
        """
        logger.info("获取日本经济指标最新数据摘要")
        
        all_indicators = self.config_manager.get_all_indicators()
        summary = {}
        
        for indicator_name in all_indicators:
            try:
                # 只获取最新的1条数据
                result = self.get_indicator_data(
                    indicator_name=indicator_name,
                    limit=1
                )
                
                if result.get('success') and result.get('data'):
                    latest_data = result['data'][0]
                    summary[indicator_name] = {
                        'series_id': result['series_id'],
                        'value': latest_data['value'],
                        'date': latest_data['date'],
                        'unit': result['indicator_config']['unit'],
                        'description': result['indicator_config']['description']
                    }
                else:
                    summary[indicator_name] = {
                        'error': result.get('error', '数据获取失败')
                    }
                    
            except Exception as e:
                logger.error(f"获取{indicator_name}最新数据失败: {e}")
                summary[indicator_name] = {
                    'error': str(e)
                }
        
        return {
            'country': 'Japan',
            'summary_date': datetime.now().isoformat(),
            'indicators_count': len(all_indicators),
            'data': summary
        }
    
    def _calculate_statistics(self, observations: List[Dict]) -> Dict[str, Any]:
        """
        计算观测数据的统计信息
        
        Args:
            observations: 观测数据列表
            
        Returns:
            统计信息字典
        """
        if not observations:
            return {}
        
        try:
            values = []
            for obs in observations:
                try:
                    value = float(obs['value'])
                    values.append(value)
                except (ValueError, TypeError):
                    continue
            
            if not values:
                return {}
            
            # 基础统计
            stats = {
                'count': len(values),
                'latest_value': values[0] if values else None,
                'min_value': min(values),
                'max_value': max(values),
                'average': sum(values) / len(values),
                'latest_date': observations[0]['date'] if observations else None,
                'earliest_date': observations[-1]['date'] if observations else None
            }
            
            # 年同比变化
            yoy_change = self._calculate_yoy_change_local(observations)
            if yoy_change is not None:
                stats['yoy_change_percent'] = yoy_change
            
            return stats
            
        except Exception as e:
            logger.warning(f"统计计算失败: {e}")
            return {}
    
    def _calculate_yoy_change_local(self, observations: List[Dict]) -> Optional[float]:
        """
        计算年同比变化（本地实现）
        
        Args:
            observations: 观测数据列表 (按日期降序)
            
        Returns:
            年同比变化百分比或None
        """
        if len(observations) < 13:  # 需要至少13个月的数据
            return None
        
        try:
            current_value = float(observations[0]['value'])
            year_ago_value = float(observations[12]['value'])
            
            if year_ago_value == 0:
                return None
            
            yoy_change = ((current_value - year_ago_value) / year_ago_value) * 100
            return round(yoy_change, 2)
            
        except (ValueError, IndexError, ZeroDivisionError) as e:
            logger.warning(f"无法计算年同比变化: {e}")
            return None
    
    def validate_connection(self) -> Dict[str, Any]:
        """
        验证API连接和配置
        
        Returns:
            验证结果
        """
        logger.info("验证日本FRED API连接")
        
        try:
            # 测试获取一个简单的指标
            test_result = self.get_indicator_data('cpi', limit=1)
            
            return {
                'connection_valid': test_result.get('success', False),
                'api_key_valid': bool(self.api_key),
                'config_valid': True,
                'country_config': self.get_country_specific_config(),
                'test_result': test_result
            }
            
        except Exception as e:
            logger.error(f"连接验证失败: {e}")
            return {
                'connection_valid': False,
                'error': str(e)
            }
    
    # 实现抽象方法
    def save_series_info(self, series_id: str, series_info: Dict) -> bool:
        """
        保存系列信息到数据库
        
        Args:
            series_id: FRED系列ID
            series_info: 系列信息
            
        Returns:
            保存是否成功
        """
        try:
            # 这里应该保存到数据库，但目前只记录日志
            logger.info(f"保存系列信息: {series_id} - {series_info.get('title', 'N/A')}")
            return True
        except Exception as e:
            logger.error(f"保存系列信息失败: {e}")
            return False
    
    def save_observations(self, series_id: str, observations: List[Dict]) -> int:
        """
        保存观测数据到数据库
        
        Args:
            series_id: FRED系列ID
            observations: 观测数据列表
            
        Returns:
            保存的记录数
        """
        try:
            # 这里应该保存到数据库，但目前只记录日志
            logger.info(f"保存观测数据: {series_id} - {len(observations)}条记录")
            return len(observations)
        except Exception as e:
            logger.error(f"保存观测数据失败: {e}")
            return 0
    
    def get_indicator_mapping(self) -> Dict[str, str]:
        """
        获取指标映射
        
        Returns:
            指标名称到FRED系列ID的映射
        """
        mapping = {}
        for indicator_name, config in self.config_manager.JAPAN_INDICATORS.items():
            mapping[indicator_name] = config['series_id']
        
        return mapping
