#!/usr/bin/env python3
"""
验证FRED Table 5.2.6投资指标的数据可用性
测试FRED API访问Real Gross and Net Domestic Investment by Major Type数据

基于FRED Table 5.2.6: Real Gross and Net Domestic Investment by Major Type (Chained Dollars)
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta

# FRED API配置
FRED_API_KEY = "1cdac6b8c1173f83a10444d17e73b32e"  # 从现有配置获取
BASE_URL = "https://api.stlouisfed.org/fred"

def test_fred_indicator(series_id, description):
    """测试单个FRED指标的可用性"""
    print(f"\n=== 测试FRED指标: {series_id} ({description}) ===")
    
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
                
                # 显示最近几个数据点
                print("   最近数据:")
                for obs in obs_data['observations'][:3]:
                    print(f"     {obs['date']}: {obs['value']}")
                
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

def search_fred_series(search_term, limit=10):
    """搜索FRED系列"""
    print(f"\n=== 搜索FRED系列: {search_term} ===")
    
    search_url = f"{BASE_URL}/series/search"
    params = {
        'search_text': search_term,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'limit': limit
    }
    
    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{search_url}?{query_string}"
        
        with urllib.request.urlopen(full_url) as response:
            search_data = json.loads(response.read().decode())
        
        if 'seriess' in search_data and len(search_data['seriess']) > 0:
            print(f"找到 {len(search_data['seriess'])} 个相关系列:")
            for series in search_data['seriess']:
                print(f"  - {series['id']}: {series['title']}")
                print(f"    单位: {series.get('units', 'N/A')}, 频率: {series.get('frequency', 'N/A')}")
            return search_data['seriess']
        else:
            print("未找到相关系列")
            return []
            
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def main():
    print("=== FRED Table 5.2.6 投资指标验证 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API密钥: {FRED_API_KEY[:10]}...")
    print()
    
    # Table 5.2.6的已知FRED系列ID
    # 基于FRED网站的Real Gross and Net Domestic Investment by Major Type
    indicators = [
        # 总投资
        ('GPDIC1', 'Real Gross Private Domestic Investment'),
        ('GPDI', 'Gross Private Domestic Investment'),
        
        # 固定投资
        ('A006RX1', 'Real gross private domestic investment'),
        ('A007RX1', 'Real fixed investment'),
        
        # 分类投资
        ('A008RX1', 'Real nonresidential fixed investment'),
        ('A011RX1', 'Real residential fixed investment'),
        ('A014RX1', 'Real change in private inventories'),
        
        # 结构、设备、知识产权
        ('A009RX1', 'Real nonresidential structures'),
        ('A557RX1', 'Real equipment and software'),
        ('B009RX1', 'Real intellectual property products'),
        
        # 净投资
        ('A557RX1', 'Real net private domestic investment'),
        ('A560RX1', 'Real net fixed investment'),
    ]
    
    # 首先搜索投资相关的系列
    print("1. 搜索投资相关的FRED系列:")
    print("="*60)
    
    search_terms = [
        'real gross private domestic investment',
        'real fixed investment', 
        'real nonresidential investment',
        'real residential investment'
    ]
    
    found_series = []
    for term in search_terms:
        results = search_fred_series(term, limit=5)
        found_series.extend(results)
    
    print("\n2. 测试已知投资指标:")
    print("="*60)
    
    valid_indicators = []
    failed_indicators = []
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
        else:
            failed_indicators.append((series_id, description))
    
    # 结果汇总
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    print(f"总测试指标: {len(indicators)}")
    print(f"有效指标: {len(valid_indicators)}")
    print(f"失败指标: {len(failed_indicators)}")
    
    if len(indicators) > 0:
        success_rate = (len(valid_indicators) / len(indicators)) * 100
        print(f"成功率: {success_rate:.1f}%")
    
    if valid_indicators:
        print("\n✅ 有效的投资指标:")
        for i, (series_id, description) in enumerate(valid_indicators, 1):
            print(f"   {i}. {series_id}: {description}")
    
    if failed_indicators:
        print("\n❌ 失败的指标:")
        for i, (series_id, description) in enumerate(failed_indicators, 1):
            print(f"   {i}. {series_id}: {description}")
    
    # 建议
    print(f"\n📋 总结:")
    if len(valid_indicators) >= 5:
        print("✅ 足够的有效指标，可以继续进行数据抓取")
        print(f"建议使用以下{min(8, len(valid_indicators))}个主要指标:")
        for i, (series_id, description) in enumerate(valid_indicators[:8], 1):
            print(f"   {i}. {series_id}: {description}")
        return True
    else:
        print("⚠️  有效指标不足，需要进一步搜索或调整指标列表")
        print("建议检查搜索结果中的其他相关指标")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
