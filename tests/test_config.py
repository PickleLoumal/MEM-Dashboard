import pytest
from django.conf import settings


def test_django_configuration():
    """Smoke test to verify Django settings are loaded."""
    assert settings.configured
    assert hasattr(settings, "INSTALLED_APPS")
