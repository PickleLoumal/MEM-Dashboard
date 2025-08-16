#!/usr/bin/env python3
"""
验证Government Deficit Financing指标的FRED数据可用性
基于资深经济分析师视角的8个核心指标
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta

# FRED API配置
FRED_API_KEY = "1cdac6b8c1173f83a10444d17e73b32e"
BASE_URL = "https://api.stlouisfed.org/fred"

def test_fred_indicator(series_id, description):
    """测试单个FRED指标的可用性"""
    try:
        # 构建API URL
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'limit': 5,
            'sort_order': 'desc'
        }
        
        url = f"{BASE_URL}/series/observations?" + urllib.parse.urlencode(params)
        
        # 发送请求
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        if 'observations' in data and len(data['observations']) > 0:
            latest_obs = data['observations'][0]
            print(f"✅ {series_id} - {description}")
            print(f"   最新数据: {latest_obs['value']} (日期: {latest_obs['date']})")
            print(f"   数据可用性: 正常")
            return True
        else:
            print(f"❌ {series_id} - {description}")
            print(f"   错误: 无数据可用")
            return False
            
    except Exception as e:
        print(f"❌ {series_id} - {description}")
        print(f"   错误: {str(e)}")
        return False

def main():
    """主验证流程"""
    print("=== Government Deficit Financing 指标验证 ===")
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 8个核心指标 - 基于资深经济分析师视角
    indicators = [
        # 用户指定的4个核心指标
        ("GFDEBTN", "Federal Debt: Total Public Debt (联邦债务总额)"),
        ("GFDEGDQ188S", "Federal Debt: Total Public Debt as Percent of GDP (联邦债务占GDP比例)"),
        ("MTSDS133FMS", "Federal Surplus or Deficit [-] (联邦盈余或赤字)"),
        ("W006RC1Q027SBEA", "Federal government current tax receipts (联邦政府当期税收)"),
        
        # 经济分析师补充的4个关键指标
        ("FYONET", "Federal Net Outlays (联邦净支出)"),
        ("FGEXPND", "Federal Government: Current Expenditures (联邦政府当期支出)"),
        ("FGRECPT", "Federal Government: Current Receipts (联邦政府当期收入)"),
        ("EXCSRESNW", "Excess Reserves of Depository Institutions (存款机构超额准备金)")
    ]
    
    print("\n🔍 开始验证各个指标...")
    print("-" * 60)
    
    success_count = 0
    total_count = len(indicators)
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            success_count += 1
        print()
    
    print("="*60)
    print(f"📊 验证完成统计:")
    print(f"   总指标数: {total_count}")
    print(f"   成功验证: {success_count}")
    print(f"   失败数量: {total_count - success_count}")
    print(f"   成功率: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 所有指标验证通过！可以继续进行数据抓取。")
        return True
    else:
        print(f"\n⚠️  有 {total_count - success_count} 个指标验证失败，请检查指标ID或网络连接。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
