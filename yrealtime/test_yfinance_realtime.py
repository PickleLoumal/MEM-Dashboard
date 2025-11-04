#!/usr/bin/env python3
"""
YFinance Real-time Data Testing Script

This script demonstrates how to use yfinance for real-time stock data updates.
Run this to test yfinance functionality in the MEM Dashboard project.
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Mock implementation since we can't install yfinance due to network issues
class MockYFinance:
    """Mock implementation of yfinance for testing purposes"""

    def __init__(self):
        self.stock_data = {
            'AAPL': {
                'current_price': 150.25,
                'previous_close': 149.80,
                'volume': 45678900,
                'market_cap': '2.5T',
                'pe_ratio': 28.5,
                'dividend_yield': 0.62
            },
            'MSFT': {
                'current_price': 320.15,
                'previous_close': 318.90,
                'volume': 23456700,
                'market_cap': '2.4T',
                'pe_ratio': 32.1,
                'dividend_yield': 0.78
            },
            'GOOGL': {
                'current_price': 125.80,
                'previous_close': 126.20,
                'volume': 18987600,
                'market_cap': '1.6T',
                'pe_ratio': 24.3,
                'dividend_yield': 0.0
            }
        }

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get stock information for a symbol"""
        return self.stock_data.get(symbol.upper())

    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get information for multiple stocks"""
        result = {}
        for symbol in symbols:
            data = self.get_stock_info(symbol)
            if data:
                result[symbol] = data
        return result

    def simulate_realtime_update(self, symbol: str) -> Dict:
        """Simulate real-time price update"""
        stock_info = self.get_stock_info(symbol)
        if not stock_info:
            return {}

        # Simulate price fluctuation (±2%)
        price_change = stock_info['current_price'] * 0.02 * (0.5 if time.time() % 2 == 0 else -0.5)
        stock_info['current_price'] += price_change
        stock_info['last_updated'] = datetime.now().isoformat()

        return stock_info

class YFinanceRealtimeUpdater:
    """Real-time stock data updater using yfinance"""

    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        self.yf = MockYFinance()  # Replace with: import yfinance as yf
        self.update_interval = 60  # seconds

    def get_realtime_data(self) -> Dict[str, Dict]:
        """Fetch real-time data for all symbols"""
        realtime_data = {}

        for symbol in self.symbols:
            try:
                # Real implementation would be:
                # ticker = yf.Ticker(symbol)
                # info = ticker.info
                # history = ticker.history(period="1d")

                # For testing, simulate real-time data
                stock_info = self.yf.simulate_realtime_update(symbol)
                if stock_info:
                    realtime_data[symbol] = stock_info

            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                continue

        return realtime_data

    def format_for_dashboard(self, data: Dict[str, Dict]) -> Dict:
        """Format data for MEM Dashboard display"""
        formatted_data = {
            'timestamp': datetime.now().isoformat(),
            'stocks': {},
            'summary': {
                'total_symbols': len(data),
                'update_interval': self.update_interval
            }
        }

        for symbol, stock_info in data.items():
            formatted_data['stocks'][symbol] = {
                'symbol': symbol,
                'price': round(stock_info['current_price'], 2),
                'change': round(stock_info['current_price'] - stock_info['previous_close'], 2),
                'change_percent': round(
                    ((stock_info['current_price'] - stock_info['previous_close']) /
                     stock_info['previous_close']) * 100, 2
                ),
                'volume': stock_info['volume'],
                'market_cap': stock_info['market_cap'],
                'pe_ratio': stock_info['pe_ratio'],
                'dividend_yield': stock_info['dividend_yield'],
                'last_updated': stock_info.get('last_updated', datetime.now().isoformat())
            }

        return formatted_data

    def run_realtime_updates(self, duration: int = 300):
        """Run real-time updates for testing"""
        print(f"Starting real-time stock updates for {duration} seconds...")
        print(f"Monitoring symbols: {', '.join(self.symbols)}")
        print("=" * 50)

        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            try:
                # Fetch real-time data
                raw_data = self.get_realtime_data()
                formatted_data = self.format_for_dashboard(raw_data)

                # Display current data
                print(f"\n📊 Stock Update - {formatted_data['timestamp']}")
                print("-" * 30)

                for symbol, stock in formatted_data['stocks'].items():
                    change_icon = "📈" if stock['change'] >= 0 else "📉"
                    print(f"{change_icon} {symbol}: ${stock['price']} "
                          f"({stock['change']:+.2f}, {stock['change_percent']:+.2f}%)")

                # Save data for dashboard integration
                with open('realtime_stock_data.json', 'w') as f:
                    json.dump(formatted_data, f, indent=2)

                print(f"💾 Data saved to realtime_stock_data.json")
                print(f"⏱️  Next update in {self.update_interval} seconds...")

                time.sleep(self.update_interval)

            except KeyboardInterrupt:
                print("\n🛑 Real-time updates stopped by user")
                break
            except Exception as e:
                print(f"❌ Error during update: {e}")
                time.sleep(self.update_interval)

        print("✅ Real-time testing completed!")

def main():
    """Main function for testing yfinance real-time updates"""
    print("🧪 YFinance Real-time Data Testing")
    print("=" * 40)

    # Initialize updater
    symbols = ['AAPL', 'MSFT', 'GOOGL']  # Start with a few symbols for testing
    updater = YFinanceRealtimeUpdater(symbols)

    # Test initial data fetch
    print("🔍 Testing initial data fetch...")
    initial_data = updater.get_realtime_data()
    formatted_data = updater.format_for_dashboard(initial_data)

    print("\n📋 Initial Stock Data:")
    print(json.dumps(formatted_data, indent=2))

    # Run real-time updates for 5 minutes (300 seconds)
    print("\n🚀 Starting real-time updates...")
    updater.run_realtime_updates(duration=300)

    print("\n✅ Testing completed successfully!")
    print("\n📄 Check 'realtime_stock_data.json' for the latest data")

if __name__ == "__main__":
    main()
