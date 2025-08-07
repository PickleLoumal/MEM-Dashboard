"""
FRED Base Data Fetcher - 通用基础数据获取器
为美国和日本FRED应用提供共同的数据获取基础功能
"""

import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction
from .constants import FRED_BASE_URL, DEFAULT_TIMEOUT, MAX_RETRIES
from .utils import validate_series_id, clean_numeric_value

logger = logging.getLogger(__name__)


class BaseFredDataFetcher(ABC):
    """FRED数据获取器基类 - 提供通用的数据获取逻辑"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化数据获取器"""
        self.api_key = api_key or getattr(settings, 'FRED_API_KEY', None)
        self.base_url = FRED_BASE_URL
        self.timeout = DEFAULT_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.session = requests.Session()
        
        # 设置通用请求头
        self.session.headers.update({
            'User-Agent': 'MEM-Dashboard/1.0',
            'Accept': 'application/json'
        })

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.session.close()

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """执行HTTP请求，包含重试逻辑"""
        if not self.api_key:
            logger.error("FRED API key not configured")
            return None

        # 添加API密钥
        params['api_key'] = self.api_key
        params['file_type'] = 'json'
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Making request to {url}, attempt {attempt + 1}")
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"HTTP {response.status_code}: {response.text}")
                    return None
                    
            except requests.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(1)  # Brief pause before retry
        
        return None

    def get_series_info(self, series_id: str) -> Optional[Dict]:
        """获取系列信息"""
        if not validate_series_id(series_id):
            logger.error(f"Invalid series ID: {series_id}")
            return None

        params = {
            'series_id': series_id
        }
        
        data = self._make_request('series', params)
        if data and 'seriess' in data and data['seriess']:
            return data['seriess'][0]
        return None

    def get_series_observations(self, series_id: str, start_date: Optional[str] = None, 
                              end_date: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """获取系列观测数据"""
        if not validate_series_id(series_id):
            logger.error(f"Invalid series ID: {series_id}")
            return []

        params = {
            'series_id': series_id,
            'sort_order': 'desc'
        }
        
        if start_date:
            params['observation_start'] = start_date
        if end_date:
            params['observation_end'] = end_date
        if limit:
            params['limit'] = str(limit)

        data = self._make_request('series/observations', params)
        if data and 'observations' in data:
            return data['observations']
        return []

    def get_latest_observation(self, series_id: str) -> Optional[Dict]:
        """获取最新观测数据"""
        observations = self.get_series_observations(series_id, limit=1)
        return observations[0] if observations else None

    def fetch_and_clean_data(self, series_id: str, limit: Optional[int] = None) -> List[Dict]:
        """获取并清理数据"""
        observations = self.get_series_observations(series_id, limit=limit)
        cleaned_data = []
        
        for obs in observations:
            if obs.get('value', '.') == '.':  # FRED uses '.' for missing values
                continue
                
            try:
                cleaned_value = clean_numeric_value(obs['value'])
                if cleaned_value is not None:
                    cleaned_data.append({
                        'date': obs['date'],
                        'value': cleaned_value,
                        'realtime_start': obs.get('realtime_start'),
                        'realtime_end': obs.get('realtime_end')
                    })
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid observation for {series_id}: {e}")
                continue
        
        return cleaned_data

    def calculate_period_change(self, current_value: float, previous_value: float) -> Optional[float]:
        """计算期间变化率"""
        if previous_value == 0:
            return None
        try:
            return ((current_value - previous_value) / previous_value) * 100
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def get_date_range_params(self, days_back: int = 365) -> Dict[str, str]:
        """生成日期范围参数"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return {
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': end_date.strftime('%Y-%m-%d')
        }

    def validate_response_data(self, data: Dict, required_fields: List[str]) -> bool:
        """验证响应数据完整性"""
        if not data:
            return False
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        
        return True

    @abstractmethod
    def save_series_info(self, series_id: str, series_info: Dict) -> bool:
        """保存系列信息到数据库 - 子类必须实现"""
        pass

    @abstractmethod
    def save_observations(self, series_id: str, observations: List[Dict]) -> int:
        """保存观测数据到数据库 - 子类必须实现"""
        pass

    @abstractmethod
    def get_indicator_mapping(self) -> Dict[str, str]:
        """获取指标映射 - 子类必须实现"""
        pass

    def fetch_indicator_data(self, indicator_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """获取指标数据的通用方法"""
        mapping = self.get_indicator_mapping()
        series_id = mapping.get(indicator_name.lower())
        
        if not series_id:
            logger.error(f"Unknown indicator: {indicator_name}")
            return {
                'success': False,
                'error': f'Unknown indicator: {indicator_name}',
                'supported_indicators': list(mapping.keys())
            }

        try:
            # 获取最新数据
            latest_obs = self.get_latest_observation(series_id)
            if not latest_obs:
                logger.error(f"No data found for series: {series_id}")
                return {
                    'success': False,
                    'error': f'No data available for {indicator_name}',
                    'series_id': series_id
                }

            # 获取系列信息
            series_info = self.get_series_info(series_id)
            
            # 构建响应
            result = {
                'success': True,
                'series_id': series_id,
                'indicator_name': indicator_name,
                'data': {
                    'value': clean_numeric_value(latest_obs['value']),
                    'date': latest_obs['date'],
                    'formatted_date': self._format_display_date(latest_obs['date']),
                    'unit': series_info.get('units', '') if series_info else '',
                    'frequency': series_info.get('frequency_short', '') if series_info else '',
                    'source': 'FRED'
                },
                'timestamp': datetime.now().isoformat()
            }

            # 获取更多数据用于计算变化率
            if limit and limit > 1:
                observations = self.get_series_observations(series_id, limit=limit)
                result['observations'] = [
                    {
                        'date': obs['date'],
                        'value': clean_numeric_value(obs['value']),
                        'formatted_date': self._format_display_date(obs['date'])
                    }
                    for obs in observations if obs.get('value', '.') != '.'
                ]

            return result

        except Exception as e:
            logger.error(f"Error fetching {indicator_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'series_id': series_id,
                'timestamp': datetime.now().isoformat()
            }

    def _format_display_date(self, date_str: str) -> str:
        """格式化显示日期"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%b %Y')
        except ValueError:
            return date_str

    def bulk_fetch_indicators(self, indicator_names: List[str]) -> Dict[str, Any]:
        """批量获取多个指标数据"""
        results = {}
        mapping = self.get_indicator_mapping()
        
        for indicator in indicator_names:
            if indicator.lower() in mapping:
                results[indicator] = self.fetch_indicator_data(indicator)
            else:
                results[indicator] = {
                    'success': False,
                    'error': f'Unknown indicator: {indicator}'
                }
        
        return {
            'success': True,
            'indicators': results,
            'total_requested': len(indicator_names),
            'total_found': len([r for r in results.values() if r.get('success')]),
            'timestamp': datetime.now().isoformat()
        }
