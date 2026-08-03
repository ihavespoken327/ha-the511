"""Tests for the New York 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.new_york import NewYorkProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{NewYorkProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a NewYorkProvider bound to the mocked aiohttp session."""
    return NewYorkProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_new_york_provider_registered():
    """New York should be registered under its provider_id."""
    assert get_provider_class("new_york") is NewYorkProvider


def test_new_york_capabilities():
    """New York supports cameras, incidents, and road conditions."""
    provider = NewYorkProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query cameras, event, and winter roads v3."""
    for url in (
        _url("cameras"),
        _url("event"),
        _url("winterroads", version=3),
    ):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3


async def test_road_conditions_use_winter_roads_v3(hass, aioclient_mock):
    """Winter roads v3 should be normalized into road conditions."""
    aioclient_mock.get(
        _url("winterroads", version=3),
        json=[
            {
                "RoadwayName": "I-87",
                "Overall Status": "Closed",
                "LocationDescription": "between exits 9 and 11",
            }
        ],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    assert conditions[0].road == "I-87"
    assert conditions[0].surface == "Closed"
