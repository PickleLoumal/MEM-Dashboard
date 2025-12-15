"""
Refinitiv Analysts' Target Prices API Permission Test

This script tests cloud API permissions for analysts' target prices endpoints.

Based on apiplayground.json, the relevant endpoints are:
- I/B/E/S Estimates API v2 (basepath: /data/estimates/v2):
  - /summaries/non-periodic-measures - Target Price and Long Term Growth
  - /summaries/non-periodic-measures-historical-snapshots - Historical data
  - /summaries/recommendations - Analyst recommendations
  - /summaries/recommendations-historical-snapshots - Historical recommendations

- DataGrid API (basepath: /data/datagrid/beta1/):
  - TR.TargetPriceMean, TR.TargetPriceHigh, TR.TargetPriceLow, etc.

Usage:
    # Run via pytest
    pytest tests/test_refinitiv_target_prices_api.py -v

    # Run standalone
    python tests/test_refinitiv_target_prices_api.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import pytest
import requests

# Add project root to path for standalone execution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "django_api"))

# Load environment variables from .env.local and .env (same as Django settings.py)
try:
    from dotenv import load_dotenv

    _env_local_path = PROJECT_ROOT / ".env.local"
    _env_path = PROJECT_ROOT / ".env"

    # .env.local takes priority (override=True), matching Django settings behavior
    if _env_local_path.exists() and os.getenv("ENVIRONMENT") != "production":
        load_dotenv(dotenv_path=_env_local_path, override=True)
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path)  # Fallback to .env
except ImportError:
    pass  # dotenv not available, rely on shell environment variables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants for log formatting
SEPARATOR_60 = "=" * 60
SEPARATOR_70 = "=" * 70
DASH_SEPARATOR_70 = "-" * 70


class PermissionStatus(Enum):
    """API permission status enum."""

    ENTITLED = "entitled"
    NOT_ENTITLED = "not_entitled"
    AUTH_ERROR = "auth_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


@dataclass
class EndpointTestResult:
    """Result of testing a single API endpoint."""

    endpoint: str
    method: str
    status_code: int | None
    permission_status: PermissionStatus
    response_body: dict[str, Any] | None
    error_message: str | None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "permission_status": self.permission_status.value,
            "error_message": self.error_message,
            "has_data": self.response_body is not None and len(self.response_body) > 0,
        }
        # Include response body for debugging (truncated for large responses)
        if self.response_body:
            body_str = json.dumps(self.response_body)
            if len(body_str) > 2000:
                result["response_preview"] = body_str[:2000] + "..."
            else:
                result["response_body"] = self.response_body
        return result


class RefinitivTargetPriceAPITester:
    """Test Refinitiv API permissions for analysts' target prices endpoints."""

    AUTH_URL = "https://api.refinitiv.com/auth/oauth2/v1/token"
    BASE_URL = "https://api.refinitiv.com"

    # Test RICs - use well-known stocks with good analyst coverage
    TEST_RICS = ["AAPL.O", "MSFT.O", "0700.HK"]  # Apple, Microsoft, Tencent

    # I/B/E/S Estimates API v2 endpoints for Target Prices
    # Note: 'package' must be one of: "base", "standard", "professional"
    ESTIMATES_API_ENDPOINTS = [
        {
            "path": "/data/estimates/v2/summaries/non-periodic-measures",
            "description": "Target Price and Long Term Growth",
            "params": {"universe": "AAPL.O", "package": "standard"},
        },
        {
            "path": "/data/estimates/v2/summaries/non-periodic-measures-historical-snapshots",
            "description": "Historical Target Price snapshots",
            "params": {"universe": "AAPL.O", "package": "standard"},
        },
        {
            "path": "/data/estimates/v2/summaries/recommendations",
            "description": "Analyst Recommendations",
            "params": {"universe": "AAPL.O", "package": "standard"},
        },
        {
            "path": "/data/estimates/v2/summaries/recommendations-historical-snapshots",
            "description": "Historical Recommendations",
            "params": {"universe": "AAPL.O", "package": "standard"},
        },
        {
            "path": "/data/estimates/v2/coverages",
            "description": "Estimates Coverage List",
            "params": {},
        },
    ]

    # DataGrid API fields for Target Prices (I/B/E/S data)
    # These require I/B/E/S subscription
    DATAGRID_TARGET_PRICE_FIELDS = [
        "TR.TargetPriceMean",
        "TR.TargetPriceHigh",
        "TR.TargetPriceLow",
        "TR.TargetPriceMedian",
        "TR.TargetPriceUpside",
        "TR.NumOfAnalysts",
        "TR.RecommendationMean",
        "TR.NumOfStrongBuyRatings",
        "TR.NumOfBuyRatings",
        "TR.NumOfHoldRatings",
        "TR.NumOfSellRatings",
        "TR.NumOfStrongSellRatings",
    ]

    # Basic fields that should always work (for verification)
    DATAGRID_BASIC_FIELDS = [
        "TR.PriceClose",
        "TR.CompanyMarketCap",
        "TR.CompanyName",
    ]

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        """Initialize the tester with credentials."""
        self.client_id = client_id or os.getenv("REFINITIV_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REFINITIV_CLIENT_SECRET")
        self.username = username or os.getenv("REFINITIV_USERNAME")
        self.password = password or os.getenv("REFINITIV_PASSWORD")

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ALFIE-TargetPriceAPITest/1.0",
            "Accept": "application/json",
        })

        self._access_token: str | None = None
        self.results: list[EndpointTestResult] = []

    def _check_credentials(self) -> bool:
        """Check if all required credentials are configured."""
        missing = []
        if not self.client_id:
            missing.append("REFINITIV_CLIENT_ID")
        if not self.username:
            missing.append("REFINITIV_USERNAME")
        if not self.password:
            missing.append("REFINITIV_PASSWORD")

        if missing:
            logger.error("Missing credentials: %s", ", ".join(missing))
            return False
        return True

    def authenticate(self) -> bool:
        """
        Authenticate with Refinitiv and obtain access token.

        Returns:
            bool: True if authentication successful
        """
        if not self._check_credentials():
            return False

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Request all required scopes for estimates API
        # trapi.data.est.sum is required for I/B/E/S Estimates API
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id,
            "scope": "trapi trapi.data.est.sum",
            "takeExclusiveSignOnControl": "true",
        }

        if self.client_secret:
            data["client_secret"] = self.client_secret

        try:
            logger.info("Authenticating with Refinitiv Data Platform...")
            response = self.session.post(self.AUTH_URL, headers=headers, data=data, timeout=15)

            if response.status_code == 200:
                token_data = response.json()
                self._access_token = token_data.get("access_token")
                logger.info("✅ Authentication successful")
                return True

            logger.error("❌ Authentication failed: %d", response.status_code)
            logger.error("   Response: %s", response.text[:500])
            return False

        except requests.Timeout:
            logger.warning("❌ Authentication timeout")
            return False
        except requests.RequestException:
            logger.exception("❌ Authentication error")
            return False

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> EndpointTestResult:
        """
        Make an authenticated API request and return detailed result.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body for POST requests

        Returns:
            EndpointTestResult with detailed status
        """
        if not self._access_token:
            return EndpointTestResult(
                endpoint=endpoint,
                method=method,
                status_code=None,
                permission_status=PermissionStatus.AUTH_ERROR,
                response_body=None,
                error_message="Not authenticated - no access token",
            )

        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=30,
            )

            # Parse response
            try:
                response_body = response.json()
            except json.JSONDecodeError:
                response_body = {"raw_text": response.text[:1000]}

            # Determine permission status
            if response.status_code == 200:
                permission_status = PermissionStatus.ENTITLED
                error_message = None
            elif response.status_code == 401:
                permission_status = PermissionStatus.AUTH_ERROR
                error_message = "Unauthorized - token may have expired"
            elif response.status_code == 403:
                permission_status = PermissionStatus.NOT_ENTITLED
                error_message = response_body.get("error", {}).get(
                    "message", "Access denied - not entitled to this endpoint"
                )
            elif response.status_code == 400:
                # Bad request - capture detailed error for debugging
                permission_status = PermissionStatus.UNKNOWN
                if isinstance(response_body.get("error"), dict):
                    error_message = response_body["error"].get("message", str(response_body))
                elif "error" in response_body:
                    error_message = str(response_body["error"])
                else:
                    error_message = f"Bad Request: {json.dumps(response_body)[:500]}"
            elif response.status_code == 404:
                permission_status = PermissionStatus.UNKNOWN
                error_message = "Endpoint not found"
            else:
                permission_status = PermissionStatus.UNKNOWN
                error_message = f"Unexpected status: {response.status_code}"

            return EndpointTestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                permission_status=permission_status,
                response_body=response_body,  # Always include response for debugging
                error_message=error_message,
            )

        except requests.Timeout:
            return EndpointTestResult(
                endpoint=endpoint,
                method=method,
                status_code=None,
                permission_status=PermissionStatus.NETWORK_ERROR,
                response_body=None,
                error_message="Request timeout",
            )
        except requests.RequestException as e:
            return EndpointTestResult(
                endpoint=endpoint,
                method=method,
                status_code=None,
                permission_status=PermissionStatus.NETWORK_ERROR,
                response_body=None,
                error_message=str(e),
            )

    def test_estimates_api_endpoints(self) -> list[EndpointTestResult]:
        """
        Test all I/B/E/S Estimates API v2 endpoints.

        Returns:
            List of test results
        """
        logger.info("\n%s", SEPARATOR_60)
        logger.info("Testing I/B/E/S Estimates API v2 Endpoints")
        logger.info("%s", SEPARATOR_60)

        results = []
        for endpoint_config in self.ESTIMATES_API_ENDPOINTS:
            path = endpoint_config["path"]
            description = endpoint_config["description"]
            params = endpoint_config.get("params", {})

            logger.info("\n📡 Testing: %s", description)
            logger.info("   Endpoint: GET %s", path)

            result = self._make_request("GET", path, params=params)
            results.append(result)

            self._log_result(result)

        return results

    def test_datagrid_basic_fields(self) -> EndpointTestResult:
        """
        Test DataGrid API with basic fields to verify connectivity.

        Returns:
            Test result for DataGrid endpoint
        """
        logger.info("\n%s", SEPARATOR_60)
        logger.info("Testing DataGrid API - Basic Fields (Verification)")
        logger.info("%s", SEPARATOR_60)

        endpoint = "/data/datagrid/beta1/"
        payload = {
            "universe": self.TEST_RICS,
            "fields": self.DATAGRID_BASIC_FIELDS,
        }

        logger.info("\n📡 Testing: DataGrid Basic Request (should work)")
        logger.info("   Endpoint: POST %s", endpoint)
        logger.info("   Universe: %s", self.TEST_RICS)
        logger.info("   Fields: %s", self.DATAGRID_BASIC_FIELDS)

        result = self._make_request("POST", endpoint, json_data=payload)
        result.endpoint = f"{endpoint} (Basic Fields)"
        self._log_result(result)

        return result

    def test_datagrid_target_price_fields(self) -> EndpointTestResult:
        """
        Test DataGrid API for target price fields.

        Returns:
            Test result for DataGrid endpoint
        """
        logger.info("\n%s", SEPARATOR_60)
        logger.info("Testing DataGrid API - Target Price Fields")
        logger.info("%s", SEPARATOR_60)

        endpoint = "/data/datagrid/beta1/"
        payload = {
            "universe": self.TEST_RICS,
            "fields": self.DATAGRID_TARGET_PRICE_FIELDS,
        }

        logger.info("\n📡 Testing: DataGrid Target Price Request")
        logger.info("   Endpoint: POST %s", endpoint)
        logger.info("   Universe: %s", self.TEST_RICS)
        logger.info("   Fields: %d target price related fields", len(self.DATAGRID_TARGET_PRICE_FIELDS))

        result = self._make_request("POST", endpoint, json_data=payload)
        result.endpoint = f"{endpoint} (Target Price Fields)"
        self._log_result(result)

        return result

    def test_individual_target_price_fields(self) -> list[EndpointTestResult]:
        """
        Test each target price field individually to identify specific permission issues.

        Returns:
            List of results for each field
        """
        logger.info("\n%s", SEPARATOR_60)
        logger.info("Testing Individual Target Price Fields")
        logger.info("%s", SEPARATOR_60)

        endpoint = "/data/datagrid/beta1/"
        results = []

        for field in self.DATAGRID_TARGET_PRICE_FIELDS:
            payload = {
                "universe": ["AAPL.O"],
                "fields": [field],
            }

            logger.info("\n📡 Testing field: %s", field)

            result = self._make_request("POST", endpoint, json_data=payload)
            # Modify endpoint name to include field for clarity
            result.endpoint = f"{endpoint} ({field})"
            results.append(result)

            status_icon = "✅" if result.permission_status == PermissionStatus.ENTITLED else "❌"
            logger.info("   %s Status: %s", status_icon, result.permission_status.value)

        return results

    def _log_result(self, result: EndpointTestResult) -> None:
        """Log a test result with appropriate formatting."""
        if result.permission_status == PermissionStatus.ENTITLED:
            logger.info("   ✅ Status: %s - ENTITLED", result.status_code)
            if result.response_body:
                # Log a summary of the response
                data_summary = self._summarize_response(result.response_body)
                logger.info("   📊 Data: %s", data_summary)
        elif result.permission_status == PermissionStatus.NOT_ENTITLED:
            logger.warning("   ❌ Status: %s - NOT ENTITLED", result.status_code)
            logger.warning("   💡 Error: %s", result.error_message)
        else:
            logger.error("   ⚠️ Status: %s - %s", result.status_code, result.permission_status.value)
            logger.error("   💡 Error: %s", result.error_message)

    def _summarize_response(self, body: dict[str, Any]) -> str:
        """Create a summary of the response data."""
        # Check for error in response (even with 200 status)
        if "error" in body and body.get("error"):
            error_info = body["error"]
            if isinstance(error_info, list):
                # DataGrid returns errors as list
                error_msgs = [e.get("message", str(e)) for e in error_info[:3]]
                return f"⚠️ Response contains errors: {'; '.join(error_msgs)}"
            elif isinstance(error_info, dict):
                return f"⚠️ Error: {error_info.get('message', str(error_info))}"
            return f"⚠️ Error: {error_info}"

        if "data" in body:
            data = body["data"]
            if isinstance(data, list):
                return f"{len(data)} records returned"
            return "Data object returned"
        if "headers" in body and "data" in body:
            return f"{len(body.get('data', []))} rows, {len(body.get('headers', []))} columns"
        return f"Keys: {list(body.keys())[:5]}"

    def run_all_tests(self) -> dict[str, Any]:
        """
        Run all API permission tests.

        Returns:
            Summary of all test results
        """
        logger.info("\n%s", SEPARATOR_70)
        logger.info("  REFINITIV TARGET PRICES API PERMISSION TEST")
        logger.info("%s", SEPARATOR_70)

        # Step 1: Authenticate
        if not self.authenticate():
            return {
                "success": False,
                "error": "Authentication failed",
                "results": [],
            }

        all_results = []

        # Step 2: Test Estimates API endpoints
        estimates_results = self.test_estimates_api_endpoints()
        all_results.extend(estimates_results)

        # Step 3: Test DataGrid API - Basic fields first (to verify API works)
        basic_result = self.test_datagrid_basic_fields()
        all_results.append(basic_result)

        # Step 4: Test DataGrid API - Target Price fields
        datagrid_result = self.test_datagrid_target_price_fields()
        all_results.append(datagrid_result)

        # Store results
        self.results = all_results

        # Generate summary
        summary = self._generate_summary(all_results)
        self._print_summary(summary)

        return summary

    def _generate_summary(self, results: list[EndpointTestResult]) -> dict[str, Any]:
        """Generate a summary of all test results."""
        entitled_count = sum(1 for r in results if r.permission_status == PermissionStatus.ENTITLED)
        not_entitled_count = sum(
            1 for r in results if r.permission_status == PermissionStatus.NOT_ENTITLED
        )
        error_count = sum(
            1
            for r in results
            if r.permission_status in [PermissionStatus.AUTH_ERROR, PermissionStatus.NETWORK_ERROR]
        )

        return {
            "success": True,
            "total_endpoints_tested": len(results),
            "entitled": entitled_count,
            "not_entitled": not_entitled_count,
            "errors": error_count,
            "results": [r.to_dict() for r in results],
            "entitled_endpoints": [
                r.endpoint for r in results if r.permission_status == PermissionStatus.ENTITLED
            ],
            "not_entitled_endpoints": [
                r.endpoint for r in results if r.permission_status == PermissionStatus.NOT_ENTITLED
            ],
        }

    def _print_summary(self, summary: dict[str, Any]) -> None:
        """Print a formatted summary of test results."""
        logger.info("\n%s", SEPARATOR_70)
        logger.info("  TEST SUMMARY")
        logger.info("%s", SEPARATOR_70)

        logger.info("\n📊 Total Endpoints Tested: %d", summary["total_endpoints_tested"])
        logger.info("   ✅ Entitled: %d", summary["entitled"])
        logger.info("   ❌ Not Entitled: %d", summary["not_entitled"])
        logger.info("   ⚠️ Errors: %d", summary["errors"])

        if summary["entitled_endpoints"]:
            logger.info("\n✅ ENTITLED ENDPOINTS:")
            for ep in summary["entitled_endpoints"]:
                logger.info("   • %s", ep)

        if summary["not_entitled_endpoints"]:
            logger.info("\n❌ NOT ENTITLED ENDPOINTS (require permission upgrade):")
            for ep in summary["not_entitled_endpoints"]:
                logger.info("   • %s", ep)

        # Provide recommendations
        logger.info("\n%s", DASH_SEPARATOR_70)
        logger.info("💡 RECOMMENDATIONS:")
        if summary["not_entitled"] > 0:
            logger.info(
                "   1. Contact your Refinitiv account representative to enable"
            )
            logger.info("      I/B/E/S Estimates API v2 access for target prices")
            logger.info("   2. Required product: 'I/B/E/S API RDP Wealth' or equivalent")
            logger.info("   3. Endpoints needed:")
            logger.info("      - /data/estimates/v2/summaries/non-periodic-measures")
            logger.info("      - /data/estimates/v2/summaries/recommendations")
        else:
            logger.info("   All required endpoints are accessible! ✅")


# ============================================================================
# Pytest fixtures and test functions
# ============================================================================


def pytest_configure(config):
    """Configure Django settings for pytest."""
    try:
        import django
        from django.conf import settings as django_settings

        if not django_settings.configured:
            django_settings.configure(
                DEBUG=True,
                DATABASES={},
                INSTALLED_APPS=[],
            )
        django.setup()
    except ImportError:
        pass  # Django not required for standalone tests


class TestRefinitivTargetPricesAPI:
    """Pytest test class for Refinitiv Target Prices API."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.tester = RefinitivTargetPriceAPITester()

    def test_credentials_configured(self):
        """Test that Refinitiv credentials are configured."""
        assert self.tester._check_credentials(), (
            "Missing Refinitiv credentials. "
            "Set REFINITIV_CLIENT_ID, REFINITIV_USERNAME, REFINITIV_PASSWORD env vars."
        )

    def test_authentication(self):
        """Test Refinitiv authentication."""
        if not self.tester._check_credentials():
            pytest.skip("Refinitiv credentials not configured")

        assert self.tester.authenticate(), "Failed to authenticate with Refinitiv"

    def test_estimates_api_non_periodic_measures(self):
        """Test /summaries/non-periodic-measures endpoint (Target Price)."""
        if not self.tester._access_token and not self.tester.authenticate():
            pytest.skip("Authentication failed")

        result = self.tester._make_request(
            "GET",
            "/data/estimates/v2/summaries/non-periodic-measures",
            params={"universe": "AAPL.O"},
        )

        # Log the result for debugging
        logger.info("Non-periodic measures result: %s", result.to_dict())

        # Test passes if we get a response (even if not entitled, we want to know)
        assert result.status_code is not None, f"Network error: {result.error_message}"

    def test_estimates_api_recommendations(self):
        """Test /summaries/recommendations endpoint."""
        if not self.tester._access_token and not self.tester.authenticate():
            pytest.skip("Authentication failed")

        result = self.tester._make_request(
            "GET",
            "/data/estimates/v2/summaries/recommendations",
            params={"universe": "AAPL.O"},
        )

        logger.info("Recommendations result: %s", result.to_dict())
        assert result.status_code is not None, f"Network error: {result.error_message}"

    def test_datagrid_target_price_fields(self):
        """Test DataGrid API for target price fields."""
        if not self.tester._access_token and not self.tester.authenticate():
            pytest.skip("Authentication failed")

        result = self.tester._make_request(
            "POST",
            "/data/datagrid/beta1/",
            json_data={
                "universe": ["AAPL.O"],
                "fields": ["TR.TargetPriceMean", "TR.RecommendationMean"],
            },
        )

        logger.info("DataGrid result: %s", result.to_dict())
        assert result.status_code is not None, f"Network error: {result.error_message}"


# ============================================================================
# Standalone execution
# ============================================================================

if __name__ == "__main__":
    # Run as standalone script
    tester = RefinitivTargetPriceAPITester()
    summary = tester.run_all_tests()

    # Export results to JSON file
    output_file = PROJECT_ROOT / "tests" / "refinitiv_target_prices_test_results.json"
    with output_file.open("w") as f:
        json.dump(summary, f, indent=2)
    logger.info("\n📄 Results saved to: %s", output_file)

    # Exit with appropriate code
    sys.exit(0 if summary.get("success") else 1)
