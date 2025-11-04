#!/usr/bin/env python3
"""
CSI300 Real-time Data Integration Test

This script tests the integration between CSI300 database and yfinance real-time updates.
It reads stock tickers from the CSI300 database and updates them with real-time data.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_api.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Initialize Django
django.setup()

from stocks.models import StockSymbol, StockPrice, StockUpdateLog
from stocks.services import StockDataService

def test_csi300_ticker_extraction():
    """测试从 CSI300 数据库提取股票代码"""
    print("🧪 Testing CSI300 Ticker Extraction...")

    try:
        service = StockDataService()

        # 获取 CSI300 股票代码
        csi300_tickers = service.get_csi300_tickers(limit=10)

        print(f"✅ Found {len(csi300_tickers)} CSI300 tickers:")
        for i, ticker in enumerate(csi300_tickers[:10], 1):
            print(f"  {i}. {ticker}")

        if not csi300_tickers:
            print("❌ No CSI300 tickers found in database")
            return False

        # 获取所有可用股票代码
        all_tickers = service.get_all_available_tickers()
        print(f"✅ Total available tickers: {len(all_tickers)}")

        return True

    except Exception as e:
        print(f"❌ CSI300 ticker extraction failed: {e}")
        return False

def test_csi300_stock_initialization():
    """测试 CSI300 股票初始化"""
    print("\n🧪 Testing CSI300 Stock Initialization...")

    try:
        service = StockDataService()

        # 初始化股票符号
        initialized = service.initialize_stock_symbols(use_csi300=True)

        print(f"✅ Initialized {initialized} CSI300 stocks")

        # 显示已创建的股票符号
        symbols = StockSymbol.objects.filter(is_active=True).order_by('symbol')[:10]
        print("✅ Created symbols in database:")
        for symbol in symbols:
            print(f"  {symbol.symbol} - {symbol.name}")

        return True

    except Exception as e:
        print(f"❌ CSI300 stock initialization failed: {e}")
        return False

def test_realtime_data_update():
    """测试实时数据更新"""
    print("\n🧪 Testing Real-time Data Update...")

    try:
        service = StockDataService()

        # 获取 CSI300 股票代码
        csi300_tickers = service.get_csi300_tickers(limit=5)  # 只测试前5个

        if not csi300_tickers:
            print("❌ No CSI300 tickers available for testing")
            return False

        print(f"📊 Testing with {len(csi300_tickers)} CSI300 stocks:")
        for ticker in csi300_tickers:
            print(f"  - {ticker}")

        # 执行更新
        result = service.update_all_stocks(csi300_tickers)

        print("✅ Update completed:")
        print(f"  - Successful: {result['successful']}")
        print(f"  - Failed: {result['failed']}")
        print(f"  - Records updated: {result['updated_count']}")

        if result['errors']:
            print("❌ Errors encountered:")
            for error in result['errors'][:3]:  # 只显示前3个错误
                print(f"  - {error['symbol']}: {error['error']}")

        # 显示最新的价格数据
        latest_prices = StockPrice.objects.order_by('-timestamp')[:5]
        print("✅ Latest price data in database:")
        for price in latest_prices:
            print(f"  {price.symbol.symbol}: ${price.close_price} "
                  f"({price.price_change:+.2f}%) at {price.timestamp}")

        return result['successful'] > 0

    except Exception as e:
        print(f"❌ Real-time data update failed: {e}")
        return False

def test_api_endpoints():
    """测试 API 端点"""
    print("\n🧪 Testing API Endpoints...")

    try:
        # 测试获取实时股票数据
        from stocks.views import realtime_stocks, stock_summary
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser

        factory = RequestFactory()

        # 测试实时股票数据
        request = factory.get('/api/stocks/api/realtime/')
        request.user = AnonymousUser()

        response = realtime_stocks(request)
        if response.status_code == 200:
            data = response.data
            print(f"✅ Real-time API: {data['count']} stocks returned")
        else:
            print(f"❌ Real-time API failed: {response.status_code}")
            return False

        # 测试股票汇总
        request = factory.get('/api/stocks/api/summary/')
        request.user = AnonymousUser()

        response = stock_summary(request)
        if response.status_code == 200:
            data = response.data
            print("✅ Summary API:")
            print(f"  - Total stocks: {data['total_stocks']}")
            print(f"  - Gainers: {data['gainers']}")
            print(f"  - Losers: {data['losers']}")
            print(f"  - Market sentiment: {data['market_sentiment']}")
        else:
            print(f"❌ Summary API failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 CSI300 Real-time Integration Test")
    print("=" * 60)

    tests = [
        ("CSI300 Ticker Extraction", test_csi300_ticker_extraction),
        ("CSI300 Stock Initialization", test_csi300_stock_initialization),
        ("Real-time Data Update", test_realtime_data_update),
        ("API Endpoints", test_api_endpoints),
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

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed!")
        print("\n📋 Next Steps:")
        print("1. Run: python3 src/django_api/manage.py migrate")
        print("2. Run: python3 src/django_api/manage.py update_stocks --initialize")
        print("3. Run: python3 src/django_api/manage.py update_stocks --duration 300")
        print("4. Visit: http://localhost:8000/api/stocks/api/realtime/")
        print("5. When network is available, replace MockYFinance with real yfinance")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("- Ensure CSI300 data is loaded in the database")
        print("- Check database permissions and models")
        print("- Verify Django settings and installed apps")

    return passed == total

def main():
    """主函数"""
    return run_comprehensive_test()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
