import yfinance as yf

from observability import get_logger

logger = get_logger(__name__)


class YahooFinanceService:
    """Service for fetching stock data from Yahoo Finance"""

    def get_stock_data(self, symbol: str) -> dict:
        """
        Get previous close price and market cap for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT').

        Returns:
            Dictionary with 'price', 'market_cap', 'market_cap_text', and 'currency'.
        """
        try:
            logger.info("Fetching stock data from Yahoo Finance", extra={"symbol": symbol})

            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")

            price = None
            if not hist.empty:
                price = hist["Close"].iloc[-1]

            market_cap = info.get("marketCap")
            currency = info.get("currency") or info.get("financialCurrency", "")

            # Format market cap for display
            market_cap_text = "N/A"
            if market_cap:
                if market_cap >= 1e12:
                    market_cap_text = f"{market_cap / 1e12:.2f}T"
                elif market_cap >= 1e9:
                    market_cap_text = f"{market_cap / 1e9:.2f}B"
                elif market_cap >= 1e6:
                    market_cap_text = f"{market_cap / 1e6:.2f}M"
                else:
                    market_cap_text = f"{market_cap:,.0f}"

            result = {
                "price": price,
                "market_cap": market_cap,
                "market_cap_text": market_cap_text,
                "currency": currency,
            }

            logger.info(
                "Yahoo Finance data retrieved successfully",
                extra={"symbol": symbol, "price": price, "market_cap_text": market_cap_text},
            )

            return result

        except Exception as e:
            logger.exception(
                "Failed to fetch Yahoo Finance data", extra={"symbol": symbol, "error": str(e)}
            )
            return {"price": None, "market_cap": None, "market_cap_text": "N/A", "currency": ""}
