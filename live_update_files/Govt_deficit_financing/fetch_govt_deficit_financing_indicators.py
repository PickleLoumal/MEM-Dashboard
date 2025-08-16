#!/usr/bin/env python3
"""
Government Deficit Financing 指标数据抓取脚本
从FRED API获取数据并存储到Django数据库
"""

import os
import sys
import django
from pathlib import Path

# 配置Django环境
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root / "src" / "django_api"))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
django.setup()

from fred_us.data_fetcher import UsFredDataFetcher
from fred_us.models import FredUsIndicator
from datetime import datetime

def fetch_govt_deficit_financing_indicators():
    """
    抓取Government Deficit Financing相关的8个指标数据
    """
    print("=== Government Deficit Financing 数据抓取开始 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 8个指标配置
    govt_deficit_financing_indicators = [
        # 用户指定的4个核心指标
        'GFDEBTN',           # Federal Debt: Total Public Debt
        'GFDEGDQ188S',       # Federal Debt: Total Public Debt as Percent of GDP
        'MTSDS133FMS',       # Federal Surplus or Deficit [-]
        'W006RC1Q027SBEA',   # Federal government current tax receipts
        
        # 经济分析师补充的4个关键指标
        'FYONET',            # Federal Net Outlays
        'FGEXPND',           # Federal Government: Current Expenditures
        'FGRECPT',           # Federal Government: Current Receipts
        'EXCSRESNW'          # Excess Reserves of Depository Institutions
    ]
    
    fetcher = UsFredDataFetcher()
    total_new_records = 0
    
    for i, series_id in enumerate(govt_deficit_financing_indicators, 1):
        print(f"\n📊 [{i}/8] 正在抓取 {series_id}...")
        
        try:
            # 检查现有数据
            existing_count = FredUsIndicator.objects.filter(series_id=series_id).count()
            print(f"   数据库中现有记录数: {existing_count}")
            
            # 使用基础类的get_series_observations方法
            print(f"   正在从FRED API抓取 {series_id} 数据...")
            observations = fetcher.get_series_observations(series_id, limit=500)
            
            if observations:
                print(f"   ✅ 从API获取到 {len(observations)} 条观测数据")
                
                # 保存到数据库
                saved_count = 0
                for obs in observations:
                    try:
                        # 跳过无效数据
                        if obs['value'] == '.' or obs['value'] == '' or obs['value'] is None:
                            continue
                            
                        # 创建或更新数据库记录
                        indicator_obj, created = FredUsIndicator.objects.update_or_create(
                            series_id=series_id,
                            date=obs['date'],
                            defaults={
                                'value': float(obs['value']),
                                'indicator_name': f"US {series_id}",
                                'indicator_type': 'govt_deficit_financing'
                            }
                        )
                        
                        if created:
                            saved_count += 1
                            
                    except (ValueError, TypeError) as e:
                        print(f"   ⚠️  跳过无效数据: {obs['date']} = {obs['value']}")
                        continue
                
                total_new_records += saved_count
                final_count = FredUsIndicator.objects.filter(series_id=series_id).count()
                
                print(f"   💾 新增记录数: {saved_count}")
                print(f"   📈 总记录数: {existing_count} → {final_count}")
                
            else:
                print(f"   ❌ 无法从API获取数据")
            
        except Exception as e:
            print(f"   ❌ {series_id}: 抓取失败 - {str(e)}")
            continue
    
    print("\n" + "="*60)
    print("📊 抓取完成统计:")
    print(f"   处理指标数: {len(govt_deficit_financing_indicators)}")
    print(f"   新增记录数: {total_new_records}")
    
    # 最终数据库状态报告
    print(f"\n📋 数据库最终状态:")
    total_records = 0
    
    for series_id in govt_deficit_financing_indicators:
        count = FredUsIndicator.objects.filter(series_id=series_id).count()
        latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
        total_records += count
        
        print(f"   {series_id}: {count} 条记录, 最新: {latest.value if latest else '无数据'} ({latest.date if latest else '无日期'})")
    
    print(f"\n📊 Government Deficit Financing 总记录数: {total_records}")
    print(f"✅ 数据抓取完成! ({datetime.now().strftime('%H:%M:%S')})")

if __name__ == "__main__":
    fetch_govt_deficit_financing_indicators()
