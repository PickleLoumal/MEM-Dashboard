#!/usr/bin/env python3
"""
验证Money Supply指标的FRED数据可用性
基于实际使用的test_household_debt_indicators.py
"""

import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
import statistics
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

def validate_series_data(series_id, expected_range=None, data_type='numeric'):
    """验证系列数据质量"""
    print(f"\n🔍 验证数据质量: {series_id}")
    
    try:
        # 获取系列观测数据
        obs_url = f"{BASE_URL}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'limit': 100,
            'sort_order': 'desc'
        }
        
        query_string = urllib.parse.urlencode(params)
        full_url = f"{obs_url}?{query_string}"
        
        with urllib.request.urlopen(full_url) as response:
            obs_data = json.loads(response.read().decode())
        
        if 'observations' not in obs_data or len(obs_data['observations']) == 0:
            print(f"❌ 无观测数据")
            return False
            
        observations = obs_data['observations']
        print(f"📊 获取到 {len(observations)} 条观测数据")
        
        # 数据质量检查
        valid_values = []
        null_count = 0
        
        for obs in observations:
            if obs['value'] == '.' or obs['value'] == '' or obs['value'] is None:
                null_count += 1
            else:
                try:
                    value = float(obs['value'])
                    valid_values.append(value)
                except ValueError:
                    print(f"⚠️  无效数值: {obs['value']} 在日期 {obs['date']}")
        
        if not valid_values:
            print(f"❌ 没有有效数值")
            return False
            
        # 统计分析
        print(f"📊 数据质量分析:")
        print(f"   - 有效数值: {len(valid_values)}")
        print(f"   - 空值数量: {null_count}")
        print(f"   - 空值比例: {null_count/len(observations)*100:.1f}%")
        print(f"   - 数值范围: {min(valid_values):.2f} 到 {max(valid_values):.2f}")
        print(f"   - 平均值: {statistics.mean(valid_values):.2f}")
        if len(valid_values) > 1:
            print(f"   - 标准差: {statistics.stdev(valid_values):.2f}")
        
        # 范围验证
        if expected_range:
            min_val, max_val = expected_range
            out_of_range = [v for v in valid_values if v < min_val or v > max_val]
            if out_of_range:
                print(f"⚠️  {len(out_of_range)} 个值超出预期范围 [{min_val}, {max_val}]")
            else:
                print(f"✅ 所有值在预期范围内")
        
        # 时间序列连续性检查
        dates = [datetime.strptime(obs['date'], '%Y-%m-%d') for obs in observations]
        dates.sort()
        
        gaps = []
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            if gap > 90:  # 超过90天的间隔视为异常
                gaps.append(gap)
        
        if gaps:
            print(f"⚠️  发现 {len(gaps)} 个大数据间隔，最大间隔: {max(gaps)} 天")
        else:
            print(f"✅ 时间序列连续性良好")
            
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    print("=== Money Supply 指标验证 ===")
    
    # 定义要验证的指标列表 - 7个核心指标+1个补充指标确保达到8个
    indicators = [
        ('FEDFUNDS', 'Federal Funds Rate - 联邦基金利率'),
        ('M2SL', 'M2 Money Supply - M2货币供应量'),
        ('WALCL', 'Federal Reserve Balance Sheet Total Assets - 美联储资产负债表总资产'),
        ('DRTSCIS', 'Net Percentage of Banks Tightening Standards for Commercial Loans - 银行贷款标准'),
        ('TOTLL', 'Commercial Banks Total Loans and Leases - 商业银行贷款和租赁总额'),
        ('IORB', 'Interest Rate on Reserve Balances - 准备金余额利率'),
        ('RRPONTSYD', 'Overnight Reverse Repurchase Agreements - 隔夜逆回购协议'),
        ('M1SL', 'M1 Money Supply - M1货币供应量 (补充指标)'),
    ]
    
    valid_indicators = []
    
    print("\n" + "="*60)
    print("验证指定的指标")
    print("="*60)
    
    for series_id, description in indicators:
        if test_fred_indicator(series_id, description):
            valid_indicators.append((series_id, description))
            # 验证数据质量
            validate_series_data(series_id)
    
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
        print("建议的替代/补充指标:")
        alternative_indicators = [
            ('BOGMBASE', 'Monetary Base - 货币基础'),
            ('MULT', 'Money Multiplier - 货币乘数'),
            ('AMBSL', 'Adjusted Monetary Base - 调整后货币基础'),
            ('CPFF', 'Commercial Paper Funding Facility - 商业票据融资便利'),
        ]
        
        for series_id, description in alternative_indicators:
            print(f"   - {series_id}: {description}")

if __name__ == "__main__":
    main()
