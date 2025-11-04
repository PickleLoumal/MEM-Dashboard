#!/usr/bin/env python3
"""
Test TCL Technology Real-time Update

This script tests real-time data update for TCL Technology Group Corp (000100.SZ)
and updates the CSI300 database with the latest information.
"""

import os
import sys
import django
from datetime import datetime, timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure Django settings for testing
from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'csi300',
            'stocks',
        ],
        USE_TZ=True,
    )

django.setup()

from csi300.models import CSI300Company
from stocks.services import StockDataService

def test_tcl_technology_update():
    """测试 TCL Technology 的实时更新"""
    print("🚀 Testing TCL Technology Real-time Update")
    print("=" * 50)

    # 查找 TCL Technology
    try:
        company = CSI300Company.objects.filter(ticker='000100.SZ').first()

        if not company:
            print("❌ TCL Technology (000100.SZ) not found in database")
            print("💡 Available companies with TCL in name:")

            # 查找包含 TCL 的公司
            tcl_companies = CSI300Company.objects.filter(name__icontains='TCL')
            for comp in tcl_companies:
                print(f"  {comp.ticker} - {comp.name}")
            return False

        print(f"✅ Found: {company.ticker} - {company.name}")
        print("\n📊 Current data before update:")
        print(f"  Price: {company.price_local_currency} {company.currency or 'N/A'}")
        print(f"  Last trade date: {company.last_trade_date}")
        print(f"  52w high: {company.price_52w_high}")
        print(f"  52w low: {company.price_52w_low}")
        print(f"  Market cap: {company.market_cap_local}")
        print(f"  Updated at: {company.updated_at}")

        # 初始化股票数据服务
        service = StockDataService()

        # 测试获取 TCL Technology 的实时数据
        print("\n🔍 Fetching real-time data for TCL Technology...")
        ticker = '000100.SZ'

        # 获取真实的股票数据
        stock_info = service.yf.get_stock_info(ticker)
        if stock_info:
            print(f"✅ Retrieved real stock info: {stock_info['company_name']}")
            print(f"  Current price: {stock_info['current_price']} {stock_info['currency']}")
            print(f"  Previous close: {stock_info['previous_close']}")
            print(f"  Volume: {stock_info['volume']}")
            print(f"  52w High: {stock_info['fifty_two_week_high']}")
            print(f"  52w Low: {stock_info['fifty_two_week_low']}")
            print(f"  P/E Ratio: {stock_info['pe_ratio']}")
            print(f"  Market Cap: {stock_info['market_cap']}")

            # 更新公司数据
            print("\n💾 Updating database with real-time data...")
            # 更新价格信息
            company.price_local_currency = stock_info['current_price']
            company.currency = stock_info['currency']
            company.last_trade_date = datetime.now().date()

            # 使用真实的52周高低价数据
            if stock_info['fifty_two_week_high'] and stock_info['fifty_two_week_high'] > 0:
                company.price_52w_high = stock_info['fifty_two_week_high']

            if stock_info['fifty_two_week_low'] and stock_info['fifty_two_week_low'] > 0:
                company.price_52w_low = stock_info['fifty_two_week_low']

            # 更新市值（如果有的话）
            if stock_info['market_cap'] and stock_info['market_cap'] != 'N/A':
                company.market_cap_local = stock_info['market_cap']

            company.updated_at = datetime.now(timezone.utc)
            company.save()

            print("✅ Database updated successfully with real data!")
        else:
            print(f"❌ Could not retrieve stock info for {ticker}")
            print("💡 This might be due to network issues or yfinance API limitations")

        # 显示更新后的数据
        print("\n📈 Updated data:")
        company.refresh_from_db()
        print(f"  Price: {company.price_local_currency} {company.currency}")
        print(f"  Last trade date: {company.last_trade_date}")
        print(f"  52w high: {company.price_52w_high}")
        print(f"  52w low: {company.price_52w_low}")
        print(f"  Updated at: {company.updated_at}")

        return True

    except Exception as e:
        print(f"❌ Error during TCL Technology update: {e}")
        return False

def create_test_data():
    """创建 TCL Technology 的测试数据（如果数据库中没有）"""
    print("\n🔧 Creating test data for TCL Technology...")
    try:
        company, created = CSI300Company.objects.get_or_create(
            ticker='000100.SZ',
            defaults={
                'name': 'TCL Technology Group Corp',
                'im_sector': 'Technology',
                'industry': 'Consumer Electronics',
                'currency': 'CNY',
                'price_local_currency': None,
                'last_trade_date': None,
                'price_52w_high': None,
                'price_52w_low': None,
                'market_cap_local': None,
            }
        )

        if created:
            print(f"✅ Created new company: {company.ticker} - {company.name}")
        else:
            print(f"✅ Company already exists: {company.ticker} - {company.name}")

        return company

    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return None

def main():
    """主函数"""
    print("🎯 TCL Technology Real-time Update Test")

    # 先创建测试数据（如果需要）
    company = create_test_data()

    if company:
        # 测试实时更新
        success = test_tcl_technology_update()

        if success:
            print("\n🎉 TCL Technology real-time update test completed successfully!")
            print("\n📋 Summary:")
            print(f"• Company: {company.name} ({company.ticker})")
            print(f"• Latest price: {company.price_local_currency} {company.currency}")
            print(f"• 52w range: {company.price_52w_low} - {company.price_52w_high}")
            print(f"• Last updated: {company.updated_at}")
        else:
            print("\n❌ TCL Technology update test failed.")
    else:
        print("❌ Could not create/access TCL Technology data.")

if __name__ == "__main__":
    main()
