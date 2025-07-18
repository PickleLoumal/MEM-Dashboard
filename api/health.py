import json
import os
from datetime import datetime

def handler(request):
    """Vercel serverless function for health check"""
    
    response_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'MEM Dashboard API',
        'environment': 'production',
        'database_configured': bool(os.getenv('DATABASE_URL')),
        'version': '1.0.0'
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
