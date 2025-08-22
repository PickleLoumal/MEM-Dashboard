#!/usr/bin/env python3
"""
验证BEA投资指标的数据可用性
测试BEA API访问和数据获取，基于真实的BEA API结构和现有数据库配置
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta

# BEA API配置
BEA_API_KEY = "DEFB02B6-33E9-4803-AEC1-73B03F4084B8"
BASE_URL = "https://apps.bea.gov/api/data"

def test_bea_indicator(table_name, line_number, description, series_id=None):
    """
    测试单个BEA指标的可用性
    基于现有数据库配置的真实BEA API参数
    """
    print(f"\n=== 测试BEA指标: {series_id or 'N/A'} ({description}) ===")
    print(f"表: {table_name}, 行: {line_number}")
    
    # BEA API标准参数
    params = {
        'UserID': BEA_API_KEY,
        'method': 'GetData',
        'datasetname': 'NIPA',
        'TableName': table_name,
        'LineNumber': str(line_number),
        'Year': '2023,2024,2025',
        'Frequency': 'Q',
        'ResultFormat': 'JSON'
    }
    
    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{BASE_URL}?{query_string}"
        print(f"API URL: {full_url}")
        
        with urllib.request.urlopen(full_url) as response:
            bea_data = json.loads(response.read().decode())
        
        print(f"API响应状态: {response.getcode()}")
        
        # 检查BEA API标准响应格式
        if 'BEAAPI' in bea_data:
            beaapi = bea_data['BEAAPI']
            
            # 检查是否有错误
            if 'Error' in beaapi:
                error_info = beaapi['Error']
                print(f"❌ BEA API错误: {error_info}")
                return False
            
            # 检查结果数据
            if 'Results' in beaapi and 'Data' in beaapi['Results']:
                data_points = beaapi['Results']['Data']
                
                if len(data_points) > 0:
                    print(f"✅ 获取到 {len(data_points)} 个数据点")
                    
                    # 显示最新几个数据点
                    print("   最新数据:")
                    for data in data_points[-3:]:
                        time_period = data.get('TimePeriod', 'N/A')
                        data_value = data.get('DataValue', 'N/A')
                        print(f"   {time_period}: {data_value}")
                    
                    # 数据质量检查
                    valid_count = 0
                    for data in data_points:
                        if data.get('DataValue') and data.get('DataValue') != '--':
                            valid_count += 1
                    
                    print(f"   有效数据点: {valid_count}/{len(data_points)}")
                    print(f"   数据有效率: {valid_count/len(data_points)*100:.1f}%")
                    
                    return True
                else:
                    print(f"❌ 无数据返回")
                    return False
            else:
                print(f"❌ 响应格式错误 - 缺少Results/Data")
                if 'Results' in beaapi:
                    print(f"   Results内容: {beaapi['Results']}")
                return False
        else:
            print(f"❌ 响应格式错误 - 缺少BEAAPI节点")
            print(f"   响应内容: {json.dumps(bea_data, indent=2)[:500]}...")
            return False
            
    except urllib.error.URLError as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bea_api_connection():
    """测试BEA API基本连接性"""
    print("=== 测试BEA API连接性 ===")
    
    # 测试基本的GetParameterList调用
    params = {
        'UserID': BEA_API_KEY,
        'method': 'GetParameterList',
        'datasetname': 'NIPA',
        'ResultFormat': 'JSON'
    }
    
    try:
        query_string = urllib.parse.urlencode(params)
        url = f"{BASE_URL}?{query_string}"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        if 'BEAAPI' in data and 'Results' in data['BEAAPI']:
            print("✅ BEA API连接正常")
            return True
        else:
            print(f"❌ BEA API连接异常: {data}")
            return False
            
    except Exception as e:
        print(f"❌ BEA API连接失败: {e}")
        return False

def main():
    print("=== BEA投资指标数据验证 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API密钥: {BEA_API_KEY[:10]}...")
    print()
    
    # 首先测试API连接性
    if not test_bea_api_connection():
        print("❌ BEA API连接失败，无法继续测试")
        return
    
    print()
    
    # 基于现有数据库配置的投资指标列表
    # 这些是已知存在于数据库中的指标配置
    indicators = [
        ('T10101', 7, 'Gross Private Domestic Investment', 'INVESTMENT_TOTAL'),
        ('T10101', 8, 'Fixed Investment', 'INVESTMENT_FIXED'),
        ('T10101', 21, 'Government Consumption and Investment', 'GOVT_TOTAL'),
        ('T10101', 22, 'Federal Government Spending', 'GOVT_FEDERAL'),
        ('T10101', 35, 'State and Local Government Spending', 'GOVT_STATE_LOCAL'),
    ]
    
    # 添加index.html中显示的其他投资子项（如果存在）
    additional_indicators = [
        ('T10101', 9, 'Nonresidential Investment', 'INVESTMENT_NONRESIDENTIAL'),
        ('T10101', 10, 'Residential Investment', 'INVESTMENT_RESIDENTIAL'), 
        ('T10101', 11, 'Change in Private Inventories', 'INVESTMENT_INVENTORIES'),
        ('T10101', 12, 'Structures', 'INVESTMENT_STRUCTURES'),
        ('T10101', 13, 'Equipment', 'INVESTMENT_EQUIPMENT'),
        ('T10101', 14, 'Intellectual Property Products', 'INVESTMENT_IP'),
    ]
    
    valid_indicators = []
    failed_indicators = []
    
    print("1. 测试已知存在的投资指标:")
    print("="*60)
    
    for table_name, line_number, description, series_id in indicators:
        if test_bea_indicator(table_name, line_number, description, series_id):
            valid_indicators.append((table_name, line_number, description, series_id))
        else:
            failed_indicators.append((table_name, line_number, description, series_id))
    
    print("\n2. 测试扩展投资指标:")
    print("="*60)
    
    for table_name, line_number, description, series_id in additional_indicators:
        if test_bea_indicator(table_name, line_number, description, series_id):
            valid_indicators.append((table_name, line_number, description, series_id))
        else:
            failed_indicators.append((table_name, line_number, description, series_id))
    
    # 结果汇总
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    print(f"总测试指标: {len(indicators) + len(additional_indicators)}")
    print(f"有效指标: {len(valid_indicators)}")
    print(f"失败指标: {len(failed_indicators)}")
    print(f"成功率: {len(valid_indicators)/(len(indicators) + len(additional_indicators))*100:.1f}%")
    
    if valid_indicators:
        print("\n✅ 有效的投资指标:")
        for i, (table_name, line_number, description, series_id) in enumerate(valid_indicators, 1):
            print(f"   {i}. {series_id}: {description} (表{table_name}, 行{line_number})")
    
    if failed_indicators:
        print("\n❌ 失败的指标:")
        for i, (table_name, line_number, description, series_id) in enumerate(failed_indicators, 1):
            print(f"   {i}. {series_id}: {description} (表{table_name}, 行{line_number})")
    
    print(f"\n📋 总结:")
    if len(valid_indicators) >= 3:
        print("✅ 足够的有效指标，可以继续进行数据抓取")
        return True
    else:
        print("⚠️  有效指标不足，需要检查API配置或指标定义")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)