"""Tests for the Louisiana 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.louisiana import LouisianaProvider

API_KEY = "test-key"


def _url(resource: str) -> str:
    """Build the expected platform URL for a resource."""
    return f"{LouisianaProvider.base_url}/api/v2/get/{resource}"


def _provider(hass):
    """Build a LouisianaProvider bound to the mocked aiohttp session."""
    return LouisianaProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_louisiana_provider_registered():
    """Louisiana should be registered under its provider_id."""
    assert get_provider_class("louisiana") is LouisianaProvider


def test_louisiana_capabilities():
    """Louisiana supports cameras, incidents, and travel times."""
    provider = LouisianaProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_travel_times
    assert not provider.supports_road_conditions
    assert not provider.supports_weather


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query every supported resource with the api key."""
    aioclient_mock.get(
        _url("cameras"), params={"key": API_KEY, "format": "json"}, json=[]
    )
    aioclient_mock.get(
        _url("event"), params={"key": API_KEY, "format": "json"}, json=[]
    )
    aioclient_mock.get(
        _url("traveltimes"), params={"key": API_KEY, "format": "json"}, json=[]
    )

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3


async def test_cameras_parse(hass, aioclient_mock):
    """Camera resources should be normalized with the enabled view."""
    aioclient_mock.get(
        _url("cameras"),
        json=[
            {
                "Id": 1,
                "Source": "LADOTD",
                "Roadway": "I-20",
                "Latitude": 32.538889,
                "Longitude": -93.630833,
                "Location": "I-20 at I-220 Off Ramp",
                "Views": [
                    {
                        "Url": "https://example.com/cam-1.jpg",
                        "Status": "Enabled",
                        "VideoUrl": "https://example.com/cam-1.m3u8",
                    }
                ],
            }
        ],
    )

    cameras = await _provider(hass).async_get_cameras()

    assert len(cameras) == 1
    camera = cameras[0]
    assert camera.id == "1"
    assert camera.name == "I-20 at I-220 Off Ramp"
    assert camera.road == "I-20"
    assert camera.latitude == 32.538889
    assert camera.image_url == "https://example.com/cam-1.jpg"
    assert camera.video_url == "https://example.com/cam-1.m3u8"


async def test_incidents_parse(hass, aioclient_mock):
    """Event resources should be normalized into incidents."""
    aioclient_mock.get(
        _url("event"),
        json=[
            {
                "ID": 21,
                "RoadwayName": "LA-29",
                "Description": "Floodgate Closure on LA-29",
                "EventType": "weatherConditions",
                "Severity": "None",
                "Latitude": 30.9509407534434,
                "Longitude": -92.181185022253,
            }
        ],
    )

    incidents = await _provider(hass).async_get_incidents()

    assert len(incidents) == 1
    incident = incidents[0]
    assert incident.id == "21"
    assert incident.title == "Floodgate Closure on LA-29"
    assert incident.event_type == "weatherConditions"
    assert incident.severity == "None"
    assert incident.latitude == 30.9509407534434
    assert incident.road == "LA-29"


async def test_travel_times_parse(hass, aioclient_mock):
    """Travel time resources should be normalized into travel times."""
    aioclient_mock.get(
        _url("traveltimes"),
        json=[
            {
                "Id": "I-10 New Orleans::77",
                "RoadwayName": "I-10",
                "Description": "I-10 WB Causeway to Loyola",
                "CurrentTime": 18.5,
                "NormalTime": 15.0,
                "Delay": 3.5,
                "Distance": 12.0,
            }
        ],
    )

    travel_times = await _provider(hass).async_get_travel_times()

    assert len(travel_times) == 1
    travel_time = travel_times[0]
    assert travel_time.id == "I-10 New Orleans::77"
    assert travel_time.name == "I-10 WB Causeway to Loyola"
    assert travel_time.road == "I-10"
    assert travel_time.minutes == 18.5
    assert travel_time.normal_minutes == 15.0
    assert travel_time.delay == 3.5
    assert travel_time.distance == 12.0
