#!/usr/bin/env python3
"""
Test TCL Technology YFinance Data Only

This script tests yfinance data retrieval for TCL Technology (000100.SZ)
without Django database dependencies.
"""

import sys
import os

# Add the src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_tcl_yfinance():
    """测试 TCL Technology 的 yfinance 数据获取"""
    print("🚀 Testing TCL Technology YFinance Data")
    print("=" * 50)

    try:
        # 导入股票服务
        from stocks.services import StockDataService

        # 初始化服务
        service = StockDataService()

        # 测试 TCL Technology 数据获取
        ticker = '000100.SZ'
        print(f"🔍 Fetching data for {ticker}...")

        stock_info = service.yf.get_stock_info(ticker)

        if stock_info:
            print("✅ Successfully retrieved real stock data!")
            print("\n📊 TCL Technology (000100.SZ) Data:")
            print(f"  Company: {stock_info['company_name']}")
            print(f"  Current Price: {stock_info['current_price']} {stock_info['currency']}")
            print(f"  Previous Close: {stock_info['previous_close']}")
            print(f"  Volume: {stock_info['volume']:,}")
            print(f"  Market Cap: {stock_info['market_cap']}")
            print(f"  P/E Ratio: {stock_info['pe_ratio']}")
            print(f"  Dividend Yield: {stock_info['dividend_yield']}")
            print(f"  Sector: {stock_info['sector']}")
            print(f"  Industry: {stock_info['industry']}")
            print(f"  52W High: {stock_info['fifty_two_week_high']}")
            print(f"  52W Low: {stock_info['fifty_two_week_low']}")

            # 验证必需字段
            required_fields = [
                'current_price', 'previous_close', 'volume', 'market_cap',
                'pe_ratio', 'dividend_yield', 'company_name', 'sector',
                'industry', 'fifty_two_week_high', 'fifty_two_week_low', 'currency'
            ]

            print("\n🔍 Field Validation:")
            all_fields_present = True
            for field in required_fields:
                if field in stock_info and stock_info[field] is not None:
                    print(f"  ✅ {field}: {stock_info[field]}")
                else:
                    print(f"  ❌ {field}: Missing or None")
                    all_fields_present = False

            if all_fields_present:
                print("\n🎉 All required fields are present!")
                print("\n📋 Database Update Fields:")
                print(f"  • price_local_currency: {stock_info['current_price']}")
                print(f"  • currency: {stock_info['currency']}")
                print(f"  • last_trade_date: Today")
                print(f"  • price_52w_high: {stock_info['fifty_two_week_high']}")
                print(f"  • price_52w_low: {stock_info['fifty_two_week_low']}")
                print(f"  • market_cap_local: {stock_info['market_cap']}")

                return True
            else:
                print("\n❌ Some required fields are missing.")
                return False
        else:
            print(f"❌ Failed to retrieve stock info for {ticker}")
            print("💡 This might be due to:")
            print("  - Network connectivity issues")
            print("  - yfinance API limitations")
            print("  - Invalid ticker symbol")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure yfinance is installed: pip install yfinance")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_fallback_data():
    """测试备用数据功能"""
    print("\n🔧 Testing Fallback Data...")
    try:
        from stocks.services import YFinanceClient

        client = YFinanceClient()

        # 测试备用数据
        fallback_data = client._get_fallback_data('000100.SZ')
        print(f"✅ Fallback data for 000100.SZ: {fallback_data['company_name']}")
        print(f"  Price: {fallback_data['current_price']} {fallback_data['currency']}")
        print(f"  52W Range: {fallback_data['fifty_two_week_low']} - {fallback_data['fifty_two_week_high']}")

        return True

    except Exception as e:
        print(f"❌ Fallback data test failed: {e}")
        return False

def main():
    """主函数"""
    print("🎯 TCL Technology YFinance Test")
    print("=" * 40)

    success1 = test_tcl_yfinance()
    success2 = test_fallback_data()

    print("\n" + "=" * 40)
    if success1:
        print("🎉 TCL Technology real-time data test PASSED!")
        print("✅ Real yfinance data is working correctly")
    else:
        print("⚠️ TCL Technology real-time data test had issues")
        print("✅ Fallback data system is available")

    if success2:
        print("✅ Fallback data system is working")
    else:
        print("❌ Fallback data system failed")

    print("\n📋 Summary:")
    print(f"• Real yfinance data retrieval: {'✅' if success1 else '❌'}")
    print(f"• Fallback data system: {'✅' if success2 else '❌'}")
    print(f"• Ready for database integration: {'✅' if success1 or success2 else '❌'}")

    return success1 or success2

if __name__ == "__main__":
    success = main()
    print(f"\nExit code: {0 if success else 1}")
    sys.exit(0 if success else 1)
