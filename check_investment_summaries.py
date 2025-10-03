#!/usr/bin/env python3
"""
检查CSI300投资摘要数据的脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('/Volumes/Pickle Samsung SSD/MEM Dashboard 2/src/django_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
django.setup()

from csi300.models import CSI300Company, CSI300InvestmentSummary

def check_investment_summaries():
    print("=== CSI300投资摘要数据检查 ===")
    
    # 检查投资摘要总数
    total_summaries = CSI300InvestmentSummary.objects.count()
    print(f"投资摘要总数: {total_summaries}")
    
    if total_summaries > 0:
        print("\n投资摘要详情:")
        for summary in CSI300InvestmentSummary.objects.all()[:5]:  # 显示前5条
            print(f"  - ID: {summary.id}, 公司ID: {summary.company.id}, 公司名称: {summary.company.name}")
    
    # 检查公司总数
    total_companies = CSI300Company.objects.count()
    print(f"\n公司总数: {total_companies}")
    
    # 检查有投资摘要的公司
    companies_with_summaries = CSI300Company.objects.filter(investment_summary__isnull=False).count()
    print(f"有投资摘要的公司数: {companies_with_summaries}")
    
    if companies_with_summaries > 0:
        print("\n有投资摘要的公司:")
        for company in CSI300Company.objects.filter(investment_summary__isnull=False)[:5]:
            print(f"  - 公司ID: {company.id}, 名称: {company.name}, 代码: {company.ticker}")

if __name__ == "__main__":
    check_investment_summaries()
