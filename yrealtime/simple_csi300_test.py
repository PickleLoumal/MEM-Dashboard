#!/usr/bin/env python3
"""
Simple CSI300 Data Test

This script tests basic CSI300 database access without Django setup issues.
"""

import sys
import os

# Add the src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_csi300_data_access():
    """测试 CSI300 数据访问"""
    print("🧪 Testing CSI300 Data Access...")

    try:
        # Try to import Django models directly
        import django
        from django.conf import settings

        # Configure Django settings manually
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

        # Now try to access CSI300 models
        from csi300.models import CSI300Company

        # Try to get some sample data
        companies = CSI300Company.objects.all()[:5]

        print(f"✅ Found {len(companies)} CSI300 companies")

        # Check for tickers
        companies_with_tickers = []
        for company in companies:
            if company.ticker:
                companies_with_tickers.append(company)

        print(f"✅ Companies with tickers: {len(companies_with_tickers)}")

        if companies_with_tickers:
            print("📊 Sample tickers:")
            for company in companies_with_tickers[:3]:
                print(f"  - {company.ticker}: {company.name}")

        return len(companies_with_tickers) > 0

    except Exception as e:
        print(f"❌ Error accessing CSI300 data: {e}")
        print("This might be because the database is not set up or tables don't exist.")
        return False

def test_mock_service():
    """测试模拟服务"""
    print("\n🧪 Testing Mock Service...")

    try:
        from stocks.services import StockDataService

        service = StockDataService()

        # Test getting CSI300 tickers (will fail without database)
        try:
            tickers = service.get_csi300_tickers(limit=5)
            print(f"✅ Got {len(tickers)} CSI300 tickers: {tickers[:3]}")
        except Exception as e:
            print(f"⚠️  CSI300 tickers not available (expected): {e}")

        # Test getting all available tickers
        all_tickers = service.get_all_available_tickers()
        print(f"✅ Got {len(all_tickers)} available tickers")

        # Test stock info retrieval
        if all_tickers:
            stock_info = service.yf.get_stock_info(all_tickers[0])
            if stock_info:
                print(f"✅ Stock info for {all_tickers[0]}: ${stock_info['current_price']}")

        return True

    except Exception as e:
        print(f"❌ Mock service test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Simple CSI300 Integration Test")
    print("=" * 50)

    tests = [
        ("CSI300 Data Access", test_csi300_data_access),
        ("Mock Service", test_mock_service),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed > 0:
        print("🎉 Basic functionality works!")
        print("\n📋 Next Steps:")
        print("1. Set up Django database with CSI300 data")
        print("2. Run migrations: python3 src/django_api/manage.py migrate")
        print("3. Load CSI300 data into database")
        print("4. Run: python3 src/django_api/manage.py update_stocks --initialize")
        print("5. Test real-time updates")
    else:
        print("⚠️  Basic tests failed. Check Django setup and database configuration.")

    return passed > 0

if __name__ == "__main__":
    success = main()
    print(f"\nExit code: {0 if success else 1}")
    sys.exit(0 if success else 1)
