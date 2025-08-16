#!/usr/bin/env python3
"""
验证Consumer and Household Debt指标的FRED数据可用性
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta

# FRED API配置
FRED_API_KEY = "1cdac6b8c1173f83a10444d17e73b32e"  # 从.env文件中获取
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
        
        with urllib.request.urlopen(full_url) as response:
            series_data = json.loads(response.read().decode())
        
        if 'seriess' in series_data and len(series_data['seriess']) > 0:
            series_info = series_data['seriess'][0]
            print(f"✅ 系列ID: {series_info['id']}")
            print(f"   标题: {series_info['title']}")
            print(f"   单位: {series_info['units']}")
            print(f"   频率: {series_info['frequency']}")
            print(f"   开始日期: {series_info['observation_start']}")
            print(f"   结束日期: {series_info['observation_end']}")
            print(f"   最后更新: {series_info['last_updated']}")
            
            # 获取最新数据
            obs_url = f"{BASE_URL}/series/observations"
            obs_params = {
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 5,
                'sort_order': 'desc'
            }
            
            obs_query_string = urllib.parse.urlencode(obs_params)
            obs_full_url = f"{obs_url}?{obs_query_string}"
            
            with urllib.request.urlopen(obs_full_url) as obs_response:
                obs_data = json.loads(obs_response.read().decode())
            
            if 'observations' in obs_data and len(obs_data['observations']) > 0:
                latest_obs = obs_data['observations'][0]
                print(f"   最新值: {latest_obs['value']} ({latest_obs['date']})")
                return True
            else:
                print(f"⚠️  无观测数据")
                return False
                
        else:
            print(f"❌ 系列不存在")
            return False
            
    except urllib.error.URLError as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return False

def main():
    print("=== Consumer and Household Debt 指标验证 ===")
    
    # 用户提到的指标列表
    indicators = [
        ('HDTGPDUSQ163N', 'Household Debt to GDP for United States'),
        ('TDSP', 'Household Debt Service Payments as a Percent of Disposable Personal Income'),
        ('MDOAH', 'Mortgage Debt Outstanding, All holders (DISCONTINUED)'),
        ('RCCCBBALTOT', 'Large Bank Consumer Credit Card Balances: Total Balances'),
        ('SLOASM', 'Student Loans Owned and Securitized'),
        ('DSR', 'Household Debt Service Ratio'),
        ('FEDFUNDS', 'Federal Funds Effective Rate'),
    ]
    
    # 需要补全的额外指标建议
    additional_indicators = [
        ('TOTALSL', 'Total Consumer Credit Outstanding'),
        ('DTCOLNVHFNM', 'Household Debt: Total'),
        ('DSRBTTSA', 'Household Debt Service Ratio'),
        ('MOCMRH', 'Monthly Consumer Credit Outstanding: Revolving'),
        ('DTCOLNVHFNM', 'Household Debt: Total'),
    ]
    
    valid_indicators = []
    
    print("\n" + "="*60)
    print("1. 验证用户指定的指标")
    print("="*60)
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
    
    print("\n" + "="*60)
    print("2. 验证补全建议指标")
    print("="*60)
    
    for series_id, description in additional_indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
    
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    print(f"有效指标数量: {len(valid_indicators)}")
    
    for series_id, description in valid_indicators:
        print(f"✅ {series_id}: {description}")
    
    print("\n建议的8个指标配置:")
    for i, (series_id, description) in enumerate(valid_indicators[:8], 1):
        print(f"{i}. {series_id}: {description}")

if __name__ == "__main__":
    main()
