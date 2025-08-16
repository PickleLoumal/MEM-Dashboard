#!/usr/bin/env python3
"""
验证Government Debts指标的FRED数据可用性
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
        url = f"{series_url}?" + urllib.parse.urlencode(params)
        print(f"请求URL: {url}")
        
        # 发送请求
        response = urllib.request.urlopen(url)
        series_data = json.loads(response.read().decode('utf-8'))
        
        if 'seriess' in series_data and len(series_data['seriess']) > 0:
            series_info = series_data['seriess'][0]
            print(f"✅ 系列信息获取成功")
            print(f"   标题: {series_info.get('title', 'N/A')}")
            print(f"   单位: {series_info.get('units', 'N/A')}")
            print(f"   频率: {series_info.get('frequency', 'N/A')}")
            print(f"   开始日期: {series_info.get('observation_start', 'N/A')}")
            print(f"   结束日期: {series_info.get('observation_end', 'N/A')}")
            
            # 获取最新观测数据
            obs_url = f"{BASE_URL}/series/observations"
            obs_params = {
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 10,
                'sort_order': 'desc'
            }
            
            obs_request_url = f"{obs_url}?" + urllib.parse.urlencode(obs_params)
            obs_response = urllib.request.urlopen(obs_request_url)
            obs_data = json.loads(obs_response.read().decode('utf-8'))
            
            if 'observations' in obs_data and len(obs_data['observations']) > 0:
                print(f"✅ 观测数据获取成功")
                print(f"   可用观测数量: {len(obs_data['observations'])}")
                
                # 显示最新的几个有效数据点
                valid_observations = [obs for obs in obs_data['observations'] if obs['value'] != '.']
                if valid_observations:
                    print(f"   最新有效数据:")
                    for i, obs in enumerate(valid_observations[:3]):
                        print(f"     {obs['date']}: {obs['value']}")
                    return True
                else:
                    print(f"❌ 没有有效的观测数据")
                    return False
            else:
                print(f"❌ 无法获取观测数据")
                return False
        else:
            print(f"❌ 系列信息获取失败")
            return False
            
    except urllib.error.URLError as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return False

def main():
    print("=== Government Debts 指标验证 ===")
    
    # 定义要验证的指标列表 - 用户指定的4个指标 + 补充的4个指标
    indicators = [
        ('GFDEBTN', 'Federal Debt: Total Public Debt'),
        ('GFDEGDQ188S', 'Federal Debt: Total Public Debt as Percent of Gross Domestic Product'),
        ('MTSDS133FMS', 'Federal Surplus or Deficit [-]'),
        ('LNU00024230', 'Population Level - 55 Yrs. & over'),
        # 补充的4个政府债务相关指标
        ('FYGFD', 'Federal Government Current Receipts and Expenditures: Government Social Benefits'),
        ('FYOIGDA188S', 'Federal Debt: Held by Federal Reserve Banks as Percent of GDP'),
        ('FYGFGDQ188S', 'Federal Government Debt: Total Public Debt as Percent of GDP'),
        ('TOTALGOV', 'Government Total Expenditures')
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
    print(f"有效指标列表:")
    for series_id, description in valid_indicators:
        print(f"  ✅ {series_id}: {description}")
    
    if len(valid_indicators) >= 4:
        print("✅ 满足基本指标要求")
        
        # 如果需要补充到8个指标，这里可以添加搜索逻辑
        if len(valid_indicators) < 8:
            print(f"⚠️  当前有{len(valid_indicators)}个指标，建议补充到8个以符合实施模板要求")
            print("可考虑的补充指标：")
            additional_indicators = [
                ('GFDEGDQ188S', 'Federal Debt to GDP Ratio'),
                ('FYGFD', 'Federal Government Debt: Total Public Debt'),
                ('FYOIGDA188S', 'Federal Debt: Held by Federal Reserve Banks as Percent of GDP'),
                ('GFDEBTN', 'Federal Debt: Total Public Debt')
            ]
            for series_id, desc in additional_indicators:
                if series_id not in [i[0] for i in valid_indicators]:
                    print(f"     - {series_id}: {desc}")
    else:
        print(f"❌ 仅有{len(valid_indicators)}个有效指标，低于最低要求")

if __name__ == "__main__":
    main()
