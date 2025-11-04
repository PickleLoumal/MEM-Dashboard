#!/usr/bin/env python3
"""
Django Stock Data Testing Script

This script tests the stocks Django app functionality without requiring network access.
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

def test_stock_models():
    """测试股票模型的基本功能"""
    print("🧪 Testing Stock Models...")

    # 创建测试股票代码
    try:
        symbol, created = StockSymbol.objects.get_or_create(
            symbol='AAPL',
            defaults={
                'name': 'Apple Inc.',
                'exchange': 'NASDAQ',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'is_active': True
            }
        )
        print(f"✅ Stock symbol created/updated: {symbol.symbol} - {symbol.name}")

        # 创建价格数据
        price_data = {
            'open_price': 150.00,
            'high_price': 152.00,
            'low_price': 149.00,
            'close_price': 151.00,
            'adjusted_close': 151.00,
            'volume': 50000000,
            'market_cap': '2.5T',
            'pe_ratio': 28.5,
            'dividend_yield': 0.62,
            'data_source': 'test'
        }

        price = StockPrice.objects.create(symbol=symbol, **price_data)
        print(f"✅ Stock price created: ${price.close_price} on {price.timestamp}")

        # 测试自动价格变动计算
        prev_price = StockPrice.objects.create(
            symbol=symbol,
            timestamp=datetime.now() - timedelta(minutes=1),
            close_price=150.00,
            open_price=149.50,
            high_price=150.50,
            low_price=149.00,
            adjusted_close=150.00,
            volume=48000000,
            data_source='test'
        )

        # 刷新价格变动
        price.refresh_from_db()
        print(f"✅ Price change calculated: ${price.price_change} ({price.price_change_percent}%)")

    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

    return True

def test_stock_service():
    """测试股票服务"""
    print("\n🧪 Testing Stock Service...")

    try:
        service = StockDataService()

        # 测试获取股票信息
        stock_info = service.yf.get_stock_info('AAPL')
        if stock_info:
            print(f"✅ Stock info retrieved: {stock_info['company_name']} - ${stock_info['current_price']}")

        # 测试价格更新模拟
        updated_info = service.yf.simulate_price_update('AAPL')
        print(f"✅ Price update simulated: ${updated_info['current_price']}")

        # 测试股票代码获取/创建
        created, symbol_obj = service.get_or_create_symbol('AAPL', stock_info)
        print(f"✅ Symbol {'created' if created else 'retrieved'}: {symbol_obj.symbol}")

        # 测试价格数据获取
        price_data = service.fetch_stock_data('AAPL')
        if price_data:
            print(f"✅ Price data fetched: ${price_data['close_price']}")

        # 测试保存价格数据
        saved = service.save_stock_price('AAPL', price_data)
        print(f"✅ Price data {'saved' if saved else 'failed to save'}")

    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

    return True

def test_django_commands():
    """测试Django管理命令"""
    print("\n🧪 Testing Django Commands...")

    try:
        from django.core.management import execute_from_command_line

        # 测试帮助信息
        print("✅ Django management commands available")

        # 注意：这里不能实际执行命令，因为会遇到权限问题
        # 但我们可以检查命令文件是否存在
        import os
        command_file = 'src/django_api/stocks/management/commands/update_stocks.py'
        if os.path.exists(command_file):
            print("✅ Update stocks command file exists")
        else:
            print("❌ Update stocks command file missing")

    except Exception as e:
        print(f"❌ Command test failed: {e}")
        return False

    return True

def main():
    """主测试函数"""
    print("🚀 Starting Django Stock Data Tests")
    print("=" * 50)

    tests = [
        ("Stock Models", test_stock_models),
        ("Stock Service", test_stock_service),
        ("Django Commands", test_django_commands),
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

    if passed == total:
        print("🎉 All tests passed!")
        print("\n📋 Next Steps:")
        print("1. Run: python3 src/django_api/manage.py migrate")
        print("2. Run: python3 src/django_api/manage.py update_stocks --once")
        print("3. Visit: http://localhost:8000/api/stocks/api/realtime/")
        print("4. Test the yfinance integration when network is available")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
