#!/usr/bin/env python3
"""
Refinitiv API Entitlement Test Suite

Tests all entitled APIs from apiplayground.json to verify actual access
and data quality. Useful for preparing discussions with Refinitiv account team.

Author: ALFIE Financial Analyst
Date: 2024-12
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import requests

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "django_api"))

# Load environment variables (same pattern as Django settings)
try:
    from dotenv import load_dotenv

    env_local = PROJECT_ROOT / ".env.local"
    env_file = PROJECT_ROOT / ".env"
    if env_local.exists() and os.getenv("ENVIRONMENT") != "production":
        load_dotenv(dotenv_path=env_local, override=True)
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

SEPARATOR = "=" * 70


class TestStatus(Enum):
    """API test result status."""

    SUCCESS = "success"
    PARTIAL = "partial"  # 200 but with errors/warnings
    AUTH_ERROR = "auth_error"
    NOT_ENTITLED = "not_entitled"
    BAD_REQUEST = "bad_request"
    SERVER_ERROR = "server_error"
    NETWORK_ERROR = "network_error"


@dataclass
class APITestResult:
    """Result of an API test."""

    api_name: str
    endpoint: str
    method: str
    status_code: int | None
    test_status: TestStatus
    response_data: dict[str, Any] | None
    error_message: str | None
    latency_ms: float | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "api_name": self.api_name,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "test_status": self.test_status.value,
            "error_message": self.error_message,
            "latency_ms": self.latency_ms,
            "has_data": self.response_data is not None,
        }
        if self.response_data:
            data_str = json.dumps(self.response_data)
            if len(data_str) > 1500:
                result["response_preview"] = data_str[:1500] + "..."
            else:
                result["response_data"] = self.response_data
        return result


class RefinitivAPITester:
    """Tests entitled Refinitiv APIs."""

    BASE_URL = "https://api.refinitiv.com"
    AUTH_URL = "https://api.refinitiv.com/auth/oauth2/v1/token"

    # Test instruments
    TEST_RICS = ["AAPL.O", "MSFT.O", "0700.HK", "600519.SS"]  # US + China stocks

    def __init__(self) -> None:
        """Initialize with credentials from environment."""
        self.client_id = os.getenv("REFINITIV_CLIENT_ID", "")
        self.username = os.getenv("REFINITIV_USERNAME", "")
        self.password = os.getenv("REFINITIV_PASSWORD", "")
        self.access_token: str | None = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate and get access token."""
        if not all([self.client_id, self.username, self.password]):
            logger.error("❌ Missing credentials")
            return False

        logger.info("\n%s", SEPARATOR)
        logger.info("🔐 Authenticating with Refinitiv...")
        logger.info("%s", SEPARATOR)

        try:
            response = self.session.post(
                self.AUTH_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                    "client_id": self.client_id,
                    "scope": "trapi",
                    "takeExclusiveSignOnControl": "true",
                },
                timeout=30,
            )

            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.error("❌ Auth failed: %s", response.text[:200])
                return False

        except requests.RequestException as e:
            logger.exception("❌ Network error: %s", e)
            return False

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
        api_name: str = "",
    ) -> APITestResult:
        """Make an authenticated API request."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        start_time = datetime.now()
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=json_data, timeout=30)
            else:
                return APITestResult(
                    api_name=api_name,
                    endpoint=endpoint,
                    method=method,
                    status_code=None,
                    test_status=TestStatus.BAD_REQUEST,
                    response_data=None,
                    error_message=f"Unsupported method: {method}",
                    latency_ms=None,
                )

            latency = (datetime.now() - start_time).total_seconds() * 1000
            response_body = response.json() if response.text else {}

            # Determine status
            if response.status_code == 200:
                # Check for embedded errors
                if "error" in response_body and response_body.get("error"):
                    test_status = TestStatus.PARTIAL
                    error_msg = self._extract_error(response_body)
                else:
                    test_status = TestStatus.SUCCESS
                    error_msg = None
            elif response.status_code == 401:
                test_status = TestStatus.AUTH_ERROR
                error_msg = "Authentication required or token expired"
            elif response.status_code == 403:
                test_status = TestStatus.NOT_ENTITLED
                error_msg = self._extract_error(response_body)
            elif response.status_code == 400:
                test_status = TestStatus.BAD_REQUEST
                error_msg = self._extract_error(response_body)
            else:
                test_status = TestStatus.SERVER_ERROR
                error_msg = f"HTTP {response.status_code}"

            return APITestResult(
                api_name=api_name,
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                test_status=test_status,
                response_data=response_body,
                error_message=error_msg,
                latency_ms=latency,
            )

        except requests.RequestException as e:
            return APITestResult(
                api_name=api_name,
                endpoint=endpoint,
                method=method,
                status_code=None,
                test_status=TestStatus.NETWORK_ERROR,
                response_data=None,
                error_message=str(e),
                latency_ms=None,
            )

    def _extract_error(self, body: dict[str, Any]) -> str:
        """Extract error message from response body."""
        if "error" in body:
            err = body["error"]
            if isinstance(err, dict):
                return err.get("message", str(err))[:200]
            if isinstance(err, list) and err:
                return str(err[0].get("message", err[0]))[:200]
            return str(err)[:200]
        return "Unknown error"

    def _log_result(self, result: APITestResult) -> None:
        """Log test result."""
        status_icons = {
            TestStatus.SUCCESS: "✅",
            TestStatus.PARTIAL: "⚠️",
            TestStatus.AUTH_ERROR: "🔐",
            TestStatus.NOT_ENTITLED: "🚫",
            TestStatus.BAD_REQUEST: "❓",
            TestStatus.SERVER_ERROR: "💥",
            TestStatus.NETWORK_ERROR: "🌐",
        }
        icon = status_icons.get(result.test_status, "❓")

        logger.info(
            "   %s %s [%s] - %sms",
            icon,
            result.test_status.value.upper(),
            result.status_code or "N/A",
            f"{result.latency_ms:.0f}" if result.latency_ms else "N/A",
        )
        if result.error_message:
            logger.info("      Error: %s", result.error_message[:100])

    # ========================================================================
    # Test Methods for Entitled APIs
    # ========================================================================

    def test_datagrid_api(self) -> list[APITestResult]:
        """Test DataGrid API with various field categories."""
        results = []
        logger.info("\n%s", SEPARATOR)
        logger.info("📊 Testing: RDP DataGrid API")
        logger.info("%s", SEPARATOR)

        test_cases = [
            {
                "name": "Basic Price Data",
                "fields": ["TR.PriceClose", "TR.Volume", "TR.PriceOpen", "TR.PriceHigh", "TR.PriceLow"],
            },
            {
                "name": "Company Info",
                "fields": ["TR.CompanyName", "TR.CommonName", "TR.HeadquartersCountry", "TR.GICSIndustry"],
            },
            {
                "name": "Market Cap & Valuation",
                "fields": ["TR.CompanyMarketCap", "TR.PE", "TR.PriceToBVPS", "TR.DividendYield"],
            },
            {
                "name": "Financial Ratios",
                "fields": ["TR.ROE", "TR.ROA", "TR.DebtToEquity", "TR.CurrentRatio"],
            },
            {
                "name": "Revenue & Earnings",
                "fields": ["TR.Revenue", "TR.NetIncome", "TR.EPS", "TR.EBITDA"],
            },
            {
                "name": "Target Price (I/B/E/S)",
                "fields": ["TR.TargetPriceMean", "TR.TargetPriceHigh", "TR.TargetPriceLow"],
            },
            {
                "name": "Analyst Recommendations",
                "fields": ["TR.RecommendationMean", "TR.NumOfAnalysts", "TR.NumOfBuyRatings"],
            },
            {
                "name": "ESG Scores",
                "fields": ["TR.TRESGScore", "TR.EnvironmentPillarScore", "TR.SocialPillarScore"],
            },
        ]

        for test in test_cases:
            logger.info("\n   📡 %s", test["name"])
            payload = {
                "universe": self.TEST_RICS[:2],  # Use 2 stocks to save quota
                "fields": test["fields"],
            }
            result = self._make_request(
                "POST",
                "/data/datagrid/beta1/",
                json_data=payload,
                api_name=f"DataGrid - {test['name']}",
            )
            result.endpoint = f"/data/datagrid/beta1/ ({test['name']})"
            self._log_result(result)
            results.append(result)

        return results

    def test_historical_pricing(self) -> list[APITestResult]:
        """Test Historical Pricing API."""
        results = []
        logger.info("\n%s", SEPARATOR)
        logger.info("📈 Testing: Historical Pricing API")
        logger.info("%s", SEPARATOR)

        # Interday historical data
        logger.info("\n   📡 Interday Summaries")
        result = self._make_request(
            "GET",
            "/data/historical-pricing/v1/views/interday-summaries/AAPL.O",
            params={"interval": "P1D", "count": 10},
            api_name="Historical Pricing - Interday",
        )
        self._log_result(result)
        results.append(result)

        # Intraday data
        logger.info("\n   📡 Intraday Summaries")
        result = self._make_request(
            "GET",
            "/data/historical-pricing/v1/views/intraday-summaries/AAPL.O",
            params={"interval": "PT1H", "count": 10},
            api_name="Historical Pricing - Intraday",
        )
        self._log_result(result)
        results.append(result)

        return results

    def test_search_api(self) -> list[APITestResult]:
        """Test Search API."""
        results = []
        logger.info("\n%s", SEPARATOR)
        logger.info("🔍 Testing: Search API")
        logger.info("%s", SEPARATOR)

        # Search for companies
        logger.info("\n   📡 Company Search")
        result = self._make_request(
            "GET",
            "/discovery/search/v1/search",
            params={"q": "Apple", "filter": "AssetType eq 'Common Stock'", "top": 5},
            api_name="Search - Company",
        )
        self._log_result(result)
        results.append(result)

        return results

    def test_symbology_api(self) -> list[APITestResult]:
        """Test Symbology API."""
        results = []
        logger.info("\n%s", SEPARATOR)
        logger.info("🏷️ Testing: Symbology API")
        logger.info("%s", SEPARATOR)

        logger.info("\n   📡 Symbol Lookup")
        result = self._make_request(
            "POST",
            "/discovery/symbology/v1/lookup",
            json_data={
                "from": [{"identifierTypes": ["RIC"], "values": ["AAPL.O", "MSFT.O"]}],
                "to": [{"identifierTypes": ["ISIN", "CUSIP", "SEDOL"]}],
            },
            api_name="Symbology - Lookup",
        )
        self._log_result(result)
        results.append(result)

        return results

    def test_news_api(self) -> list[APITestResult]:
        """Test News API (mobile service - we have access)."""
        results = []
        logger.info("\n%s", SEPARATOR)
        logger.info("📰 Testing: News Service API")
        logger.info("%s", SEPARATOR)

        logger.info("\n   📡 News Headlines")
        result = self._make_request(
            "GET",
            "/user-framework/mobile/news-service/v1/stories",
            params={"limit": 5},
            api_name="News - Headlines",
        )
        self._log_result(result)
        results.append(result)

        return results

    def test_quantitative_analytics(self) -> list[APITestResult]:
        """Test IPA Financial Contracts (Quantitative Analytics)."""
        results = []
        logger.info("\n%s", SEPARATOR)
        logger.info("📐 Testing: Quantitative Analytics API")
        logger.info("%s", SEPARATOR)

        logger.info("\n   📡 Bond Pricing")
        result = self._make_request(
            "POST",
            "/data/quantitative-analytics/v1/financial-contracts",
            json_data={
                "universe": [
                    {
                        "instrumentType": "Bond",
                        "instrumentDefinition": {
                            "instrumentCode": "US912828Z302=",
                        },
                    }
                ],
                "fields": ["MarketValueInDealCcy", "CleanPricePercent"],
            },
            api_name="Quantitative Analytics - Bond",
        )
        self._log_result(result)
        results.append(result)

        return results

    def run_all_tests(self) -> dict[str, Any]:
        """Run all API tests and return summary."""
        if not self.authenticate():
            return {"success": False, "error": "Authentication failed"}

        all_results: list[APITestResult] = []

        # Run all test suites
        all_results.extend(self.test_datagrid_api())
        all_results.extend(self.test_historical_pricing())
        all_results.extend(self.test_search_api())
        all_results.extend(self.test_symbology_api())
        all_results.extend(self.test_news_api())
        all_results.extend(self.test_quantitative_analytics())

        # Summarize
        summary = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "by_status": {},
            "results": [r.to_dict() for r in all_results],
        }

        for status in TestStatus:
            count = sum(1 for r in all_results if r.test_status == status)
            if count > 0:
                summary["by_status"][status.value] = count

        # Print summary
        logger.info("\n%s", SEPARATOR)
        logger.info("📊 TEST SUMMARY")
        logger.info("%s", SEPARATOR)
        for status, count in summary["by_status"].items():
            logger.info("   %s: %d", status.upper(), count)

        # Categorize for meeting prep
        working_apis = [r.api_name for r in all_results if r.test_status == TestStatus.SUCCESS]
        partial_apis = [r.api_name for r in all_results if r.test_status == TestStatus.PARTIAL]
        blocked_apis = [
            r.api_name for r in all_results if r.test_status in [TestStatus.NOT_ENTITLED, TestStatus.AUTH_ERROR]
        ]

        summary["working_apis"] = working_apis
        summary["partial_apis"] = partial_apis
        summary["blocked_apis"] = blocked_apis

        logger.info("\n✅ WORKING APIs:")
        for api in working_apis:
            logger.info("   • %s", api)

        logger.info("\n⚠️ PARTIAL/WARNING APIs:")
        for api in partial_apis:
            logger.info("   • %s", api)

        logger.info("\n🚫 BLOCKED/NOT ENTITLED APIs:")
        for api in blocked_apis:
            logger.info("   • %s", api)

        return summary


def main() -> None:
    """Main entry point."""
    logger.info("\n%s", SEPARATOR)
    logger.info("🔬 REFINITIV API ENTITLEMENT TEST SUITE")
    logger.info("   Testing APIs from apiplayground.json")
    logger.info("%s", SEPARATOR)

    tester = RefinitivAPITester()
    results = tester.run_all_tests()

    # Save results
    output_path = PROJECT_ROOT / "tests" / "refinitiv_entitled_apis_results.json"
    with output_path.open("w") as f:
        json.dump(results, f, indent=2)
    logger.info("\n📁 Results saved to: %s", output_path)


if __name__ == "__main__":
    main()
