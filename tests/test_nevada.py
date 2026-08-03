"""Tests for the Nevada 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.nevada import NevadaProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{NevadaProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a NevadaProvider bound to the mocked aiohttp session."""
    return NevadaProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_nevada_provider_registered():
    """Nevada should be registered under its provider_id."""
    assert get_provider_class("nevada") is NevadaProvider


def test_nevada_capabilities():
    """Nevada supports cameras, incidents, road conditions, and weather."""
    provider = NevadaProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query roadconditions v3 and weatherstations."""
    for url in (
        _url("cameras"),
        _url("event"),
        _url("roadconditions", version=3),
        _url("weatherstations"),
    ):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 4


async def test_road_conditions_use_roadconditions_v3(hass, aioclient_mock):
    """Road conditions come from the roadconditions resource, not winterroads."""
    aioclient_mock.get(
        _url("roadconditions", version=3),
        json=[{"RoadwayName": "US-395", "Overall Status": "Snow Packed"}],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    assert conditions[0].road == "US-395"
    assert conditions[0].surface == "Snow Packed"


async def test_weather_stations_parse_named_aliases(hass, aioclient_mock):
    """Nevada weather uses StationName, Dewpoint, and Wind field names."""
    aioclient_mock.get(
        _url("weatherstations"),
        json=[
            {
                "Id": 2302,
                "StationName": "Mt. Rose Summit",
                "AirTemperature": "38 °F",
                "RelativeHumidity": "70 %",
                "Dewpoint": "30 °F",
                "Wind": "25 mph",
                "WindDirection": "SW",
            }
        ],
    )

    stations = await _provider(hass).async_get_weather()

    assert len(stations) == 1
    station = stations[0]
    assert station.name == "Mt. Rose Summit"
    assert station.temperature == 3.3
    assert station.dewpoint == -1.1
    assert station.humidity == 70.0
    assert station.wind == "SW 25 mph"
