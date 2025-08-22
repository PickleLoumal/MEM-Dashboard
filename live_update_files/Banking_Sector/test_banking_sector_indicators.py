#!/usr/bin/env python3
"""
验证Banking Sector指标的FRED数据可用性
基于实际使用的test_money_supply_indicators.py架构
严格遵循实时指标实施模板

Banking Sector指标列表(确保8个指标):
1. Federal Funds Rate (Effective) - FEDFUNDS
2. Interest on Reserve Balances (IORB) - IORB  
3. Total Reserve Balances - TOTRESNS
4. Federal Reserve Balance Sheet (Total Assets) - WALCL
5. PCE Price Index (Inflation) - PCEPI
6. Unemployment Rate - UNRATE
7. Commercial Bank Loans and Leases - TOTLL
8. Bank Prime Loan Rate - DPRIME
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
    """测试单个FRED指标的可用性和数据质量"""
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
            
            # 获取最新数据进行质量检查
            obs_url = f"{BASE_URL}/series/observations"
            obs_params = {
                'series_id': series_id,
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'limit': 100,
                'sort_order': 'desc'
            }
            
            obs_query_string = urllib.parse.urlencode(obs_params)
            obs_full_url = f"{obs_url}?{obs_query_string}"
            
            with urllib.request.urlopen(obs_full_url) as obs_response:
                obs_data = json.loads(obs_response.read().decode())
            
            if 'observations' in obs_data and len(obs_data['observations']) > 0:
                observations = obs_data['observations']
                latest_obs = observations[0]
                print(f"   最新值: {latest_obs['value']} ({latest_obs['date']})")
                
                # 数据质量分析
                return analyze_data_quality(series_id, observations)
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

def analyze_data_quality(series_id, observations):
    """分析数据质量和完整性"""
    print(f"📊 数据质量分析 - {series_id}:")
    
    # 基础统计
    total_obs = len(observations)
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
                null_count += 1
    
    if not valid_values:
        print(f"❌ 没有有效数值")
        return False
    
    # 数据质量指标
    print(f"   - 总观测数: {total_obs}")
    print(f"   - 有效数值: {len(valid_values)}")
    print(f"   - 空值数量: {null_count}")
    print(f"   - 数据完整率: {(len(valid_values)/total_obs)*100:.1f}%")
    print(f"   - 数值范围: {min(valid_values):.2f} 到 {max(valid_values):.2f}")
    
    if len(valid_values) > 1:
        print(f"   - 平均值: {statistics.mean(valid_values):.3f}")
        print(f"   - 标准差: {statistics.stdev(valid_values):.3f}")
    
    # 时间覆盖分析
    dates = []
    for obs in observations:
        if obs['value'] != '.' and obs['value'] != '' and obs['value'] is not None:
            try:
                dates.append(datetime.strptime(obs['date'], '%Y-%m-%d'))
            except ValueError:
                continue
    
    if dates:
        dates.sort()
        earliest = dates[-1]  # 因为是desc排序
        latest = dates[0]
        time_span = (latest - earliest).days
        print(f"   - 时间跨度: {time_span} 天 ({earliest.strftime('%Y-%m-%d')} 到 {latest.strftime('%Y-%m-%d')})")
        
        # 数据新鲜度检查
        days_since_latest = (datetime.now() - latest).days
        print(f"   - 数据新鲜度: {days_since_latest} 天前")
        
        if days_since_latest <= 30:
            print(f"✅ 数据新鲜度良好")
        elif days_since_latest <= 90:
            print(f"⚠️  数据稍显陈旧")
        else:
            print(f"❌ 数据过于陈旧")
    
    # 业务逻辑验证
    validate_business_rules(series_id, valid_values)
    
    return len(valid_values) > 50  # 至少需要50个有效数据点

def validate_business_rules(series_id, values):
    """根据经济指标特性进行业务规则验证"""
    print(f"🔍 业务规则验证 - {series_id}:")
    
    if not values:
        print("   ❌ 无数据可验证")
        return False
    
    min_val = min(values)
    max_val = max(values)
    
    # 根据不同指标类型进行验证
    if series_id in ['FEDFUNDS', 'IORB']:  # 利率指标
        if min_val < 0:
            print(f"   ⚠️  检测到负利率: {min_val}%")
        if max_val > 25:
            print(f"   ⚠️  检测到异常高利率: {max_val}%")
        if 0 <= min_val <= 25 and 0 <= max_val <= 25:
            print("   ✅ 利率范围合理")
            
    elif series_id == 'UNRATE':  # 失业率
        if min_val < 0 or max_val > 100:
            print(f"   ❌ 失业率范围异常: {min_val}% - {max_val}%")
        elif 0 <= min_val <= 20 and 0 <= max_val <= 20:
            print("   ✅ 失业率范围正常")
        else:
            print(f"   ⚠️  失业率范围需关注: {min_val}% - {max_val}%")
            
    elif series_id in ['WALCL', 'TOTRESNS', 'TOTLL']:  # 资产负债表和贷款指标
        if min_val < 0:
            print(f"   ❌ 检测到负值: {min_val}")
        else:
            print(f"   ✅ 资产值范围合理")
            
    elif series_id == 'DPRIME':  # 银行基准利率
        if min_val < 0:
            print(f"   ⚠️  检测到负利率: {min_val}%")
        if max_val > 30:
            print(f"   ⚠️  检测到异常高利率: {max_val}%")
        if 0 <= min_val <= 30 and 0 <= max_val <= 30:
            print("   ✅ 银行基准利率范围合理")
            
    elif series_id == 'PCEPI':  # 价格指数
        if min_val < 0:
            print(f"   ⚠️  检测到通缩期间: 最低值 {min_val}")
        if len(values) > 12:  # 检查趋势
            recent_avg = statistics.mean(values[:12])
            older_avg = statistics.mean(values[-12:])
            growth_rate = ((recent_avg - older_avg) / older_avg) * 100
            print(f"   📈 年化通胀趋势: {growth_rate:.2f}%")
            
    return True

def main():
    """主验证流程"""
    print("=== Banking Sector 指标验证 ===")
    print("基于FRED API的数据可用性和质量验证")
    
    # 定义要验证的指标列表 - 确保8个指标符合要求
    indicators = [
        ('FEDFUNDS', 'Federal Funds Rate (Effective) - 联邦基金利率'),
        ('IORB', 'Interest on Reserve Balances (IORB) - 准备金余额利率'),
        ('TOTRESNS', 'Total Reserve Balances - 总准备金余额'),
        ('WALCL', 'Federal Reserve Balance Sheet (Total Assets) - 美联储资产负债表总资产'),
        ('PCEPI', 'PCE Price Index (Inflation) - PCE价格指数'),
        ('UNRATE', 'Unemployment Rate - 失业率'),
        ('TOTLL', 'Commercial Bank Loans and Leases - 商业银行贷款和租赁'),
        ('DPRIME', 'Bank Prime Loan Rate - 银行基准贷款利率'),
    ]
    
    valid_indicators = []
    validation_results = {}
    
    print("\n" + "="*80)
    print("验证Banking Sector指定的8个指标")
    print("="*80)
    
    for series_id, description in indicators:
        success = test_fred_indicator(series_id, description)
        validation_results[series_id] = success
        if success:
            valid_indicators.append((series_id, description))
    
    print("\n" + "="*80)
    print("验证结果汇总")
    print("="*80)
    print(f"总指标数量: {len(indicators)}")
    print(f"有效指标数量: {len(valid_indicators)}")
    print(f"验证成功率: {(len(valid_indicators)/len(indicators))*100:.1f}%")
    
    if len(valid_indicators) >= 8:
        print("✅ 满足8个指标要求")
        print("\n📋 有效指标清单:")
        for i, (series_id, description) in enumerate(valid_indicators, 1):
            status = "✅" if validation_results[series_id] else "⚠️"
            print(f"{i}. {status} {series_id}: {description}")
    else:
        print(f"⚠️  仅有{len(valid_indicators)}个有效指标，需要检查失败原因")
        print("\n❌ 失败指标:")
        for series_id, description in indicators:
            if not validation_results[series_id]:
                print(f"   - {series_id}: {description}")
    
    # 技术建议
    print("\n" + "="*80)
    print("技术实施建议")
    print("="*80)
    
    if len(valid_indicators) == len(indicators):
        print("🎉 所有指标验证通过，可以开始数据抓取和API开发")
        print("📊 建议数据抓取配置:")
        print("   - 历史数据: 最近1000条记录")
        print("   - 更新频率: 5分钟")
        print("   - 批处理大小: 100条/批次")
        print("   - 重试策略: 3次重试，指数退避")
    else:
        print("⚠️  部分指标存在问题，建议先解决验证失败的指标")
    
    return len(valid_indicators) == len(indicators)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Banking Sector指标验证完成，可以进行下一步实施")
            sys.exit(0)
        else:
            print("\n❌ 指标验证存在问题，请检查并解决")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断验证过程")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 验证过程发生异常: {str(e)}")
        sys.exit(2)
