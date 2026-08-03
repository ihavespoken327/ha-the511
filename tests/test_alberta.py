"""Tests for the Alberta 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.alberta import AlbertaProvider


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{AlbertaProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build an AlbertaProvider bound to the mocked aiohttp session."""
    return AlbertaProvider(
        session=async_get_clientsession(hass),
        config={},
    )


def test_alberta_provider_registered():
    """Alberta should be registered under its provider_id."""
    assert get_provider_class("alberta") is AlbertaProvider


def test_alberta_capabilities():
    """Alberta supports cameras, incidents, road conditions, and weather."""
    provider = AlbertaProvider(session=None, config={})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert provider.supports_weather
    assert not provider.supports_travel_times


def test_alberta_open_api_needs_no_key():
    """Alberta publishes openly: the key must not be required or sent."""
    provider = AlbertaProvider(session=None, config={})

    assert CONF_API_KEY not in AlbertaProvider.required_config_keys
    assert CONF_API_KEY not in AlbertaProvider.secret_config_keys
    assert provider._api_key is None


async def test_update_fetches_all_supported_resources_without_key(hass, aioclient_mock):
    """async_update should query cameras, event, winter roads, and weather."""
    for url in (
        _url("cameras"),
        _url("event"),
        _url("winterroads", version=3),
        _url("weatherstations"),
    ):
        aioclient_mock.get(url, params={"format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 4


async def test_road_conditions_use_primary_condition(hass, aioclient_mock):
    """Alberta winter roads report the surface under ``Primary Condition``."""
    aioclient_mock.get(
        _url("winterroads", version=3),
        json=[{"RoadwayName": "AB-2", "Primary Condition": "Bare Dry"}],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    assert conditions[0].road == "AB-2"
    assert conditions[0].surface == "Bare Dry"


async def test_weather_parses_celsius_and_degrees_wind(hass, aioclient_mock):
    """Weather readings are metric and wind direction is a bearing."""
    aioclient_mock.get(
        _url("weatherstations"),
        json=[
            {
                "Id": 1,
                "StationName": "Calgary",
                "AirTemperature": "14.4",
                "RelativeHumidity": "62 %",
                "Dewpoint": "5.2",
                "Speed": "9.7",
                "WindDirection": "286",
            }
        ],
    )

    stations = await _provider(hass).async_get_weather()

    assert len(stations) == 1
    station = stations[0]
    assert station.name == "Calgary"
    assert station.temperature == 14.4
    assert station.humidity == 62.0
    assert station.dewpoint == 5.2
    assert station.wind == "WNW 9.7"
