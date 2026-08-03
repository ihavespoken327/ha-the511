"""Tests for the Arizona 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.arizona import ArizonaProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{ArizonaProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build an ArizonaProvider bound to the mocked aiohttp session."""
    return ArizonaProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_arizona_provider_registered():
    """Arizona should be registered under its provider_id."""
    assert get_provider_class("arizona") is ArizonaProvider


def test_arizona_capabilities():
    """Arizona supports cameras, incidents, and weather."""
    provider = ArizonaProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_weather
    assert not provider.supports_road_conditions
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query cameras, event, and weatherstations."""
    for url in (_url("cameras"), _url("event"), _url("weatherstations")):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3


async def test_weather_stations_parse_without_name_or_dewpoint(hass, aioclient_mock):
    """Arizona weather has no name/dewpoint field; parsing should tolerate it."""
    aioclient_mock.get(
        _url("weatherstations"),
        json=[
            {
                "Id": 4123,
                "AirTemperature": "95 °F",
                "RelativeHumidity": "12 %",
                "WindSpeed": "8 mph",
                "WindDirection": "W",
            }
        ],
    )

    stations = await _provider(hass).async_get_weather()

    assert len(stations) == 1
    station = stations[0]
    assert station.station_id == "4123"
    assert station.temperature == 35.0
    assert station.humidity == 12.0
    assert station.dewpoint is None
    assert station.wind == "W 8 mph"
