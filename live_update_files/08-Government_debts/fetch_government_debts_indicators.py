#!/usr/bin/env python3
"""
抓取Government Debts指标数据到Django数据库
基于实际使用的fetch_debt_indicators.py
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

def fetch_government_debts_indicators():
    """抓取Government Debts指标数据"""
    print("🔄 开始抓取Government Debts指标数据...")
    
    # 要抓取的8个指标 - 确保满足8个指标要求
    government_debts_indicators = [
        'GFDEBTN',       # Federal Debt: Total Public Debt
        'GFDEGDQ188S',   # Federal Debt: Total Public Debt as Percent of GDP
        'MTSDS133FMS',   # Federal Surplus or Deficit [-]
        'LNU00024230',   # Population Level - 55 Yrs. & over
        'FYGFD',         # Gross Federal Debt
        'FYOIGDA188S',   # Federal Outlays: Interest as Percent of GDP
        'FYGFGDQ188S',   # Federal Debt Held by the Public as Percent of GDP
        'TOTALGOV'       # Total Consumer Credit Owned by Federal Government
    ]
    
    fetcher = UsFredDataFetcher()
    
    for series_id in government_debts_indicators:
        print(f"\n=== 抓取指标: {series_id} ===")
        try:
            # 检查当前数据库中是否已有数据
            existing_count = FredUsIndicator.objects.filter(series_id=series_id).count()
            print(f"数据库中现有记录数: {existing_count}")
            
            # 使用基础类的get_series_observations方法抓取历史数据
            print(f"正在从FRED API抓取 {series_id} 数据...")
            observations = fetcher.get_series_observations(series_id, limit=1000)
            
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
                                indicator_name=f"US {series_id}",
                                indicator_type="Government Debt Indicator",
                                source='FRED',
                                metadata={
                                    'country': 'US',
                                    'category': 'Government Debts',
                                    'original_series_id': series_id
                                }
                            )
                            indicator.save()
                            saved_count += 1
                            
                    except Exception as e:
                        print(f"保存单个数据点失败: {e}")
                        continue
                
                print(f"✅ {series_id} 保存成功: 新增 {saved_count} 条记录")
                
                # 检查最新数据
                latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
                earliest = FredUsIndicator.objects.filter(series_id=series_id).order_by('date').first()
                
                if latest:
                    print(f"   最新数据: {latest.value} ({latest.date})")
                if earliest:
                    print(f"   最早数据: {earliest.value} ({earliest.date})")
            else:
                print(f"❌ {series_id} 无法获取数据")
                
        except Exception as e:
            print(f"❌ {series_id} 抓取异常: {e}")
    
    print("\n" + "="*60)
    print("📈 抓取完成! 数据库状态汇总:")
    
    for series_id in government_debts_indicators:
        count = FredUsIndicator.objects.filter(series_id=series_id).count()
        latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
        if latest:
            print(f"  {series_id}: {count} 条记录, 最新: {latest.value} ({latest.date})")
        else:
            print(f"  {series_id}: 0 条记录")

if __name__ == "__main__":
    fetch_government_debts_indicators()
