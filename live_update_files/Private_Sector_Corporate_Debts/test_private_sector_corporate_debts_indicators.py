#!/usr/bin/env python3
"""
验证Private Sector Corporate Debts指标的FRED数据可用性
基于实际使用的test_household_debt_indicators.py
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
    print("=== Private Sector Corporate Debts 指标验证 ===")
    
    # 定义要验证的指标列表 - 扩展至8个指标
    indicators = [
        ('USREC', 'NBER based Recession Indicators for the United States from the Period following the Peak through the Trough'),
        ('FPCPITOTLZGUSA', 'Inflation, consumer prices for the United States'),
        ('BAMLH0A0HYM2', 'ICE BofA US High Yield Index Option-Adjusted Spread'),
        ('WPC', 'Assets: Liquidity and Credit Facilities: Loans: Primary Credit: Week Average'),
        ('BCNSDODNS', 'Nonfinancial Corporate Business; Debt Securities and Loans; Liability, Level'),
        ('AAA', 'Moody\'s Seasoned Aaa Corporate Bond Yield'),
        ('BAA', 'Moody\'s Seasoned Baa Corporate Bond Yield'),
        ('NCBCMDPMVCE', 'Nonfinancial Corporate Business; Debt as a Percentage of the Market Value of Corporate Equities, Level'),
    ]
    
    valid_indicators = []
    
    print("\n" + "="*60)
    print("验证指定的指标")
    print("="*60)
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
    
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    print(f"有效指标数量: {len(valid_indicators)}")
    
    if len(valid_indicators) >= 8:
        print("✅ 满足8个指标要求")
        for i, (series_id, description) in enumerate(valid_indicators[:8], 1):
            print(f"{i}. {series_id}: {description}")
    else:
        print(f"⚠️  仅有{len(valid_indicators)}个有效指标，需要补充")

if __name__ == "__main__":
    main()
