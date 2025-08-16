#!/usr/bin/env python3
"""
验证Trade Deficits指标的FRED数据可用性
从资深经济分析师角度精选贸易逆差和国际收支相关指标
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
    print("=== Trade Deficits and International Balance 指标验证 ===")
    print("从资深经济分析师角度精选的核心贸易和国际收支指标")
    
    # 用户指定的5个优先指标 + 3个补充指标（资深分析师视角）
    indicators = [
        # 用户指定的5个优先核心指标
        ('BOPGSTB', 'Trade Balance: Goods and Services, Balance of Payments Basis'),
        ('IEABC', 'Balance on current account'),
        ('BOGZ1FL263061130Q', 'Rest of the World; Treasury Securities Held by Foreign Official Institutions; Asset, Level'),
        ('B235RC1Q027SBEA', 'Federal government current tax receipts: Taxes on production and imports: Customs duties'),
        ('MTSDS133FMS', 'Federal Surplus or Deficit [-]'),
        
        # 补充指标 - 从资深经济分析师角度添加以达到8个指标要求
        ('NETEXP', 'Net Exports of Goods and Services'),
        ('IMPGSC1', 'Real Imports of Goods and Services'),
        ('EXPGSC1', 'Real Exports of Goods and Services')
    ]
    
    valid_indicators = []
    
    print("\n" + "="*80)
    print("验证指定的贸易逆差和国际收支指标")
    print("="*80)
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
    
    print("\n" + "="*80)
    print("验证结果汇总")
    print("="*80)
    print(f"有效指标数量: {len(valid_indicators)}")
    
    if len(valid_indicators) >= 8:
        print("✅ 满足8个指标要求")
        print("\n经济分析师视角的指标分类:")
        print("📊 核心贸易指标:")
        for i, (series_id, description) in enumerate(valid_indicators[:3], 1):
            print(f"  {i}. {series_id}: {description}")
        
        print("💰 国际收支与财政指标:")
        for i, (series_id, description) in enumerate(valid_indicators[3:6], 4):
            print(f"  {i}. {series_id}: {description}")
            
        print("📈 补充分析指标:")
        for i, (series_id, description) in enumerate(valid_indicators[6:], 7):
            print(f"  {i}. {series_id}: {description}")
    else:
        print(f"⚠️  仅有{len(valid_indicators)}个有效指标，需要补充")
        print("\n建议补充的相关指标:")
        print("- EXPGSC1: 商品和服务出口")
        print("- BOGZ1FL265090205Q: 对外投资净头寸")
        print("- USWTBAL: 美国商品贸易余额")

    print(f"\n📋 经济分析解读:")
    print("• BOPGSTB: 核心贸易平衡指标，反映美国商品和服务贸易差额")
    print("• IEABC: 经常账户余额，包含贸易、收入和转移支付的综合指标")
    print("• BOGZ1FL263061130Q: 外国官方持有美国国债规模，反映美元储备货币地位")
    print("• B235RC1Q027SBEA: 关税收入，反映贸易政策影响")
    print("• MTSDS133FMS: 联邦财政赤字，与贸易逆差存在双赤字关联")

if __name__ == "__main__":
    main()
