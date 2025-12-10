"""
FRED US API Helper Methods

辅助方法 - 通用数据获取和错误响应处理。
"""

from typing import Any, Dict, Optional
from datetime import datetime
import logging

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.db.models.query import QuerySet

from .models import FredUsIndicator
from .serializers import FredUsErrorResponseSerializer

logger = logging.getLogger(__name__)


class FredUsHelperMixin:
    """
    FRED US 辅助方法 Mixin
    
    提供通用的数据获取和错误响应处理方法。
    """
    
    def _get_specific_indicator(self, series_id: str, request: Request) -> Response:
        """
        获取特定指标数据的通用方法
        
        返回前端期望的简单格式，包含最新值、历史观测数据和元信息。
        
        Args:
            series_id: FRED 系列 ID (如 'UNRATE', 'CPIAUCSL')
            request: DRF 请求对象
            
        Returns:
            Response: 指标数据响应
        """
        try:
            limit: int = int(request.query_params.get('limit', 100))
            
            # 从数据库获取数据
            base_queryset: QuerySet[FredUsIndicator] = FredUsIndicator.objects.filter(
                series_id=series_id
            ).order_by('-date')
            
            if not base_queryset.exists():
                # 如果数据库中没有数据，尝试从API获取
                fetcher = self.get_data_fetcher()
                if fetcher:
                    result = fetcher.fetch_indicator_data(series_id, limit=limit)
                    if result.get('success'):
                        base_queryset = FredUsIndicator.objects.filter(
                            series_id=series_id
                        ).order_by('-date')
            
            if base_queryset.exists():
                all_indicators = list(base_queryset)
                indicators = all_indicators[:limit]
                latest = indicators[0] if indicators else None
                
                if latest and latest.date and latest.value is not None:
                    # 计算同比变化
                    yoy_change = self._calculate_yoy_change(latest, all_indicators)
                    
                    # 格式化日期
                    formatted_date = latest.date.strftime('%b %Y')
                    
                    response_data = {
                        'success': True,
                        'data': {
                            'value': float(latest.value),
                            'date': latest.date.isoformat(),
                            'formatted_date': formatted_date,
                            'yoy_change': round(yoy_change, 2) if yoy_change is not None else None,
                            'series_id': series_id,
                            'indicator_name': latest.indicator_name or '',
                            'unit': latest.unit or '',
                            'source': 'PostgreSQL Database (Django DRF)',
                            'last_updated': latest.updated_at.isoformat() if latest.updated_at else None
                        },
                        'series_id': series_id,
                        'count': len(indicators),
                        'limit': limit,
                        'country': 'US'
                    }
                    
                    # 包含observations用于图表
                    observations = []
                    for indicator in indicators:
                        if indicator.date and indicator.value is not None:
                            observations.append({
                                'date': indicator.date.isoformat(),
                                'value': str(indicator.value),
                                'realtime_start': indicator.date.isoformat(),
                                'realtime_end': indicator.date.isoformat()
                            })
                    response_data['observations'] = observations
                    
                    return Response(response_data)
                else:
                    return self._error_response(f"Invalid data for {series_id}")
            else:
                return self._error_response(f"No data available for {series_id}")
                
        except Exception as e:
            logger.error(f"获取指标 {series_id} 失败: {e}")
            return self._error_response(f"Failed to get indicator {series_id}: {str(e)}")

    def _calculate_yoy_change(self, latest, all_indicators) -> Optional[float]:
        """计算同比变化"""
        if len(all_indicators) <= 1:
            return None
        
        try:
            year_ago = latest.date.replace(year=latest.date.year - 1)
            year_ago_indicator = None
            for indicator in all_indicators:
                if indicator.date <= year_ago:
                    year_ago_indicator = indicator
                    break
            
            if year_ago_indicator and year_ago_indicator.value:
                current_val = float(latest.value)
                year_ago_val = float(year_ago_indicator.value)
                return ((current_val - year_ago_val) / year_ago_val) * 100
        except (ValueError, AttributeError):
            pass
        
        return None

    def _error_response(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> Response:
        """
        生成标准化的错误响应
        
        Args:
            message: 错误消息
            details: 额外的错误详情
            
        Returns:
            Response: 错误响应 (HTTP 400)
        """
        error_data: Dict[str, Any] = {
            'success': False,
            'error': message,
            'country': 'US',
            'details': details if details is not None else {},
            'timestamp': datetime.now()
        }
        return Response(
            FredUsErrorResponseSerializer(error_data).data,
            status=status.HTTP_400_BAD_REQUEST
        )


__all__ = ['FredUsHelperMixin']

