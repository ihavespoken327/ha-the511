"""Tests for the Connecticut 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.connecticut import ConnecticutProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{ConnecticutProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a ConnecticutProvider bound to the mocked aiohttp session."""
    return ConnecticutProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_connecticut_provider_registered():
    """Connecticut should be registered under its provider_id."""
    assert get_provider_class("connecticut") is ConnecticutProvider


def test_connecticut_capabilities():
    """Connecticut supports only incidents."""
    provider = ConnecticutProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_incidents
    assert not provider.supports_cameras
    assert not provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_event_only(hass, aioclient_mock):
    """async_update should query the event resource only."""
    aioclient_mock.get(
        _url("event"), params={"key": API_KEY, "format": "json"}, json=[]
    )

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 1
