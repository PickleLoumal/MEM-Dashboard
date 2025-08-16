#!/usr/bin/env python3
"""
抓取Private Sector Corporate Debts企业债务指标数据到Django数据库
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

def fetch_private_sector_corporate_debts_indicators():
    """抓取Private Sector Corporate Debts指标数据"""
    print("🔄 开始抓取Private Sector Corporate Debts指标数据...")
    print("📊 从资深经济分析师角度精选的8个核心指标")
    
    # 8个验证过的指标（您指定的4个优先 + 4个补充）
    private_sector_corporate_debts_indicators = [
        # 用户指定的4个优先核心指标
        'USREC',          # NBER Recession Indicators
        'FPCPITOTLZGUSA', # Inflation, consumer prices
        'BAMLH0A0HYM2',   # ICE BofA US High Yield Index Option-Adjusted Spread
        'WPC',            # Assets: Liquidity and Credit Facilities
        
        # 补充指标 - 达到8个指标要求
        'BCNSDODNS',      # Nonfinancial Corporate Business; Debt Securities and Loans
        'AAA',            # Moody's Seasoned Aaa Corporate Bond Yield
        'BAA',            # Moody's Seasoned Baa Corporate Bond Yield
        'NCBCMDPMVCE'     # Nonfinancial Corporate Business; Debt as % of Market Value
    ]
    
    # 指标中文描述（用于数据库记录）
    indicator_descriptions = {
        # 用户指定的4个优先指标
        'USREC': 'NBER经济衰退指标',
        'FPCPITOTLZGUSA': '美国消费者价格通胀率',
        'BAMLH0A0HYM2': 'ICE BofA美国高收益指数期权调整利差',
        'WPC': '资产流动性和信贷便利：主要信贷贷款',
        
        # 补充指标
        'BCNSDODNS': '非金融企业：债券和贷款负债水平',
        'AAA': '穆迪季节性Aaa级企业债券收益率',
        'BAA': '穆迪季节性Baa级企业债券收益率',
        'NCBCMDPMVCE': '非金融企业债务占股权市值比例'
    }
    
    fetcher = UsFredDataFetcher()
    
    for series_id in private_sector_corporate_debts_indicators:
        print(f"\n=== 抓取指标: {series_id} ({indicator_descriptions.get(series_id, 'Corporate Debt Indicator')}) ===")
        
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
                                indicator_type="Private Sector Corporate Debt Indicator",
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
    print("📈 Private Sector Corporate Debts 数据抓取完成总结")
    print(f"{'='*60}")
    
    # 生成最终报告
    for series_id in private_sector_corporate_debts_indicators:
        count = FredUsIndicator.objects.filter(series_id=series_id).count()
        latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
        description = indicator_descriptions.get(series_id, series_id)
        
        print(f"📊 {series_id} ({description}): {count} 条记录", end="")
        if latest:
            print(f", 最新: {latest.value} ({latest.date})")
        else:
            print(f", 无数据")
    
    print(f"\n🎯 经济分析师视角总结:")
    print("• 用户优先指标: USREC, FPCPITOTLZGUSA, BAMLH0A0HYM2, WPC")
    print("• 补充企业债务指标: BCNSDODNS, AAA, BAA, NCBCMDPMVCE")
    print("• 这8个指标构成了完整的企业债务和信用风险分析框架")
    print("• 涵盖经济周期、通胀环境、信用利差、流动性、企业负债等核心维度")

if __name__ == "__main__":
    fetch_private_sector_corporate_debts_indicators()
