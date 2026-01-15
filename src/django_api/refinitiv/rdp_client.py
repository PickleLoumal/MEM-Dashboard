"""
Refinitiv Data Platform (RDP) API Client
Cloud-based REST API - No local Workspace required
"""

import logging
import os
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RDPClient:
    """Refinitiv Data Platform API Client"""

    # API Endpoints
    AUTH_URL = "https://api.refinitiv.com/auth/oauth2/v1/token"
    BASE_URL = "https://api.refinitiv.com"

    # Token cache key
    TOKEN_CACHE_KEY = "rdp_access_token"
    TOKEN_EXPIRY_CACHE_KEY = "rdp_token_expiry"

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        """
        Initialize RDP Client

        Args:
            client_id: RDP App Key (UUID format)
            client_secret: RDP App Secret
            username: RDP Username (for password grant)
            password: RDP Password (for password grant)
        """
        self.client_id = (
            client_id
            or getattr(settings, "REFINITIV_CLIENT_ID", None)
            or os.getenv("REFINITIV_CLIENT_ID")
        )
        self.client_secret = (
            client_secret
            or getattr(settings, "REFINITIV_CLIENT_SECRET", None)
            or os.getenv("REFINITIV_CLIENT_SECRET")
        )
        self.username = (
            username
            or getattr(settings, "REFINITIV_USERNAME", None)
            or os.getenv("REFINITIV_USERNAME")
        )
        self.password = (
            password
            or getattr(settings, "REFINITIV_PASSWORD", None)
            or os.getenv("REFINITIV_PASSWORD")
        )

        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "MEM-Dashboard/1.0", "Accept": "application/json"}
        )

        self._access_token = None
        self._refresh_token = None
        self._token_expiry = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.session.close()

    def clear_cache(self):
        """Clear cached tokens to force re-authentication"""
        cache.delete(self.TOKEN_CACHE_KEY)
        cache.delete(self.TOKEN_EXPIRY_CACHE_KEY)
        self._access_token = None
        self._refresh_token = None
        self._token_expiry = None
        logger.info("Cleared RDP token cache")

    def authenticate(self, grant_type: str = "password", force_refresh: bool = False) -> bool:
        """
        Authenticate with RDP and obtain access token

        Args:
            grant_type: "password" or "client_credentials"
            force_refresh: If True, ignore cached token and re-authenticate

        Returns:
            bool: True if authentication successful
        """
        # Clear cache if force refresh requested
        if force_refresh:
            self.clear_cache()

        # Check cached token first
        cached_token = cache.get(self.TOKEN_CACHE_KEY)
        cached_expiry = cache.get(self.TOKEN_EXPIRY_CACHE_KEY)

        if cached_token and cached_expiry and datetime.now(tz=UTC) < cached_expiry:
            self._access_token = cached_token
            self._token_expiry = cached_expiry
            logger.info("Using cached RDP access token")
            return True

        # Prepare authentication request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        if grant_type == "password":
            if not all([self.username, self.password, self.client_id]):
                logger.error("Missing credentials for password grant")
                return False

            data = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.client_id,
                "scope": "trapi",  # Request all available permissions
                "takeExclusiveSignOnControl": "true",  # Force exclusive session
            }

            if self.client_secret:
                data["client_secret"] = self.client_secret

        elif grant_type == "client_credentials":
            if not all([self.client_id, self.client_secret]):
                logger.error("Missing client_id or client_secret for client_credentials grant")
                return False

            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "trapi",  # Request all available permissions
            }
        else:
            logger.error(f"Unsupported grant type: {grant_type}")
            return False

        try:
            logger.info(f"Authenticating with RDP using {grant_type} grant...")
            response = self.session.post(self.AUTH_URL, headers=headers, data=data, timeout=10)

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                self._refresh_token = token_data.get("refresh_token")
                expires_in = int(token_data.get("expires_in", 300))

                # Cache token with 90% of expiry time for safety margin
                cache_timeout = int(expires_in * 0.9)
                self._token_expiry = datetime.now(tz=UTC) + timedelta(seconds=cache_timeout)
                cache.set(self.TOKEN_CACHE_KEY, self._access_token, cache_timeout)
                cache.set(self.TOKEN_EXPIRY_CACHE_KEY, self._token_expiry, cache_timeout)

                logger.info("✅ RDP authentication successful")
                return True
            logger.error(f"❌ RDP authentication failed: {response.status_code} - {response.text}")
            return False

        except Exception:
            logger.exception("❌ RDP authentication error")
            return False

    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self._refresh_token:
            logger.warning("No refresh token available, re-authenticating...")
            return self.authenticate()

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self.client_id,
        }

        if self.client_secret:
            data["client_secret"] = self.client_secret

        try:
            response = self.session.post(self.AUTH_URL, headers=headers, data=data, timeout=10)

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                self._refresh_token = token_data.get("refresh_token")
                expires_in = int(token_data.get("expires_in", 300))

                cache_timeout = int(expires_in * 0.9)
                self._token_expiry = datetime.now(tz=UTC) + timedelta(seconds=cache_timeout)
                cache.set(self.TOKEN_CACHE_KEY, self._access_token, cache_timeout)
                cache.set(self.TOKEN_EXPIRY_CACHE_KEY, self._token_expiry, cache_timeout)

                logger.info("✅ RDP token refreshed")
                return True
            logger.error(f"❌ Token refresh failed: {response.status_code}")
            return self.authenticate()

        except Exception:
            logger.exception("❌ Token refresh error")
            return self.authenticate()

    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token"""
        if not self._access_token:
            return self.authenticate()

        if self._token_expiry and datetime.now(tz=UTC) >= self._token_expiry:
            return self.refresh_access_token()

        return True

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict | None:
        """
        Make authenticated request to RDP API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/data/pricing/snapshots/v1/")
            params: Query parameters
            json_data: JSON body data
            max_retries: Maximum retry attempts

        Returns:
            Response JSON or None
        """
        if not self._ensure_authenticated():
            logger.error("Failed to authenticate with RDP")
            return None

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        for attempt in range(max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=30,
                )

                if response.status_code == 200:
                    return response.json()
                if response.status_code == 401:
                    # Token expired, refresh and retry
                    logger.warning("Token expired, refreshing...")
                    if self.refresh_access_token():
                        headers["Authorization"] = f"Bearer {self._access_token}"
                        continue
                    return None
                if response.status_code == 429:
                    # Rate limit
                    wait_time = 2**attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None

            except Exception:
                logger.exception("Request error (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    return None
                time.sleep(1)

        return None

    # ========== Data API Methods ==========

    def get_pricing_snapshots(
        self, rics: list[str], fields: list[str] | None = None
    ) -> dict | None:
        """
        Get real-time pricing data using Data Grid API

        Args:
            rics: List of RICs (e.g., ["AAPL.O", "MSFT.O"])
            fields: Optional list of fields to retrieve (TR.* format)

        Returns:
            Pricing data or None
        """
        endpoint = "/data/datagrid/beta1/"

        # Default pricing fields if not specified
        if not fields:
            fields = ["TR.PriceClose", "TR.Volume", "TR.PriceHigh", "TR.PriceLow", "TR.PriceOpen"]

        payload = {"universe": rics, "fields": fields}

        return self._make_request("POST", endpoint, json_data=payload)

    def get_historical_pricing(
        self,
        ric: str,
        start_date: str | None = None,
        end_date: str | None = None,
        interval: str = "P1D",
    ) -> dict | None:
        """
        Get historical pricing data

        Args:
            ric: RIC code (e.g., "AAPL.O")
            start_date: Start date (ISO format: "2024-01-01")
            end_date: End date (ISO format: "2024-12-31")
            interval: Time interval (P1D=daily, PT1H=hourly, etc.)

        Returns:
            Historical data or None
        """
        endpoint = f"/data/historical-pricing/v1/views/interday-summaries/{ric}"

        params = {"interval": interval}

        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date

        return self._make_request("GET", endpoint, params=params)

    def search_symbology(self, query: str, limit: int = 10) -> dict | None:
        """
        Search for instruments by name or symbol

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Search results or None
        """
        endpoint = "/discovery/search/v1/"

        payload = {
            "Query": query,
            "View": "SearchAll",
            "Select": "RIC,DocumentTitle,ExchangeName,Currency",
            "Top": limit,
        }

        return self._make_request("POST", endpoint, json_data=payload)

    def get_company_fundamentals(self, ric: str) -> dict | None:
        """
        Get company fundamental data

        Args:
            ric: RIC code

        Returns:
            Fundamental data or None
        """
        endpoint = "/data/fundamentals/v1/views/estimates"

        params = {"universe": ric}

        return self._make_request("GET", endpoint, params=params)

    # ========== News API Methods ==========

    def get_news_headlines(
        self,
        query: str,
        limit: int = 10,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict | None:
        """
        Get news headlines

        Args:
            query: Search query (e.g., "Apple", "RIC:AAPL.O", "China A-shares")
            limit: Maximum number of results (default: 10)
            date_from: Start date (ISO format: "2024-01-01")
            date_to: End date (ISO format: "2024-12-31")

        Returns:
            News headlines or None
        """
        endpoint = "/data/news/v1/headlines"

        params = {"query": query, "limit": limit}

        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to

        return self._make_request("GET", endpoint, params=params)

    def get_news_story(self, news_id: str) -> dict | None:
        """
        Get full news story by ID

        Args:
            news_id: News story ID

        Returns:
            Full news story or None
        """
        endpoint = f"/data/news/v1/stories/{news_id}"
        return self._make_request("GET", endpoint)

    def get_news_by_ric(
        self,
        ric: str,
        limit: int = 10,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict | None:
        """
        Get news for a specific instrument

        Args:
            ric: RIC code (e.g., "AAPL.O")
            limit: Maximum number of results
            date_from: Start date (ISO format)
            date_to: End date (ISO format)

        Returns:
            News headlines or None
        """
        return self.get_news_headlines(
            query=f"RIC:{ric}", limit=limit, date_from=date_from, date_to=date_to
        )

    def get_news_analytics(self, ric: str, limit: int = 10) -> dict | None:
        """
        Get news analytics (sentiment analysis)

        Args:
            ric: RIC code
            limit: Maximum number of results

        Returns:
            News analytics or None
        """
        endpoint = "/data/news/v1/analytics"

        params = {"universe": ric, "limit": limit}

        return self._make_request("GET", endpoint, params=params)

    # ========== Financial Data API Methods ==========

    def get_financial_data(self, ric: str, fields: list[str] | None = None) -> dict | None:
        """
        Get comprehensive financial data using Data Grid API.

        Args:
            ric: RIC code (e.g., "0425.SZ" for XCMG)
            fields: Optional list of TR.* fields. If None, uses default set.

        Returns:
            Financial data dict or None
        """
        endpoint = "/data/datagrid/beta1/"

        # Default comprehensive field set for investment summary
        if not fields:
            fields = [
                # Pricing
                "TR.PriceClose",
                "TR.PriceClose.Date",
                "TR.52WeekHigh",
                "TR.52WeekLow",
                "TR.CompanyMarketCap",
                # Revenue & Profitability
                "TR.Revenue",
                "TR.RevenueGrowthRate",
                "TR.OperatingIncome",
                "TR.NetIncome",
                "TR.NetIncomeGrowthRate",
                "TR.OperatingMargin",
                "TR.GrossMargin",
                "TR.NetProfitMargin",
                # Per Share
                "TR.EPS",
                "TR.EPSGrowthRate",
                "TR.DividendYield",
                "TR.DividendPerShare",
                # Valuation
                "TR.PEEXCLXOR",  # P/E Ratio
                "TR.PEGRatio",
                "TR.PriceToBVPerShare",  # P/B Ratio
                "TR.EVToEBITDA",
                # Balance Sheet
                "TR.TotalDebt",
                "TR.TotalEquity",
                "TR.DebtToEquity",
                "TR.CurrentRatio",
                "TR.QuickRatio",
                # Profitability Ratios
                "TR.ROE",
                "TR.ROA",
                "TR.ROIC",
                # Cash Flow
                "TR.OperatingCashFlow",
                "TR.FreeCashFlow",
                "TR.CapEx",
            ]

        payload = {"universe": [ric], "fields": fields}

        return self._make_request("POST", endpoint, json_data=payload)

    def get_analyst_estimates(self, ric: str) -> dict | None:
        """
        Get analyst estimates and recommendations.

        Args:
            ric: RIC code

        Returns:
            Analyst data dict or None
        """
        endpoint = "/data/datagrid/beta1/"

        fields = [
            # Consensus Recommendations
            "TR.RecommendationMean",
            "TR.NumOfStrongBuyRatings",
            "TR.NumOfBuyRatings",
            "TR.NumOfHoldRatings",
            "TR.NumOfSellRatings",
            "TR.NumOfStrongSellRatings",
            "TR.NumOfAnalysts",
            # Target Price
            "TR.TargetPriceMean",
            "TR.TargetPriceHigh",
            "TR.TargetPriceLow",
            "TR.TargetPriceMedian",
            "TR.TargetPriceUpside",
            # Estimates - Current Year
            "TR.RevenueMeanEstimate",
            "TR.EPSMeanEstimate",
            "TR.NetIncomeMeanEstimate",
            # Estimates - Next Year
            "TR.RevenueMeanEstimate(Period=FY1)",
            "TR.EPSMeanEstimate(Period=FY1)",
            # Growth Estimates
            "TR.RevenueGrowthRateMeanEstimate",
            "TR.EPSGrowthRateMeanEstimate",
        ]

        payload = {"universe": [ric], "fields": fields}

        return self._make_request("POST", endpoint, json_data=payload)

    def get_segment_data(self, ric: str) -> dict | None:
        """
        Get business segment/division data.

        Args:
            ric: RIC code

        Returns:
            Segment data dict or None
        """
        endpoint = "/data/datagrid/beta1/"

        fields = [
            # Segment Revenue
            "TR.BGS.BusSegmentName",
            "TR.BGS.BusSegmentRevenue",
            "TR.BGS.BusSegmentRevenuePct",
            "TR.BGS.BusSegmentOperatingIncome",
            "TR.BGS.BusSegmentOperatingMargin",
            # Geographic Segments
            "TR.BGS.GeoSegmentName",
            "TR.BGS.GeoSegmentRevenue",
            "TR.BGS.GeoSegmentRevenuePct",
        ]

        payload = {"universe": [ric], "fields": fields}

        return self._make_request("POST", endpoint, json_data=payload)

    def get_investment_summary_data(self, ric: str) -> dict[str, Any]:
        """
        Get all data needed for Investment Summary generation.

        This is the main method for fetching comprehensive financial data
        to inject into the AI prompt as context.

        Args:
            ric: RIC code (e.g., "0425.SZ")

        Returns:
            Dict with keys: 'pricing', 'financials', 'analysts', 'segments', 'errors'
        """
        result: dict[str, Any] = {
            "ric": ric,
            "pricing": None,
            "financials": None,
            "analysts": None,
            "segments": None,
            "errors": [],
        }

        # 1. Get pricing data
        try:
            pricing_fields = [
                "TR.PriceClose",
                "TR.PriceClose.Date",
                "TR.52WeekHigh",
                "TR.52WeekLow",
                "TR.CompanyMarketCap",
                "TR.Volume",
            ]
            result["pricing"] = self.get_financial_data(ric, pricing_fields)
        except Exception as e:
            result["errors"].append(f"Pricing error: {e!s}")
            logger.exception("Failed to get pricing data")

        # 2. Get financial fundamentals
        try:
            result["financials"] = self.get_financial_data(ric)
        except Exception as e:
            result["errors"].append(f"Financials error: {e!s}")
            logger.exception("Failed to get financial data")

        # 3. Get analyst estimates
        try:
            result["analysts"] = self.get_analyst_estimates(ric)
        except Exception as e:
            result["errors"].append(f"Analysts error: {e!s}")
            logger.exception("Failed to get analyst data")

        # 4. Get segment data
        try:
            result["segments"] = self.get_segment_data(ric)
        except Exception as e:
            result["errors"].append(f"Segments error: {e!s}")
            logger.exception("Failed to get segment data")

        return result

    def test_connection(self) -> dict[str, Any]:
        """
        Test RDP connection and return status.

        Returns:
            Dict with connection status and details
        """
        result = {
            "authenticated": False,
            "credentials_configured": False,
            "error": None,
        }

        # Check credentials
        result["credentials_configured"] = all(
            [
                self.client_id,
                self.username,
                self.password,
            ]
        )

        if not result["credentials_configured"]:
            result["error"] = "Missing credentials. Check REFINITIV_* env vars."
            return result

        # Try authentication
        try:
            result["authenticated"] = self.authenticate()
            if not result["authenticated"]:
                result["error"] = "Authentication failed. Check credentials."
        except Exception as e:
            result["error"] = f"Authentication error: {e!s}"

        return result
