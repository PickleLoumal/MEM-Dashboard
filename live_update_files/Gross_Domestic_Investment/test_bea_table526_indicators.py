#!/usr/bin/env python3
"""
验证BEA Table 5.2.6 Real Gross and Net Domestic Investment指标的数据可用性
测试BEA API访问Table 5.2.6: Real Gross and Net Domestic Investment by Major Type (Chained dollars)

这是实际的投资数值，不是百分比变化
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

def test_bea_table_info():
    """测试BEA表格信息，寻找Table 5.2.6的正确表名"""
    print("=== 查找BEA Table 5.2.6的正确表名 ===")
    
    # 获取所有NIPA表格列表
    params = {
        'UserID': BEA_API_KEY,
        'method': 'GetParameterValues',
        'datasetname': 'NIPA',
        'ParameterName': 'TableName',
        'ResultFormat': 'JSON'
    }
    
    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"{BASE_URL}?{query_string}"
        print(f"获取表格列表URL: {full_url}")
        
        with urllib.request.urlopen(full_url) as response:
            data = json.loads(response.read().decode())
        
        if 'BEAAPI' in data and 'Results' in data['BEAAPI']:
            tables = data['BEAAPI']['Results']['ParamValue']
            print(f"找到 {len(tables)} 个NIPA表格")
            
            # 查找包含"5.2.6"或"investment"的表格
            investment_tables = []
            print("所有包含'5'开头的表格:")
            for table in tables:
                table_name = table.get('Key', '')
                table_desc = table.get('Desc', '')
                
                # 显示所有5开头的表格来找到5.2.6
                if table_name.startswith('T5') or '5.' in table_name:
                    print(f"  📋 {table_name}: {table_desc}")
                
                if ('5.2.6' in table_name or '5.2.6' in table_desc or 
                    ('investment' in table_desc.lower() and 'real' in table_desc.lower()) or
                    ('5.2.6' in table_name) or ('526' in table_name)):
                    investment_tables.append((table_name, table_desc))
                    print(f"  📊 {table_name}: {table_desc}")
            
            return investment_tables
        else:
            print("❌ 无法获取表格列表")
            return []
            
    except Exception as e:
        print(f"❌ 获取表格信息失败: {e}")
        return []

def test_bea_indicator(table_name, line_number, description, series_id=None):
    """
    测试单个BEA指标的可用性
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
        'Year': '2022,2023',  # 只测试这两年以减少数据量
        'Frequency': 'A',  # 改为年度数据
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
                all_data_points = beaapi['Results']['Data']
                
                print(f"✅ 获取到 {len(all_data_points)} 个数据点 (整个表格)")
                
                # 过滤出指定行号的数据
                target_line_data = []
                for data in all_data_points:
                    data_line_number = data.get('LineNumber', '')
                    if data_line_number == str(line_number):
                        target_line_data.append(data)
                
                if len(target_line_data) > 0:
                    print(f"   找到行 {line_number} 的数据: {len(target_line_data)} 个数据点")
                    
                    # 显示该行的完整信息用于调试
                    print("   该行数据结构:")
                    for i, data in enumerate(target_line_data):
                        time_period = data.get('TimePeriod', 'N/A')
                        data_value = data.get('DataValue', 'N/A')
                        line_desc = data.get('LineDescription', 'N/A')
                        print(f"   [{i}] {time_period}: {data_value} - {line_desc}")
                    
                    # 收集数值用于范围分析
                    values = []
                    for data in target_line_data:
                        data_value = data.get('DataValue', 'N/A')
                        try:
                            if data_value and data_value != '--':
                                # 移除逗号并转换为数字
                                clean_value = data_value.replace(',', '')
                                values.append(float(clean_value))
                        except:
                            pass
                            
                    data_points = target_line_data  # 用于后续处理
                    
                    # 分析数值范围来判断是否为实际数值
                    if values:
                        min_val = min(values)
                        max_val = max(values)
                        avg_val = sum(values) / len(values)
                        print(f"   数值范围: {min_val:.2f} - {max_val:.2f} (平均: {avg_val:.2f})")
                        
                        # 判断数据类型
                        if max_val > 1000:
                            print("   ✅ 数据类型: 实际数值 (十亿美元)")
                        elif max_val < 100 and min_val > -50:
                            print("   ⚠️  数据类型: 可能是百分比变化")
                        else:
                            print("   ❓ 数据类型: 需要进一步确认")
                    
                    # 数据质量检查
                    valid_count = 0
                    for data in data_points:
                        if data.get('DataValue') and data.get('DataValue') != '--':
                            valid_count += 1
                    
                    print(f"   有效数据点: {valid_count}/{len(data_points)}")
                    print(f"   数据有效率: {valid_count/len(data_points)*100:.1f}%")
                    
                    return True
                else:
                    print(f"❌ 未找到行 {line_number} 的数据")
                    # 显示可用的行号用于调试
                    available_lines = set()
                    for data in all_data_points[:10]:  # 只显示前10个以避免输出过长
                        available_lines.add(data.get('LineNumber', 'N/A'))
                    print(f"   可用行号 (前10个): {sorted(available_lines)}")
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

def main():
    print("=== BEA Table 5.2.6 投资指标数据验证 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API密钥: {BEA_API_KEY[:10]}...")
    print()
    
    # 首先查找正确的表格名称
    print("1. 查找Table 5.2.6的正确表名:")
    print("="*60)
    investment_tables = test_bea_table_info()
    
    if not investment_tables:
        print("❌ 未找到相关投资表格，尝试已知的表名")
        # 基于BEA命名约定尝试更多可能的表名
        possible_tables = [
            'T50206',    # Table 5.02.06
            'T50206A',   # 年度版本
            'T50206Q',   # 季度版本
            'T050206',   # 完整数字格式
            'T05206',    # 简化格式
            'T052006',   # 年份格式
            '5.2.6',     # 原始格式
            'T050206A',  # 年度完整格式
            'T050206Q',  # 季度完整格式
        ]
        investment_tables = [(table, f"Real Gross and Net Domestic Investment (尝试: {table})") 
                           for table in possible_tables]
    
    print(f"\n2. 测试投资指标 (使用找到的 {len(investment_tables)} 个表格):")
    print("="*60)
    
    # Table 5.2.6的主要投资指标行号（基于CSV文件真实结构）
    indicators = [
        (4, 'Gross private domestic investment', 'INVESTMENT_TOTAL'),        # 行4 - 应该是4169.2 (2023)
        (7, 'Fixed investment', 'INVESTMENT_FIXED'),                        # 行7 - 应该是4103.9 (2023)
        (10, 'Nonresidential', 'INVESTMENT_NONRESIDENTIAL'),               # 行10 - 应该是3384.5 (2023)
        (13, 'Structures', 'INVESTMENT_STRUCTURES'),                       # 行13 - 应该是654.3 (2023)
        (16, 'Equipment', 'INVESTMENT_EQUIPMENT'),                          # 行16 - 应该是1285.2 (2023)
        (19, 'Intellectual property products', 'INVESTMENT_IP'),           # 行19 - 应该是1445.9 (2023)
        (22, 'Residential', 'INVESTMENT_RESIDENTIAL'),                     # 行22 - 应该是762.7 (2023)
        (25, 'Change in private inventories', 'INVESTMENT_INVENTORIES'),   # 行25 - 应该是33.1 (2023)
        (6, 'Equals: Net private domestic investment', 'INVESTMENT_NET'),   # 行6 - 应该是994.1 (2023)
        (26, 'Gross government investment', 'GOVT_INVESTMENT_TOTAL'),       # 行26 - 应该是797.2 (2023)
    ]
    
    valid_indicators = []
    failed_indicators = []
    
    # 测试每个可能的表名
    for table_name, table_desc in investment_tables:
        print(f"\n测试表格: {table_name} - {table_desc}")
        print("-" * 50)
        
        table_valid_count = 0
        for line_number, description, series_id in indicators:
            if test_bea_indicator(table_name, line_number, description, series_id):
                valid_indicators.append((table_name, line_number, description, series_id))
                table_valid_count += 1
            else:
                failed_indicators.append((table_name, line_number, description, series_id))
        
        print(f"表格 {table_name} 有效指标: {table_valid_count}/{len(indicators)}")
        
        # 如果找到足够多的有效指标，可以停止测试其他表格
        if table_valid_count >= 3:
            print(f"✅ 表格 {table_name} 包含足够的有效指标，建议使用此表")
            break
        
        # 为了调试，只测试前3个表格
        if len([t for t, _, _, _ in valid_indicators + failed_indicators]) > 30:
            print("⚠️ 为了避免输出过长，停止测试更多表格")
            break
    
    # 结果汇总
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    print(f"总测试指标: {len(indicators) * len(investment_tables)}")
    print(f"有效指标: {len(valid_indicators)}")
    print(f"失败指标: {len(failed_indicators)}")
    
    if len(valid_indicators) > 0:
        success_rate = len(valid_indicators) / (len(valid_indicators) + len(failed_indicators)) * 100
        print(f"成功率: {success_rate:.1f}%")
    
    if valid_indicators:
        print("\n✅ 有效的投资指标:")
        for i, (table_name, line_number, description, series_id) in enumerate(valid_indicators, 1):
            print(f"   {i}. {series_id}: {description} (表{table_name}, 行{line_number})")
    
    if failed_indicators:
        print(f"\n❌ 失败的指标: {len(failed_indicators)} 个")
        # 只显示前5个失败的指标，避免输出过长
        for i, (table_name, line_number, description, series_id) in enumerate(failed_indicators[:5], 1):
            print(f"   {i}. {series_id}: {description} (表{table_name}, 行{line_number})")
        if len(failed_indicators) > 5:
            print(f"   ... 还有 {len(failed_indicators) - 5} 个失败指标")
    
    print(f"\n📋 总结:")
    if len(valid_indicators) >= 5:
        print("✅ 找到足够的有效指标，可以继续进行数据抓取")
        # 推荐最佳表格
        table_counts = {}
        for table_name, _, _, _ in valid_indicators:
            table_counts[table_name] = table_counts.get(table_name, 0) + 1
        
        best_table = max(table_counts.items(), key=lambda x: x[1])
        print(f"🎯 推荐使用表格: {best_table[0]} (包含{best_table[1]}个有效指标)")
        return True
    else:
        print("⚠️  有效指标不足，需要检查表名或API配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
