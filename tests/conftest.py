"""Shared fixtures for The 511 tests."""

from __future__ import annotations

import pytest
from homeassistant.const import CONF_API_KEY

from custom_components.the511.models import CameraData
from custom_components.the511.providers import PROVIDERS, BaseProvider


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations so hass can load the511."""
    return enable_custom_integrations


@pytest.fixture
def fake_provider_class():
    """Register a fake provider in the registry, unregistering afterwards."""

    class FakeProvider(BaseProvider):
        provider_id = "fake"
        name = "Fake 511"
        region = "Fake Region"
        supports_cameras = True
        supports_incidents = True

        async def async_get_cameras(self) -> list[CameraData]:
            return [
                CameraData(
                    id="cam-1",
                    name="Test Camera",
                    image_url="https://example.com/cam-1.jpg",
                )
            ]

    PROVIDERS[FakeProvider.provider_id] = FakeProvider
    yield FakeProvider
    PROVIDERS.pop(FakeProvider.provider_id, None)


@pytest.fixture
def secret_provider_class():
    """Register a provider that requires an api key, unregistering afterwards."""

    class SecretProvider(BaseProvider):
        provider_id = "secret"
        name = "Secret 511"
        region = "Secret Region"
        supports_cameras = True

        required_config_keys = (CONF_API_KEY,)
        secret_config_keys = (CONF_API_KEY,)

        async def async_get_cameras(self) -> list[CameraData]:
            return []

    PROVIDERS[SecretProvider.provider_id] = SecretProvider
    yield SecretProvider
    PROVIDERS.pop(SecretProvider.provider_id, None)
