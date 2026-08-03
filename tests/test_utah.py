"""Tests for the Utah 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.utah import UtahProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{UtahProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build a UtahProvider bound to the mocked aiohttp session."""
    return UtahProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_utah_provider_registered():
    """Utah should be registered under its provider_id."""
    assert get_provider_class("utah") is UtahProvider


def test_utah_capabilities():
    """Utah supports cameras, incidents, road conditions, and weather."""
    provider = UtahProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query roadconditions v2 and weatherstations."""
    for url in (
        _url("cameras"),
        _url("event"),
        _url("roadconditions", version=2),
        _url("weatherstations"),
    ):
        aioclient_mock.get(url, params={"key": API_KEY, "format": "json"}, json=[])

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 4


async def test_road_conditions_use_roadconditions_v2_and_road_condition_field(
    hass, aioclient_mock
):
    """Utah road conditions report status under the RoadCondition field."""
    aioclient_mock.get(
        _url("roadconditions", version=2),
        json=[
            {
                "RoadwayName": "I-15",
                "RoadCondition": "Snow Covered",
                "WeatherCondition": "Snow",
                "Restriction": "No Restrictions",
            }
        ],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    assert conditions[0].road == "I-15"
    assert conditions[0].surface == "Snow Covered"


async def test_weather_stations_parse_utah_aliases(hass, aioclient_mock):
    """Utah weather uses DewpointTemp and WindSpeedAvg field names."""
    aioclient_mock.get(
        _url("weatherstations"),
        json=[
            {
                "Id": 6401,
                "StationName": "Parley's Summit",
                "AirTemperature": "24 °F",
                "RelativeHumidity": "88 %",
                "DewpointTemp": "21 °F",
                "WindSpeedAvg": "10 mph",
                "WindDirection": "N",
            }
        ],
    )

    stations = await _provider(hass).async_get_weather()

    assert len(stations) == 1
    station = stations[0]
    assert station.name == "Parley's Summit"
    assert station.temperature == -4.4
    assert station.dewpoint == -6.1
    assert station.humidity == 88.0
    assert station.wind == "N 10 mph"
