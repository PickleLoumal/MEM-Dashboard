#!/usr/bin/env python3
"""
抓取债务指标数据到Django数据库
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

def fetch_household_debt_indicators():
    """抓取家庭债务指标数据"""
    print("🔄 开始抓取家庭债务指标数据...")
    
    # 要抓取的7个债务指标
    debt_indicators = [
        'HDTGPDUSQ163N',  # Household Debt to GDP
        'TDSP',           # Debt Service Ratio  
        'MDOAH',          # Mortgage Debt Outstanding
        'RCCCBBALTOT',    # Credit Card Balances
        'SLOASM',         # Student Loans
        'TOTALSL',        # Total Consumer Credit
        'DTCOLNVHFNM'     # Total Household Debt
    ]
    
    fetcher = UsFredDataFetcher()
    
    for series_id in debt_indicators:
        print(f"\n=== 抓取指标: {series_id} ===")
        
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
                            
                            # 创建新记录 - 使用正确的字段
                            indicator = FredUsIndicator(
                                series_id=series_id,
                                date=obs['date'],
                                value=value,
                                indicator_name=f"US {series_id}",
                                indicator_type="Debt Indicator",
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
                print(f"❌ {series_id}: 未能获取到API数据")
                
        except Exception as e:
            print(f"❌ {series_id}: 抓取失败 - {e}")
            continue
    
    print("\n" + "="*60)
    print("📈 抓取完成! 数据库状态汇总:")
    
    for series_id in debt_indicators:
        count = FredUsIndicator.objects.filter(series_id=series_id).count()
        if count > 0:
            latest = FredUsIndicator.objects.filter(series_id=series_id).order_by('-date').first()
            print(f"✅ {series_id}: {count} 条记录, 最新: {latest.value} ({latest.date})")
        else:
            print(f"❌ {series_id}: 无数据")

if __name__ == "__main__":
    fetch_household_debt_indicators()
