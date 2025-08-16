#!/usr/bin/env python3
"""
验证Government Deficit Financing & Corporate Debts指标的FRED数据可用性
基于资深经济分析师视角的综合指标体系
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta

# FRED API配置
FRED_API_KEY = "1cdac6b8c1173f83a10444d17e73b32e"  # 从实际环境获取
BASE_URL = "https://api.stlouisfed.org/fred"

def test_fred_indicator(series_id, description):
    """测试单个FRED指标的可用性"""
    print(f"\n=== 测试指标: {series_id} ({description}) ===")
    
    # 获取系列信息
    series_url = f"{BASE_URL}/series"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json'
    }
    
    try:
        # 构建URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{series_url}?{query_string}"
        
        # 发送请求获取系列信息
        with urllib.request.urlopen(full_url) as response:
            series_data = json.loads(response.read().decode())
        
        if 'seriess' in series_data and len(series_data['seriess']) > 0:
            series_info = series_data['seriess'][0]
            print(f"✅ 系列ID: {series_info['id']}")
            print(f"   标题: {series_info['title']}")
            print(f"   单位: {series_info.get('units', 'N/A')}")
            print(f"   频率: {series_info.get('frequency', 'N/A')}")
            print(f"   开始日期: {series_info.get('observation_start', 'N/A')}")
            print(f"   结束日期: {series_info.get('observation_end', 'N/A')}")
            
            # 获取最新数据点
            obs_url = f"{BASE_URL}/series/observations"
            obs_params = {
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 5,
                'sort_order': 'desc'
            }
            
            obs_query = urllib.parse.urlencode(obs_params)
            obs_full_url = f"{obs_url}?{obs_query}"
            
            with urllib.request.urlopen(obs_full_url) as obs_response:
                obs_data = json.loads(obs_response.read().decode())
            
            if 'observations' in obs_data and len(obs_data['observations']) > 0:
                latest_obs = obs_data['observations'][0]
                print(f"   最新值: {latest_obs['value']} ({latest_obs['date']})")
                return True
            else:
                print("⚠️  无可用观测数据")
                return False
        else:
            print(f"❌ 未找到系列: {series_id}")
            return False
            
    except urllib.error.URLError as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return False

def main():
    print("=== Government Deficit Financing & Corporate Debts 指标验证 ===")
    
    # 定义要验证的指标列表 - 确保至少8个
    # 基于资深经济分析师视角的综合指标体系
    indicators = [
        # 核心政府债务指标
        ('GFDEBTN', 'Federal Debt: Total Public Debt'),
        ('GFDEGDQ188S', 'Federal Debt as Percent of GDP'),
        ('MTSDS133FMS', 'Federal Surplus or Deficit'),
        ('W006RC1Q027SBEA', 'Federal Tax Receipts'),
        
        # 补充的企业债务与融资指标 - 经济分析师视角
        ('NCBDBIQ027S', 'Nonfinancial Corporate Business Debt Securities'),  # 非金融企业债券
        ('BCNSDODNS', 'Corporate and Foreign Bonds Outstanding'),  # 企业与外国债券余额
        ('TBSDODNS', 'Total Debt Securities Outstanding'),  # 债务证券总余额
        ('FGSDODNS', 'Federal Government Debt Securities Outstanding')  # 联邦政府债务证券余额
    ]
    
    valid_indicators = []
    
    print("\n" + "="*70)
    print("验证指定的8个核心指标")
    print("="*70)
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
    
    print("\n" + "="*70)
    print("验证结果汇总")
    print("="*70)
    print(f"有效指标数量: {len(valid_indicators)}")
    
    if len(valid_indicators) >= 8:
        print("✅ 满足8个指标要求")
        print("\n📊 最终指标列表:")
        for i, (series_id, description) in enumerate(valid_indicators, 1):
            print(f"  {i}. {series_id}: {description}")
    else:
        print(f"⚠️  仅有{len(valid_indicators)}个有效指标，需要补充")
        
        # 如果指标不足，建议备选指标
        backup_indicators = [
            ('BOGZ1FL104104005Q', 'Nonfinancial Corporate Business Credit Market Instruments'),
            ('BOGZ1FL144104005Q', 'Nonfinancial Noncorporate Business Credit Market Instruments'),
            ('CMDEBT', 'Corporate and Municipal Debt Outstanding'),
            ('ASTDSL', 'Assets: Total Debt Securities: Level')
        ]
        
        print("\n🔄 测试备选指标:")
        for series_id, description in backup_indicators:
            if len(valid_indicators) >= 8:
                break
            if test_fred_indicator(series_id, description):
                valid_indicators.append((series_id, description))
    
    print(f"\n✅ 最终确认指标数量: {len(valid_indicators)}")
    
    # 生成配置代码
    print("\n" + "="*70)
    print("Django视图配置代码生成:")
    print("="*70)
    
    view_names = [
        'federal_debt_total', 'federal_debt_gdp_ratio', 'federal_surplus_deficit', 'federal_tax_receipts',
        'corporate_debt_securities', 'corporate_foreign_bonds', 'total_debt_securities', 'federal_govt_debt_securities'
    ]
    
    for i, (series_id, description) in enumerate(valid_indicators[:8]):
        view_name = view_names[i] if i < len(view_names) else f'indicator_{i+1}'
        print(f"""
@action(detail=False, methods=['get'], url_path='{view_name.replace('_', '-')}')
def {view_name}(self, request):
    \"\"\"{description}\"\"\"
    return self._get_specific_indicator(request, '{series_id}')""")

if __name__ == "__main__":
    main()
