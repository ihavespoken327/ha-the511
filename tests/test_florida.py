"""Tests for the Florida 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.florida import FloridaProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{FloridaProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a FloridaProvider bound to the mocked aiohttp session."""
    return FloridaProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_florida_provider_registered():
    """Florida should be registered under its provider_id."""
    assert get_provider_class("florida") is FloridaProvider


def test_florida_capabilities():
    """Florida supports cameras and incidents only."""
    provider = FloridaProvider(session=None, config={CONF_API_KEY: API_KEY})

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


async def test_cameras_parse(hass, aioclient_mock):
    """Camera resources should be normalized like other states."""
    aioclient_mock.get(
        _url("cameras"),
        json=[
            {
                "Id": 901,
                "Location": "I-95 @ Hollywood Blvd",
                "Roadway": "I-95",
                "Latitude": 26.01,
                "Longitude": -80.15,
                "Views": [{"Url": "https://example.com/hwd.jpg", "Status": "Enabled"}],
            }
        ],
    )

    cameras = await _provider(hass).async_get_cameras()

    assert len(cameras) == 1
    assert cameras[0].id == "901"
    assert cameras[0].name == "I-95 @ Hollywood Blvd"
    assert cameras[0].road == "I-95"
    assert cameras[0].image_url == "https://example.com/hwd.jpg"
