#!/usr/bin/env python3
"""
Debug YFinance Issues

This script helps diagnose issues with yfinance data retrieval.
"""

import sys
import os
from datetime import datetime

def check_yfinance_installation():
    """检查 yfinance 安装情况"""
    print("🔍 Checking YFinance Installation...")
    print("=" * 40)

    try:
        import yfinance as yf
        print("✅ yfinance is installed")

        # 检查版本
        print(f"✅ Version: {yf.__version__}")

        # 测试基本功能
        try:
            # 测试一个简单的股票代码
            ticker = yf.Ticker("AAPL")
            print("✅ Ticker object created successfully")

            # 测试 info 获取
            info = ticker.info
            print(f"✅ Info retrieved for AAPL: {info.get('longName', 'N/A')}")

            return True

        except Exception as e:
            print(f"❌ Error testing yfinance: {e}")
            return False

    except ImportError:
        print("❌ yfinance is not installed")
        print("💡 Install with: pip install yfinance")
        return False

def test_tcl_technology():
    """测试 TCL Technology 数据获取"""
    print("\n📊 Testing TCL Technology (000100.SZ)...")
    print("=" * 40)

    try:
        import yfinance as yf

        ticker_symbol = "000100.SZ"
        print(f"🔍 Getting data for {ticker_symbol}...")

        ticker = yf.Ticker(ticker_symbol)

        # 测试基本信息
        try:
            info = ticker.info
            print("✅ Basic info retrieved:"            print(f"  Name: {info.get('longName', 'N/A')}")
            print(f"  Symbol: {info.get('symbol', 'N/A')}")
            print(f"  Currency: {info.get('currency', 'N/A')}")
            print(f"  Current Price: {info.get('currentPrice', 'N/A')}")
            print(f"  Market Cap: {info.get('marketCap', 'N/A')}")
        except Exception as e:
            print(f"❌ Error getting basic info: {e}")
            return False

        # 测试历史数据
        try:
            print("\n📈 Testing historical data...")
            hist = ticker.history(period="1y")
            if not hist.empty:
                print(f"✅ Historical data available: {len(hist)} records")
                print(f"  52W High: {hist['High'].max()}")
                print(f"  52W Low: {hist['Low'].min()}")
                print(f"  Latest Close: {hist['Close'].iloc[-1]}")
            else:
                print("⚠️ No historical data available")
        except Exception as e:
            print(f"❌ Error getting historical data: {e}")

        # 测试其他字段
        try:
            print("
📋 Testing additional fields..."            test_fields = [
                'trailingPE', 'dividendYield', 'sector', 'industry',
                'fiftyTwoWeekHigh', 'fiftyTwoWeekLow', 'volume'
            ]

            for field in test_fields:
                value = info.get(field, 'N/A')
                print(f"  {field}: {value}")

        except Exception as e:
            print(f"❌ Error testing additional fields: {e}")

        return True

    except Exception as e:
        print(f"❌ Error testing TCL Technology: {e}")
        return False

def check_network_connectivity():
    """检查网络连接"""
    print("\n🌐 Checking Network Connectivity...")
    print("=" * 40)

    try:
        import urllib.request
        import socket

        # 测试基本的网络连接
        try:
            # 测试到 Yahoo Finance 的连接
            socket.setdefaulttimeout(10)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('finance.yahoo.com', 443))
            sock.close()

            if result == 0:
                print("✅ Can connect to finance.yahoo.com")
            else:
                print("❌ Cannot connect to finance.yahoo.com")
                return False

        except Exception as e:
            print(f"❌ Network connection test failed: {e}")
            return False

        # 测试 DNS 解析
        try:
            ip = socket.gethostbyname('finance.yahoo.com')
            print(f"✅ DNS resolution works: {ip}")
        except Exception as e:
            print(f"❌ DNS resolution failed: {e}")
            return False

        return True

    except ImportError:
        print("❌ urllib not available for network testing")
        return False

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 Solutions and Recommendations...")
    print("=" * 40)

    print("If yfinance is not working:")
    print("1. Check internet connection")
    print("2. Install/update yfinance: pip install --upgrade yfinance")
    print("3. Check firewall/proxy settings")
    print("4. Try a different stock symbol for testing")

    print("\nAlternative approaches:")
    print("1. Use a different financial data API (Alpha Vantage, IEX Cloud)")
    print("2. Use web scraping for specific data needs")
    print("3. Use local/mock data for development")
    print("4. Set up a proxy or VPN if needed")

    print("\nFor TCL Technology specifically:")
    print("1. The ticker '000100.SZ' might not be available in all regions")
    print("2. Try alternative tickers: '000100' or check Yahoo Finance website")
    print("3. Consider using a different Chinese stock for testing")

def main():
    """主函数"""
    print("🔧 YFinance Debugging Tool")
    print("=" * 30)

    # 检查安装
    yfinance_ok = check_yfinance_installation()

    # 检查网络
    network_ok = check_network_connectivity()

    # 测试 TCL Technology
    if yfinance_ok and network_ok:
        tcl_ok = test_tcl_technology()
    else:
        tcl_ok = False
        print("\n⚠️ Skipping TCL Technology test due to setup issues")

    # 提供建议
    suggest_solutions()

    print("\n" + "=" * 30)
    print("📋 Summary:")
    print(f"• YFinance Installation: {'✅' if yfinance_ok else '❌'}")
    print(f"• Network Connectivity: {'✅' if network_ok else '❌'}")
    print(f"• TCL Technology Test: {'✅' if tcl_ok else '❌'}")

    if yfinance_ok and network_ok and not tcl_ok:
        print("\n🔍 TCL Technology specific issues detected")
        print("💡 Try alternative tickers or check Yahoo Finance availability")

    return yfinance_ok and network_ok

if __name__ == "__main__":
    success = main()
    print(f"\nExit code: {0 if success else 1}")
    sys.exit(0 if success else 1)
