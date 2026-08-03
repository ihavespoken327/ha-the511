"""Tests for the North Carolina 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.north_carolina import NorthCarolinaProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{NorthCarolinaProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a provider bound to the mocked aiohttp session."""
    return NorthCarolinaProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_north_carolina_provider_registered():
    """North Carolina should be registered under its provider_id."""
    assert get_provider_class("north_carolina") is NorthCarolinaProvider


def test_north_carolina_capabilities():
    """North Carolina is limited to cameras and incidents (no public docs)."""
    provider = NorthCarolinaProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert not provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query only cameras and event with the key."""
    for url in (_url("cameras"), _url("event")):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 2
