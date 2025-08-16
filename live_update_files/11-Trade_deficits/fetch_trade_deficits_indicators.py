#!/usr/bin/env python3
"""
抓取Trade Deficits贸易逆差指标数据到Django数据库
使用Django管理命令方式
"""

import os
import sys
import django
from datetime import datetime

# 添加Django项目路径
sys.path.append('/Volumes/Pickle Samsung SSD/MEM Dashboard 2/src/django_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')

# 初始化Django
django.setup()

from fred_us.data_fetcher import UsFredDataFetcher
from fred_us.models import FredUsIndicator

def fetch_trade_deficits_indicators():
    """抓取贸易逆差和国际收支指标数据"""
    print("🔄 开始抓取贸易逆差和国际收支指标数据...")
    print("📊 从资深经济分析师角度精选的8个核心指标")
    
    # 8个贸易逆差和国际收支指标（用户指定的5个优先 + 3个补充）
    trade_indicators = [
        # 用户指定的5个优先核心指标
        'BOPGSTB',    # Trade Balance: Goods and Services, Balance of Payments Basis
        'IEABC',      # Balance on current account
        'BOGZ1FL263061130Q',  # Rest of the World; Treasury Securities Held by Foreign Official Institutions
        'B235RC1Q027SBEA',    # Federal government current tax receipts: Customs duties
        'MTSDS133FMS',        # Federal Surplus or Deficit [-]
        
        # 补充指标 - 达到8个指标要求
        'NETEXP',     # Net Exports of Goods and Services
        'IMPGSC1',    # Real Imports of Goods and Services
        'EXPGSC1',    # Real Exports of Goods and Services
    ]
    
    # 指标中文描述（用于数据库记录）
    indicator_descriptions = {
        # 用户指定的5个优先指标
        'BOPGSTB': '贸易平衡：商品和服务（国际收支基础）',
        'IEABC': '经常账户余额',
        'BOGZ1FL263061130Q': '外国官方机构持有的美国国债',
        'B235RC1Q027SBEA': '联邦政府关税收入',
        'MTSDS133FMS': '联邦财政赤字/盈余',
        
        # 补充指标
        'NETEXP': '商品和服务净出口',
        'IMPGSC1': '实际商品和服务进口',
        'EXPGSC1': '实际商品和服务出口'
    }
    
    fetcher = UsFredDataFetcher()
    
    for series_id in trade_indicators:
        print(f"\n=== 抓取指标: {series_id} ({indicator_descriptions.get(series_id, 'Trade Indicator')}) ===")
        
        try:
            # 检查当前数据库中是否已有数据
            existing_count = FredUsIndicator.objects.filter(series_id=series_id).count()
            print(f"数据库中现有记录数: {existing_count}")
            
            # 使用基础类的get_series_observations方法
            print(f"正在从FRED API抓取 {series_id} 数据...")
            observations = fetcher.get_series_observations(series_id, limit=500)
            
            if observations:
                print(f"✅ 从API获取到 {len(observations)} 条观测数据")
                
                # 保存到数据库
                saved_count = 0
                for obs in observations:
                    try:
                        # 跳过无效数据
                        if obs['value'] == '.' or obs['value'] == '' or obs['value'] is None:
                            continue
                            
                        # 转换值为浮点数
                        try:
                            value = float(obs['value'])
                        except (ValueError, TypeError):
                            continue
                        
                        # 检查是否已存在
                        if not FredUsIndicator.objects.filter(
                            series_id=series_id, 
                            date=obs['date']
                        ).exists():
                            
                            # 创建新记录
                            indicator = FredUsIndicator(
                                series_id=series_id,
                                date=obs['date'],
                                value=value,
                                indicator_name=f"US {indicator_descriptions.get(series_id, series_id)}",
                                indicator_type="Trade Deficit Indicator",
                                source="FRED",
                                unit='',  # 暂时留空
                                frequency='',  # 暂时留空
                                metadata={}
                            )
                            indicator.save()
                            saved_count += 1
                    except Exception as e:
                        print(f"⚠️  保存单条记录失败: {e}")
                        continue
                
                print(f"✅ {series_id}: 成功保存 {saved_count} 条新记录")
                
                # 验证数据
                final_count = FredUsIndicator.objects.filter(series_id=series_id).count()
                latest_record = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
                
                if latest_record:
                    print(f"📊 总记录数: {final_count}")
                    print(f"📊 最新数据: {latest_record.value} ({latest_record.date})")
                else:
                    print(f"⚠️  数据验证失败：未找到任何记录")
                    
            else:
                print(f"❌ 未能从API获取到有效数据")
                
        except Exception as e:
            print(f"❌ 抓取指标 {series_id} 时发生错误: {e}")
            continue
    
    print(f"\n{'='*60}")
    print("📈 Trade Deficits 数据抓取完成总结")
    print(f"{'='*60}")
    
    # 生成最终报告
    for series_id in trade_indicators:
        count = FredUsIndicator.objects.filter(series_id=series_id).count()
        latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
        description = indicator_descriptions.get(series_id, series_id)
        
        print(f"📊 {series_id} ({description}): {count} 条记录", end="")
        if latest:
            print(f", 最新: {latest.value} ({latest.date})")
        else:
            print(f", 无数据")
    
    print(f"\n🎯 经济分析师视角总结:")
    print("• 用户优先指标: BOPGSTB, IEABC, BOGZ1FL263061130Q, B235RC1Q027SBEA, MTSDS133FMS")
    print("• 补充贸易指标: NETEXP, IMPGSC1, EXPGSC1")
    print("• 这8个指标构成了完整的贸易逆差和国际收支分析框架")
    print("• 涵盖贸易平衡、经常账户、国际资本流动、财政政策等核心维度")

if __name__ == "__main__":
    fetch_trade_deficits_indicators()
