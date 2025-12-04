import pytest
from rest_framework import status
from rest_framework.test import APIClient
from csi300.models import CSI300Company

@pytest.mark.django_db
class TestCSI300API:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def sample_company(self):
        return CSI300Company.objects.create(
            name="Test Company",
            ticker="000001.SZ",
            im_sector="Financials",
            industry="Banks",
            market_cap_local=100000000.0,
            # Add other required fields if any. 
            # Assuming these are enough based on model inspection or handling defaults
            region="Mainland China"
        )

    def test_health_check(self, api_client):
        # Assuming the URL is configured at /api/csi300/health/
        url = '/api/csi300/health/'
        response = api_client.get(url)
        # Allow 200 or 500 depending on DB state, but since we are in test DB, it should be 200
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'

    def test_company_list(self, api_client, sample_company):
        url = '/api/csi300/api/companies/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Verify we have results
        # Pagination might be in effect
        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
            
        assert len(results) >= 1
        found = any(c['ticker'] == sample_company.ticker for c in results)
        assert found

    def test_search(self, api_client, sample_company):
        url = '/api/csi300/api/companies/search/'
        response = api_client.get(url, {'q': 'Test'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['ticker'] == sample_company.ticker

