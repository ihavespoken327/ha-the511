"""Tests for the Idaho 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.idaho import IdahoProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{IdahoProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build an IdahoProvider bound to the mocked aiohttp session."""
    return IdahoProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_idaho_provider_registered():
    """Idaho should be registered under its provider_id."""
    assert get_provider_class("idaho") is IdahoProvider


def test_idaho_capabilities():
    """Idaho supports cameras, incidents, road conditions, and weather."""
    provider = IdahoProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query all four supported resources."""
    for url in (
        _url("cameras"),
        _url("event"),
        _url("winterroads", version=3),
        _url("weatherstations"),
    ):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 4


async def test_weather_stations_parse_rich_fields(hass, aioclient_mock):
    """Idaho weather carries the richest field set; all readings map."""
    aioclient_mock.get(
        _url("weatherstations"),
        json=[
            {
                "Id": 5701,
                "StationName": "Lowman",
                "AirTemperature": "30 °F",
                "RelativeHumidity": "82 %",
                "DewpointTemperature": "25 °F",
                "WindSpeed": "5 mph",
                "WindDirection": "NE",
            }
        ],
    )

    stations = await _provider(hass).async_get_weather()

    assert len(stations) == 1
    station = stations[0]
    assert station.name == "Lowman"
    assert station.temperature == -1.1
    assert station.dewpoint == -3.9
    assert station.humidity == 82.0
    assert station.wind == "NE 5 mph"
