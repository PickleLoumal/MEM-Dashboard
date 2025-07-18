"""
BEA指标通用处理器
统一处理所有BEA指标的数据格式化、计算和响应生成
"""

from django.utils import timezone
from .models import BeaIndicator
from .dynamic_config import DynamicBeaConfigManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BeaIndicatorProcessor:
    """BEA指标通用处理器"""
    
    @classmethod
    def process_indicator_data(cls, series_id, include_quarterly=True):
        """
        处理指标数据，返回标准化的API响应格式
        
        Args:
            series_id: 指标系列ID
            include_quarterly: 是否包含季度数据
            
        Returns:
            dict: 标准化的API响应数据
        """
        try:
            # 获取指标配置
            config = DynamicBeaConfigManager.get_indicator_config(series_id)
            if not config:
                return cls._get_fallback_response(series_id, "Indicator config not found")
            
            # 获取最新数据
            latest_data = BeaIndicator.get_latest_by_series(series_id)
            
            if latest_data:
                # 使用实际数据库数据
                response_data = cls._format_database_data(latest_data, config, include_quarterly)
            else:
                # 使用配置中的fallback数据
                response_data = cls._format_fallback_data(config)
            
            return {
                'success': True,
                'data': response_data,
                'last_updated': timezone.now().isoformat(),
                'source': 'PostgreSQL Database (Django DRF)' if latest_data else 'Fallback Data'
            }
            
        except Exception as e:
            logger.error(f"Error processing indicator {series_id}: {e}")
            return cls._get_error_response(series_id, str(e))
    
    @classmethod
    def process_all_indicators(cls):
        """
        处理所有激活的指标数据
        
        Returns:
            dict: 包含所有指标数据的响应
        """
        try:
            all_configs = DynamicBeaConfigManager.get_all_indicators()
            all_data = {}
            processed_count = 0
            
            for series_id, config in all_configs.items():
                try:
                    indicator_response = cls.process_indicator_data(series_id, include_quarterly=False)
                    if indicator_response['success']:
                        all_data[config['api_endpoint']] = indicator_response['data']
                        processed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing indicator {series_id}: {e}")
                    # 继续处理其他指标
                    continue
            
            return {
                'success': True,
                'data': all_data,
                'indicators_count': processed_count,
                'source': 'PostgreSQL Database (Django DRF)',
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing all indicators: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'indicators_count': 0
            }
    
    @classmethod
    def process_category_indicators(cls, category):
        """
        处理指定类别的指标数据
        
        Args:
            category: 指标类别
            
        Returns:
            dict: 该类别的所有指标数据
        """
        try:
            category_configs = DynamicBeaConfigManager.get_configs_by_category(category)
            category_data = {}
            processed_count = 0
            
            for series_id, config in category_configs.items():
                try:
                    indicator_response = cls.process_indicator_data(series_id, include_quarterly=False)
                    if indicator_response['success']:
                        category_data[config['api_endpoint']] = indicator_response['data']
                        processed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing indicator {series_id} in category {category}: {e}")
                    continue
            
            return {
                'success': True,
                'data': category_data,
                'category': category,
                'indicators_count': processed_count,
                'source': 'PostgreSQL Database (Django DRF)',
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing category {category}: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': category,
                'data': {},
                'indicators_count': 0
            }
    
    @classmethod
    def get_available_indicators(cls):
        """
        获取所有可用指标的列表
        
        Returns:
            dict: 可用指标列表
        """
        try:
            all_configs = DynamicBeaConfigManager.get_all_indicators()
            indicators_list = []
            
            for series_id, config in all_configs.items():
                indicators_list.append({
                    'series_id': series_id,
                    'name': config['name'],
                    'description': config.get('description', ''),
                    'category': config['category'],
                    'api_endpoint': config['api_endpoint'],
                    'units': config.get('units', ''),
                    'priority': config.get('priority', 999)
                })
            
            # 按优先级排序
            indicators_list.sort(key=lambda x: x['priority'])
            
            return {
                'success': True,
                'data': indicators_list,
                'count': len(indicators_list),
                'source': 'PostgreSQL Database (Django DRF)'
            }
            
        except Exception as e:
            logger.error(f"Error getting available indicators: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'count': 0
            }
    
    @classmethod
    def _format_database_data(cls, latest_data, config, include_quarterly=True):
        """格式化数据库中的实际数据"""
        # 计算同比变化
        yoy_change = latest_data.get_yoy_change()
        
        # 格式化日期
        formatted_date = cls._format_date(latest_data.time_period)
        
        response_data = {
            'value': float(latest_data.value),
            'date': latest_data.date.isoformat(),
            'formatted_date': formatted_date,
            'yoy_change': round(yoy_change, 2) if yoy_change is not None else None,
            'series_id': latest_data.series_id,
            'series_name': config['name'],
            'description': config.get('description', ''),
            'units': config.get('units', ''),
            'category': config['category'],
            'source': 'BEA API'
        }
        
        # 包含季度数据（如果请求）
        if include_quarterly:
            quarterly_data = BeaIndicator.get_quarterly_data(latest_data.series_id)
            response_data['quarterly_data'] = [
                {
                    'TimePeriod': item.time_period,
                    'DataValue': str(item.value),
                    'date': item.date.isoformat()
                }
                for item in quarterly_data
            ]
        
        return response_data
    
    @classmethod
    def _format_fallback_data(cls, config):
        """格式化fallback数据"""
        return {
            'value': config.get('fallback_value', 0),
            'date': '2025-01-01',
            'formatted_date': 'Q1 2025',
            'yoy_change': None,
            'series_id': config.get('series_id', ''),
            'series_name': config['name'],
            'description': config.get('description', ''),
            'units': config.get('units', ''),
            'category': config['category'],
            'source': 'Fallback Data'
        }
    
    @classmethod
    def _format_date(cls, time_period):
        """格式化时间周期为可读格式"""
        try:
            if 'Q' in time_period:
                year = time_period[:4]
                quarter = time_period[5:]
                return f"{quarter} {year}"
            elif len(time_period) == 4:  # 年度数据
                return time_period
            else:
                return time_period
        except:
            return time_period
    
    @classmethod
    def _get_fallback_response(cls, series_id, message):
        """获取fallback响应"""
        return {
            'success': False,
            'error': message,
            'data': {
                'value': 0,
                'date': '2025-01-01',
                'formatted_date': 'Q1 2025',
                'yoy_change': None,
                'series_id': series_id,
                'source': 'Error Fallback'
            }
        }
    
    @classmethod
    def _get_error_response(cls, series_id, error_message):
        """获取错误响应"""
        return {
            'success': False,
            'error': error_message,
            'series_id': series_id,
            'timestamp': timezone.now().isoformat()
        }


class BeaCompatibilityProcessor:
    """BEA兼容性处理器 - 保持与Flask API的兼容性"""
    
    @classmethod
    def get_motor_vehicles_data(cls):
        """获取Motor Vehicles数据（兼容Flask格式）"""
        return BeaIndicatorProcessor.process_indicator_data('MOTOR_VEHICLES', include_quarterly=True)
    
    @classmethod
    def get_recreational_goods_data(cls):
        """获取Recreational Goods数据（兼容Flask格式）"""
        return BeaIndicatorProcessor.process_indicator_data('RECREATIONAL_GOODS', include_quarterly=False)
    
    @classmethod
    def get_bea_status(cls):
        """获取BEA系统状态"""
        try:
            stats = DynamicBeaConfigManager.get_statistics()
            
            # 获取最新更新时间
            latest_indicator = BeaIndicator.objects.first()
            latest_update = latest_indicator.updated_at.isoformat() if latest_indicator else None
            
            # 获取可用系列
            available_series = list(DynamicBeaConfigManager.get_all_indicators().keys())
            
            return {
                'success': True,
                'data': {
                    'total_indicators': BeaIndicator.objects.count(),
                    'total_series': len(available_series),
                    'latest_update': latest_update,
                    'available_series': available_series[:10],  # 显示前10个
                    'active_configs': stats.get('active_indicators', 0),
                    'categories': stats.get('categories', [])
                },
                'service': 'BEA Django API',
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting BEA status: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': 'BEA Django API',
                'timestamp': timezone.now().isoformat()
            }