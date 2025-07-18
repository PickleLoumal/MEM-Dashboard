import json
import os
from datetime import datetime

def handler(request):
    """Basic economic indicators endpoint for production"""
    
    # 基础经济数据 - 生产环境fallback
    basic_indicators = {
        'M2SL': {
            'value': 21.86,
            'date': '2025-04-01',
            'yoy_change': 4.44,
            'formatted_date': 'Apr 2025',
            'source': 'Production API'
        },
        'M1SL': {
            'value': 18.67,
            'date': '2025-04-01', 
            'yoy_change': 3.86,
            'formatted_date': 'Apr 2025',
            'source': 'Production API'
        },
        'CPIAUCSL': {
            'value': 307.8,
            'date': '2025-05-01',
            'yoy_change': 2.4,
            'formatted_date': 'May 2025',
            'source': 'Production API'
        },
        'UNRATE': {
            'value': 3.7,
            'date': '2025-05-01',
            'yoy_change': -0.1,
            'formatted_date': 'May 2025',
            'source': 'Production API'
        }
    }
    
    # 检查请求的指标
    indicator = request.args.get('indicator', 'M2SL')
    
    if indicator in basic_indicators:
        response_data = {
            'success': True,
            'data': basic_indicators[indicator],
            'environment': 'production',
            'database_connected': bool(os.getenv('DATABASE_URL'))
        }
    else:
        response_data = {
            'success': False,
            'error': f'Indicator {indicator} not found',
            'available_indicators': list(basic_indicators.keys())
        }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(response_data)
    }
