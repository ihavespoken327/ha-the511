"""Tests for the Wisconsin 511 provider."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.wisconsin import (
    CAMERAS_URL,
    EVENTS_URL,
    WINTER_ROADS_URL,
    WisconsinProvider,
)

API_KEY = "test-key"


def _provider(hass):
    """Build a WisconsinProvider bound to the mocked aiohttp session."""
    return WisconsinProvider(
        session=async_get_clientsession(hass),
        config={CONF_API_KEY: API_KEY},
    )


def test_wisconsin_provider_registered():
    """Wisconsin should be registered under its provider_id."""
    assert get_provider_class("wisconsin") is WisconsinProvider


def test_wisconsin_capabilities():
    """Wisconsin supports cameras, incidents, and road conditions."""
    provider = WisconsinProvider(session=None, config={CONF_API_KEY: API_KEY})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_road_conditions
    assert not provider.supports_weather


async def test_update_fetches_all_supported_resources(hass, aioclient_mock):
    """async_update should query every supported resource with the api key."""
    aioclient_mock.get(CAMERAS_URL, params={"key": API_KEY, "format": "json"}, json=[])
    aioclient_mock.get(EVENTS_URL, params={"key": API_KEY, "format": "json"}, json=[])
    aioclient_mock.get(
        WINTER_ROADS_URL, params={"key": API_KEY, "format": "json"}, json=[]
    )

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3


async def test_cameras_use_first_enabled_view(hass, aioclient_mock):
    """Camera parsing should pick the first enabled view."""
    aioclient_mock.get(
        CAMERAS_URL,
        json=[
            {
                "Id": 42,
                "Roadway": "I-94",
                "Direction": "East",
                "Latitude": 43.0,
                "Longitude": -89.0,
                "Location": "Madison",
                "Views": [
                    {
                        "Url": "https://example.com/disabled.jpg",
                        "Status": "Disabled",
                    },
                    {
                        "Url": "https://example.com/live.jpg",
                        "Status": "Enabled",
                        "VideoUrl": "https://example.com/live.m3u8",
                    },
                ],
            }
        ],
    )

    cameras = await _provider(hass).async_get_cameras()

    assert len(cameras) == 1
    camera = cameras[0]
    assert camera.id == "42"
    assert camera.name == "Madison"
    assert camera.road == "I-94"
    assert camera.direction == "East"
    assert camera.latitude == 43.0
    assert camera.longitude == -89.0
    assert camera.image_url == "https://example.com/live.jpg"
    assert camera.video_url == "https://example.com/live.m3u8"
    assert camera.status == "Enabled"


async def test_camera_falls_back_to_first_view(hass, aioclient_mock):
    """Without an enabled view the first view should be used."""
    aioclient_mock.get(
        CAMERAS_URL,
        json=[
            {
                "Id": 7,
                "Location": "Beloit",
                "Views": [{"Url": "https://example.com/cam.jpg"}],
            }
        ],
    )

    cameras = await _provider(hass).async_get_cameras()

    assert cameras[0].id == "7"
    assert cameras[0].name == "Beloit"
    assert cameras[0].image_url == "https://example.com/cam.jpg"
    assert cameras[0].road is None


async def test_camera_missing_fields_have_stable_fallbacks(hass, aioclient_mock):
    """Missing identity fields should not produce None names or ids."""
    aioclient_mock.get(CAMERAS_URL, json=[{}])

    cameras = await _provider(hass).async_get_cameras()

    assert cameras[0].id == "Unknown"
    assert cameras[0].name == "Unknown"
    assert cameras[0].image_url is None


async def test_incidents_parse(hass, aioclient_mock):
    """Event resources should be normalized into incidents."""
    aioclient_mock.get(
        EVENTS_URL,
        json=[
            {
                "ID": 101,
                "RoadwayName": "US-51",
                "Description": "Crash",
                "Comment": "Right lane blocked",
                "EventType": "Crash",
                "Severity": "Moderate",
                "Latitude": 43.5,
                "Longitude": -89.2,
            }
        ],
    )

    incidents = await _provider(hass).async_get_incidents()

    assert len(incidents) == 1
    incident = incidents[0]
    assert incident.id == "101"
    assert incident.title == "Crash"
    assert incident.description == "Right lane blocked"
    assert incident.event_type == "Crash"
    assert incident.severity == "Moderate"
    assert incident.latitude == 43.5
    assert incident.road == "US-51"


async def test_incident_missing_fields_have_stable_fallbacks(hass, aioclient_mock):
    """Missing event fields should fall back to Unknown for identity."""
    aioclient_mock.get(EVENTS_URL, json=[{}])

    incidents = await _provider(hass).async_get_incidents()

    assert incidents[0].id == "Unknown"
    assert incidents[0].title == "Unknown"
    assert incidents[0].description is None


async def test_road_conditions_parse(hass, aioclient_mock):
    """Winter roads should be normalized into road conditions."""
    aioclient_mock.get(
        WINTER_ROADS_URL,
        json=[{"RoadwayName": "I-90", "Overall Status": "Partially covered"}],
    )

    conditions = await _provider(hass).async_get_road_conditions()

    assert len(conditions) == 1
    condition = conditions[0]
    assert condition.road == "I-90"
    assert condition.surface == "Partially covered"
