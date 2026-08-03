"""Tests for the Alaska 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.alaska import AlaskaProvider

API_KEY = "test-key"


def _url(resource: str, version: int = 2) -> str:
    """Build the expected platform URL for a resource."""
    return f"{AlaskaProvider.base_url}/api/v{version}/get/{resource}"


def _provider(hass):
    """Build an AlaskaProvider bound to the mocked aiohttp session."""
    return AlaskaProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_alaska_provider_registered():
    """Alaska should be registered under its provider_id."""
    assert get_provider_class("alaska") is AlaskaProvider


def test_alaska_capabilities():
    """Alaska supports cameras, incidents, road conditions, and weather."""
    provider = AlaskaProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert provider.supports_weather
    assert not provider.supports_travel_times


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query every supported resource with the api key."""
    aioclient_mock.get(
        _url("cameras"), params={"key": API_KEY, "format": "json"}, json=[]
    )
    aioclient_mock.get(
        _url("event"), params={"key": API_KEY, "format": "json"}, json=[]
    )
    aioclient_mock.get(
        _url("winterroads", version=3),
        params={"key": API_KEY, "format": "json"},
        json=[],
    )
    aioclient_mock.get(
        _url("weatherstations"), params={"key": API_KEY, "format": "json"}, json=[]
    )

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 4


async def test_cameras_parse(hass, aioclient_mock):
    """Camera resources should be normalized with the enabled view."""
    aioclient_mock.get(
        _url("cameras"),
        json=[
            {
                "Id": 2,
                "Roadway": "Seward Highway",
                "Direction": "North",
                "Latitude": 60.929619,
                "Longitude": -149.346632,
                "Location": "Seward Highway @ Bird Point MP 96.3",
                "Views": [
                    {
                        "Url": "https://example.com/bird-point.jpg",
                        "Status": "Enabled",
                    }
                ],
            }
        ],
    )

    cameras = await _provider(hass).async_get_cameras()

    assert len(cameras) == 1
    camera = cameras[0]
    assert camera.id == "2"
    assert camera.name == "Seward Highway @ Bird Point MP 96.3"
    assert camera.road == "Seward Highway"
    assert camera.direction == "North"
    assert camera.latitude == 60.929619
    assert camera.image_url == "https://example.com/bird-point.jpg"
    assert camera.status == "Enabled"


async def test_road_conditions_parse(hass, aioclient_mock):
    """Winter roads should be normalized into road conditions."""
    aioclient_mock.get(
        _url("winterroads", version=3),
        json=[
            {
                "RoadwayName": "Seward Hwy",
                "Overall Status": "Hazardous",
                "LocationDescription": "from Rabbit Creek to Tudor",
            }
        ],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    condition = conditions[0]
    assert condition.road == "Seward Hwy"
    assert condition.surface == "Hazardous"


async def test_weather_stations_parse(hass, aioclient_mock):
    """Weather stations should be normalized with Fahrenheit converted to Celsius."""
    aioclient_mock.get(
        _url("weatherstations"),
        json=[
            {
                "Id": 12082,
                "AirTemperature": "20 °F",
                "SurfaceTemperature": "23 °F",
                "Dewpoint": "18 °F",
                "RelativeHumidity": "90 %",
                "WindSpeed": "2 mph",
                "Direction": "W",
            }
        ],
    )

    stations = await _provider(hass).async_get_weather()

    assert len(stations) == 1
    station = stations[0]
    assert station.station_id == "12082"
    assert station.temperature == -6.7
    assert station.dewpoint == -7.8
    assert station.humidity == 90.0
    assert station.wind == "W 2 mph"
    assert station.visibility is None


async def test_weather_station_missing_fields_are_tolerated(hass, aioclient_mock):
    """Missing station readings should not raise."""
    aioclient_mock.get(_url("weatherstations"), json=[{"Id": 12081}])

    stations = await _provider(hass).async_get_weather()

    assert stations[0].station_id == "12081"
    assert stations[0].temperature is None
    assert stations[0].humidity is None
    assert stations[0].wind is None
