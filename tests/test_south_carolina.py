"""Tests for the South Carolina 511 provider."""

from __future__ import annotations

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.south_carolina import SouthCarolinaProvider


def _url(layer: str) -> str:
    """Build the expected CDN URL for a layer."""
    base = SouthCarolinaProvider.base_url
    return f"{base}/geojson/icons/metadata/icons.{layer}.geojson"


def _provider(hass):
    """Build a provider bound to the mocked aiohttp session."""
    return SouthCarolinaProvider(session=async_get_clientsession(hass), config={})


def test_south_carolina_provider_registered():
    """South Carolina should be registered under its provider_id."""
    assert get_provider_class("south_carolina") is SouthCarolinaProvider


def test_south_carolina_capabilities():
    """South Carolina supports cameras and incidents, keylessly."""
    provider = SouthCarolinaProvider(session=None, config={})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert not provider.supports_message_signs
    assert not provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times
    assert SouthCarolinaProvider.required_config_keys == ()


async def test_update_fetches_cameras_incident_and_construction(hass, aioclient_mock):
    """async_update should query the open GeoJSON layers with no key."""
    for layer in ("cameras", "incident", "construction"):
        aioclient_mock.get(_url(layer), json={"features": []})

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3
