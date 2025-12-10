import pytest
from unittest.mock import MagicMock, patch
from django.utils import timezone
from fred_us.auto_fetcher import FredUsAutoFetcher
from fred_us.models import FredUsIndicatorConfig


@pytest.mark.django_db
class TestFredUsAutoFetcher:
    @pytest.fixture
    def fetcher(self):
        return FredUsAutoFetcher(api_key="test_key")

    @pytest.fixture
    def sample_config(self):
        return FredUsIndicatorConfig.objects.create(
            series_id="TEST_SERIES",
            name="Test Series",
            auto_fetch=True,
            is_active=True,
            fetch_frequency="daily",
            additional_config={},
        )

    @patch("fred_us.auto_fetcher.UsFredDataFetcher")
    def test_fetch_single_indicator_success(self, mock_fetcher_cls, fetcher, sample_config):
        # Setup mock
        mock_instance = mock_fetcher_cls.return_value
        mock_instance.get_series_info.return_value = {"title": "Test Title"}
        mock_instance.get_series_observations.return_value = [
            {"date": "2023-01-01", "value": "100"}
        ]
        mock_instance.save_observations.return_value = 1

        # Execute
        result = fetcher.fetch_single_indicator(sample_config)

        # Assert
        assert result is True
        mock_instance.get_series_info.assert_called_with("TEST_SERIES")
        mock_instance.get_series_observations.assert_called()
        mock_instance.save_observations.assert_called()

        # Check config update
        sample_config.refresh_from_db()
        assert sample_config.fetch_status == "success"

    @patch("fred_us.auto_fetcher.UsFredDataFetcher")
    def test_fetch_single_indicator_failure(self, mock_fetcher_cls, fetcher, sample_config):
        # Setup mock to fail
        mock_instance = mock_fetcher_cls.return_value
        mock_instance.get_series_info.return_value = {}
        mock_instance.get_series_observations.side_effect = Exception("API Error")

        # Execute
        result = fetcher.fetch_single_indicator(sample_config)

        # Assert
        assert result is False

        # Check config update
        sample_config.refresh_from_db()
        assert sample_config.fetch_status == "failed"
        assert "API Error" in str(sample_config.additional_config.get("last_error", ""))

    def test_should_fetch_indicator(self, fetcher, sample_config):
        # Should fetch if no last_fetch_time
        assert fetcher.should_fetch_indicator(sample_config) is True

        # Should NOT fetch if recently fetched
        sample_config.last_fetch_time = timezone.now()
        sample_config.save()
        assert fetcher.should_fetch_indicator(sample_config) is False

        # Should fetch if time passed
        sample_config.last_fetch_time = timezone.now() - timezone.timedelta(hours=25)
        sample_config.save()
        assert fetcher.should_fetch_indicator(sample_config) is True
