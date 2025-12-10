import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# Django Model & Service Imports
from csi300.models import CSI300Company, CSI300InvestmentSummary
from csi300.services import (
    generate_company_summary,
    parse_business_overview_to_json,
    safe_decimal,
    extract_ai_content_sections,
)
from csi300.services.parser import SECTION_PATTERNS

# Fixtures
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_company(db):
    """创建一个测试用的 CSI300Company"""
    return CSI300Company.objects.create(
        name="测试公司",
        ticker="000001.SZ",
        industry="科技",
        im_sector="信息技术"
    )

@pytest.fixture
def generate_url():
    return reverse('csi300:generate_investment_summary')

# ==========================================
# 1. API 端点测试
# ==========================================

@pytest.mark.django_db
def test_api_endpoint_exists(api_client, generate_url):
    """测试 API 端点存在"""
    response = api_client.post(generate_url, {})
    assert response.status_code != status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_missing_company_id(api_client, generate_url):
    """测试缺少 company_id 参数"""
    response = api_client.post(generate_url, {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'company_id' in response.data['message'].lower()

@pytest.mark.django_db
def test_invalid_company_id_type(api_client, generate_url):
    """测试无效的 company_id 类型"""
    response = api_client.post(generate_url, {'company_id': 'invalid'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'integer' in response.data['message'].lower()

@pytest.mark.django_db
def test_nonexistent_company(api_client, generate_url):
    """测试不存在的公司 ID"""
    response = api_client.post(generate_url, {'company_id': 99999})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert '不存在' in response.data['message']

@pytest.mark.django_db
@patch('csi300.views.generate_company_summary')
def test_successful_generation_api(mock_generate, api_client, generate_url, test_company):
    """测试 API 调用成功生成摘要"""
    mock_generate.return_value = {
        'status': 'success',
        'message': 'Created',
        'data': {
            'company_id': test_company.id,
            'company_name': test_company.name,
            'ticker': test_company.ticker,
            'duration': 10.5
        }
    }
    
    response = api_client.post(generate_url, {'company_id': test_company.id})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert 'data' in response.data

@pytest.mark.django_db
@patch('csi300.views.generate_company_summary')
def test_generation_failure_api(mock_generate, api_client, generate_url, test_company):
    """测试 API 处理生成失败的情况"""
    mock_generate.return_value = {
        'status': 'error',
        'message': 'AI Generation Failed',
        'data': None
    }
    
    response = api_client.post(generate_url, {'company_id': test_company.id})
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data['status'] == 'error'

# ==========================================
# 2. 业务逻辑与解析测试
# ==========================================

def test_parse_business_overview_empty():
    """测试空文本解析"""
    result = parse_business_overview_to_json("", "Test Company")
    import json
    data = json.loads(result)
    assert data['parsed'] is None

def test_parse_business_overview_json_block():
    """测试 AI 生成的 JSON 块解析"""
    text = '''
    Some narrative text here.
    
    ```business_overview_data
    {
        "fiscal_year": "2024",
        "key_metrics": {
            "total_revenue": "100B CNY",
            "operating_income": "10B CNY"
        },
        "divisions": [
            {"name": "Division A", "sales_pct": "60%", "gross_margin": "30%"}
        ]
    }
    ```
    '''
    
    result = parse_business_overview_to_json(text, "Test Company")
    import json
    data = json.loads(result)
    
    assert data['parsed'] is not None
    assert data['parsed']['fiscal_year'] == '2024'
    assert 'total_revenue' in data['parsed']['key_metrics']
    assert len(data['parsed']['divisions']) == 1
    assert data['parsed']['divisions'][0]['name'] == "Division A"

def test_parse_business_overview_fallback():
    """测试正则回退解析"""
    text = '''
    Key financials for FY2024: sales 100B CNY, operating income 10B CNY, 
    margins ~10%.
    '''
    
    result = parse_business_overview_to_json(text, "Test Company")
    import json
    data = json.loads(result)
    
    # 即使解析不完美，也应返回 parsed 对象而不是 None
    assert data['parsed'] is not None

def test_safe_decimal():
    """测试 Decimal 转换工具函数"""
    assert safe_decimal(10.5) == Decimal('10.5')
    assert safe_decimal('100') == Decimal('100')
    assert safe_decimal(None) == Decimal('0')
    assert safe_decimal('invalid') == Decimal('0')

def test_extract_ai_content_sections():
    """测试 Markdown Section 提取"""
    content = '''
    # Business Overview
    This is the business overview content.
    
    ## Key Financials and Valuation
    Financial metrics here.
    
    ### Recommended Action
    Buy this stock because...
    '''
    
    sections = extract_ai_content_sections(content)
    
    assert 'business_overview' in sections
    assert 'key_financials' in sections
    assert 'recommended_action' in sections
    assert 'overview content' in sections['business_overview'].lower()

def test_section_regex_anchoring():
    """测试正则表达式锚点 (防止误匹配正文)"""
    # 模拟正文中包含 "Key Financials" 文本的情况
    text_with_inline = '''
    Business Overview text here.
    Key financials for FY2024 show revenue of 100B.
    More text here.
    
    ## Key Financials and Valuation
    This is the actual section.
    '''
    
    match = SECTION_PATTERNS['key_financials'].search(text_with_inline)
    assert match is not None
    
    matched_text = match.group(0)
    # 确保匹配的是标题行
    assert '## Key Financials' in matched_text
    # 确保没有匹配到第一段的正文
    assert 'Key financials for FY2024' not in matched_text.split('\n')[0]

# ==========================================
# 3. Service 层集成测试 (Mock 外部依赖)
# ==========================================

@pytest.mark.django_db
@patch('csi300.services.generator.Client')
@patch('csi300.services.utils.yf.Ticker')
def test_service_generate_success(mock_yf, mock_client, test_company):
    """测试服务层生成逻辑 (Mock AI 和 Yahoo)"""
    # Mock Yahoo Finance
    mock_ticker = MagicMock()
    mock_ticker.info = {
        'regularMarketPreviousClose': 100.0,
        'marketCap': 1000000000000,
        'currency': 'CNY'
    }
    mock_yf.return_value = mock_ticker
    
    # Mock XAI Client
    mock_client_instance = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    
    mock_response.content = '''
    # Business Overview
    Test company operates in technology sector.
    
    ```business_overview_data
    {
        "fiscal_year": "2024",
        "key_metrics": {"total_revenue": "100B CNY"},
        "divisions": []
    }
    ```
    
    ## Key Financials and Valuation
    Strong financial performance.
    
    ### Recommended Action
    Hold
    '''
    mock_chat.sample.return_value = mock_response
    mock_client_instance.chat.create.return_value = mock_chat
    mock_client.return_value = mock_client_instance
    
    # 调用服务
    result = generate_company_summary(test_company.id)
    
    assert result['status'] == 'success'
    assert result['data']['company_id'] == test_company.id
    
    # 验证数据库记录
    summary = CSI300InvestmentSummary.objects.filter(company=test_company).first()
    assert summary is not None
    assert summary.recommended_action == 'Hold'

@pytest.mark.django_db
def test_service_nonexistent_company():
    """测试服务层处理不存在的公司"""
    result = generate_company_summary(99999)
    assert result['status'] == 'error'
    assert '不存在' in result['message']

@pytest.mark.django_db
@patch('csi300.services.generator.Client')
def test_service_ai_failure(mock_client, test_company):
    """测试服务层处理 AI 调用失败"""
    mock_client_instance = MagicMock()
    mock_chat = MagicMock()
    # 模拟超时或错误
    mock_chat.sample.side_effect = Exception("AI Service Unavailable")
    mock_client_instance.chat.create.return_value = mock_chat
    mock_client.return_value = mock_client_instance
    
    result = generate_company_summary(test_company.id)
    
    assert result['status'] == 'error'
    assert 'Error' in result['message']

