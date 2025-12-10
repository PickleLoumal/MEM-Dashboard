import pytest
from rest_framework.test import APIClient
from rest_framework import status
from drf_spectacular.generators import SchemaGenerator
from csi300.models import CSI300Company


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_companies(db):
    """Create sample companies for testing peers comparison"""
    # Target company
    target = CSI300Company.objects.create(
        id=1,
        name="Target Corp",
        ticker="600001",
        im_sector="Banking",
        market_cap_local=100000000000,  # 100B
        pe_ratio_trailing=10.5,
        roe_trailing=15.2,
        operating_margin_trailing=40.5,
    )

    # Peer 1 (Larger cap)
    CSI300Company.objects.create(
        id=2,
        name="Big Bank",
        ticker="600002",
        im_sector="Banking",
        market_cap_local=200000000000,  # 200B
        pe_ratio_trailing=12.0,
        roe_trailing=16.0,
    )

    # Peer 2 (Smaller cap)
    CSI300Company.objects.create(
        id=3,
        name="Small Bank",
        ticker="600003",
        im_sector="Banking",
        market_cap_local=50000000000,  # 50B
        pe_ratio_trailing=8.0,
        roe_trailing=12.0,
    )

    # Peer 3 (Different sector) - should not be included
    CSI300Company.objects.create(
        id=4,
        name="Tech Corp",
        ticker="600004",
        im_sector="Technology",
        market_cap_local=300000000000,
    )

    return target


@pytest.mark.django_db
class TestCSI300PeersMigration:
    def test_industry_peers_comparison_endpoint(self, api_client, sample_companies):
        """Test that the endpoint returns the correct structure and data"""
        target_id = sample_companies.id
        url = f"/api/csi300/api/companies/{target_id}/industry_peers_comparison/"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 1. Verify Response Structure (Migration Check)
        assert "target_company" in data
        assert "industry" in data
        assert "comparison_data" in data
        assert "total_top_companies_shown" in data
        assert "total_companies_in_industry" in data

        # 2. Verify Data Content
        assert data["industry"] == "Banking"
        assert data["total_companies_in_industry"] == 3  # Target + 2 peers (excluding Tech Corp)

        # Verify comparison_data includes Target and Big Bank (Top 2 by market cap)
        # Big Bank (200B) -> Rank 1
        # Target (100B) -> Rank 2
        # Small Bank (50B) -> Rank 3
        # API returns Top 3 + Target (if not in top 3), here all 3 are returned

        comparison_list = data["comparison_data"]
        assert len(comparison_list) >= 2

        # Find target in list
        target_item = next((item for item in comparison_list if item["id"] == target_id), None)
        assert target_item is not None
        assert target_item["is_current_company"] is True
        assert target_item["market_cap_display"] == "100.00B"
        assert target_item["pe_ratio_display"] == "10.50"

        # Find Big Bank
        big_bank = next((item for item in comparison_list if item["ticker"] == "600002"), None)
        assert big_bank is not None
        assert big_bank["rank"] == 1
        assert big_bank["market_cap_display"] == "200.00B"

    def test_schema_generation_warnings(self):
        """
        Test that schema generation runs without warnings for the peers endpoint.
        This verifies that we fixed the 'unable to resolve type hint' warnings.
        """
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)

        # Navigate to the path in the schema
        paths = schema.get("paths", {})
        peers_path = paths.get("/api/csi300/api/companies/{id}/industry_peers_comparison/")

        assert peers_path is not None, "Endpoint path missing from schema"
        assert "get" in peers_path

        operation = peers_path["get"]
        responses = operation.get("responses", {})
        assert "200" in responses

        # Verify response schema reference
        schema_ref = responses["200"]["content"]["application/json"]["schema"]["$ref"]
        assert "CSI300PeerComparisonResponse" in schema_ref

        # Verify Component Schema
        components = schema.get("components", {}).get("schemas", {})
        item_schema = components.get("CSI300PeerComparisonItem")

        assert item_schema is not None
        properties = item_schema.get("properties", {})

        # Check if the display fields are correctly typed as string
        assert properties["market_cap_display"]["type"] == "string"
        assert properties["pe_ratio_display"]["type"] == "string"
        assert properties["roe_display"]["type"] == "string"
