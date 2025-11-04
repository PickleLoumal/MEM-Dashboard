#!/usr/bin/env python3
"""
Check CSI300 Data in Database

This script checks if CSI300 data is properly loaded in the database
and helps diagnose admin interface issues.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    django.setup()

    from csi300.models import CSI300Company

    def check_csi300_data():
        """检查 CSI300 数据"""
        print("🔍 Checking CSI300 Database Data...")
        print("=" * 50)

        # 检查总记录数
        total_companies = CSI300Company.objects.count()
        print(f"📊 Total companies in database: {total_companies}")

        if total_companies == 0:
            print("❌ No companies found in database!")
            print("💡 You need to load CSI300 data first.")
            return False

        # 检查有 ticker 的公司
        companies_with_ticker = CSI300Company.objects.filter(ticker__isnull=False).exclude(ticker='').count()
        print(f"✅ Companies with ticker: {companies_with_ticker}")

        # 检查有价格的公司
        companies_with_price = CSI300Company.objects.filter(price_local_currency__isnull=False).count()
        print(f"💰 Companies with price data: {companies_with_price}")

        # 检查有市值数据的公司
        companies_with_market_cap = CSI300Company.objects.filter(market_cap_local__isnull=False).count()
        print(f"🏢 Companies with market cap: {companies_with_market_cap}")

        # 显示样本数据
        print("
📋 Sample company data:"        sample_companies = CSI300Company.objects.filter(ticker__isnull=False).exclude(ticker='')[:5]

        for i, company in enumerate(sample_companies, 1):
            print(f"\n{i}. {company.ticker} - {company.name}")
            print(f"   Price: {company.price_local_currency} {company.currency or 'N/A'}")
            print(f"   Market Cap: {company.market_cap_local}")
            print(f"   P/E Ratio: {company.pe_ratio_trailing}")
            print(f"   Sector: {company.im_sector}")

        # 检查数据分布
        print("
📈 Data Distribution:"        sectors = CSI300Company.objects.values('im_sector').distinct()
        print(f"   Unique sectors: {len(sectors)}")

        currencies = CSI300Company.objects.values('currency').distinct()
        print(f"   Unique currencies: {len(currencies)}")

        # 检查最近更新
        recent_updates = CSI300Company.objects.order_by('-updated_at')[:3]
        print("
🕒 Recent updates:"        for company in recent_updates:
            print(f"   {company.ticker}: {company.updated_at}")

        return True

    def suggest_admin_improvements():
        """建议 admin 界面改进"""
        print("
💡 Admin Interface Suggestions:"        print("✅ Updated admin.py to include price fields")
        print("✅ Added 'price_local_currency' to list_display")
        print("✅ Added 'Price Information' fieldset")
        print("✅ Enhanced search and filter options")
        print("✅ Added earnings and growth metrics")

        print("
🔧 Next steps:"        print("1. Restart Django server: python3 src/django_api/manage.py runserver")
        print("2. Go to /admin/ in your browser")
        print("3. Navigate to CSI300 > CSI300 companies")
        print("4. Check if price fields are now visible")
        print("5. Use the new filters and search options")

    if __name__ == "__main__":
        if check_csi300_data():
            suggest_admin_improvements()
            print("
🎉 CSI300 data check completed successfully!"        else:
            print("
❌ CSI300 data check found issues. Please load data first."
except Exception as e:
    print(f"❌ Error checking CSI300 data: {e}")
    print("💡 Make sure Django is properly configured and database is accessible.")
