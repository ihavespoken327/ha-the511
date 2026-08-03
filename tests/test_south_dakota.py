"""Tests for the South Dakota 511 provider."""

from __future__ import annotations

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.south_dakota import SouthDakotaProvider


def _url(layer: str) -> str:
    """Build the expected CDN URL for a layer."""
    base = SouthDakotaProvider.base_url
    return f"{base}/geojson/icons/metadata/icons.{layer}.geojson"


def _provider(hass):
    """Build a provider bound to the mocked aiohttp session."""
    return SouthDakotaProvider(session=async_get_clientsession(hass), config={})


def test_south_dakota_provider_registered():
    """South Dakota should be registered under its provider_id."""
    assert get_provider_class("south_dakota") is SouthDakotaProvider


def test_south_dakota_capabilities():
    """South Dakota supports cameras only (other layers are gated)."""
    provider = SouthDakotaProvider(session=None, config={})

    assert provider.supports_cameras
    assert not provider.supports_incidents
    assert not provider.supports_message_signs
    assert provider.cameras_nested
    assert not provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times
    assert SouthDakotaProvider.required_config_keys == ()


async def test_update_fetches_only_cameras(hass, aioclient_mock):
    """async_update should query just the cameras layer."""
    aioclient_mock.get(_url("cameras"), json={"features": []})

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 1
