"""Tests for the Newfoundland and Labrador 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.newfoundland_and_labrador import (
    NewfoundlandLabradorProvider,
)

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{NewfoundlandLabradorProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a provider bound to the mocked aiohttp session."""
    return NewfoundlandLabradorProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_newfoundland_provider_registered():
    """Newfoundland and Labrador should be registered under its provider_id."""
    assert (
        get_provider_class("newfoundland_and_labrador") is NewfoundlandLabradorProvider
    )


def test_newfoundland_capabilities():
    """Newfoundland supports cameras, incidents, and road conditions."""
    provider = NewfoundlandLabradorProvider(
        session=None, config={CONF_API_KEY: API_KEY}
    )

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query cameras, event, and winter roads with the key."""
    for url in (
        _url("cameras"),
        _url("event"),
        _url("winterroads", version=3),
    ):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3


async def test_road_conditions_use_primary_condition(hass, aioclient_mock):
    """Newfoundland winter roads report the surface under ``Primary Condition``."""
    aioclient_mock.get(
        _url("winterroads", version=3),
        json=[{"RoadwayName": "TCH", "Primary Condition": "Wet"}],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    assert conditions[0].road == "TCH"
    assert conditions[0].surface == "Wet"
