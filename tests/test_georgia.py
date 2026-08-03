"""Tests for the Georgia 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.georgia import GeorgiaProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{GeorgiaProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a GeorgiaProvider bound to the mocked aiohttp session."""
    return GeorgiaProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_georgia_provider_registered():
    """Georgia should be registered under its provider_id."""
    assert get_provider_class("georgia") is GeorgiaProvider


def test_georgia_capabilities():
    """Georgia supports only cameras and incidents."""
    provider = GeorgiaProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert not provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query cameras and event only."""
    for url in (_url("cameras"), _url("event")):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 2


async def test_incidents_parse(hass, aioclient_mock):
    """Events should be normalized into incidents."""
    aioclient_mock.get(
        _url("event"),
        json=[
            {
                "ID": "GATL_123",
                "Description": "Multi-vehicle crash",
                "Severity": "Moderate",
                "RoadwayName": "I-285",
            }
        ],
    )

    incidents = await _provider(hass).async_get_incidents()

    assert len(incidents) == 1
    assert incidents[0].id == "GATL_123"
    assert incidents[0].title == "Multi-vehicle crash"
    assert incidents[0].road == "I-285"
