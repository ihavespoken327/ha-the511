"""Tests for the shared Iteris/ATG GeoJSON provider base."""

from __future__ import annotations

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers.iteris_atis import (
    IterisAtisProvider,
    _active_status,
    _feature_point,
    _site_key,
    _strip_html,
)


class FlatCamerasProvider(IterisAtisProvider):
    """A base provider with one camera per feature."""

    provider_id = "flat-cameras"
    base_url = "https://flat.example.com"

    supports_cameras = True


class NestedCamerasProvider(IterisAtisProvider):
    """A base provider that groups cameras per road site."""

    provider_id = "nested-cameras"
    base_url = "https://nested.example.com"

    supports_cameras = True
    cameras_nested = True


class EventsProvider(IterisAtisProvider):
    """A base provider with live incidents and construction layers."""

    provider_id = "events"
    base_url = "https://events.example.com"

    supports_incidents = True
    incident_layers = ("incident", "construction")


def _url(base_url: str, layer: str) -> str:
    """Build the expected CDN URL for a layer."""
    return f"{base_url}/geojson/icons/metadata/icons.{layer}.geojson"


def _provider(hass, provider_class):
    """Build a provider bound to the mocked aiohttp session."""
    return provider_class(session=async_get_clientsession(hass), config={})


def test_iteris_atis_requires_no_api_key():
    """The GeoJSON layers are open; setup needs no credentials."""
    assert IterisAtisProvider.required_config_keys == ()
    assert IterisAtisProvider.secret_config_keys == ()


def test_feature_point_parses_coordinates():
    """Point coordinates are returned as (latitude, longitude)."""
    feature = {"geometry": {"type": "Point", "coordinates": [-80.997286, 33.948503]}}
    assert _feature_point(feature) == (33.948503, -80.997286)
    assert _feature_point({"geometry": {"coordinates": ["-80.9", "34.9"]}}) == (
        34.9,
        -80.9,
    )
    assert _feature_point({}) == (None, None)
    assert _feature_point({"geometry": {}}) == (None, None)
    assert _feature_point({"geometry": {"coordinates": []}}) == (None, None)
    assert _feature_point({"geometry": {"coordinates": ["n/a", 3]}}) == (None, None)


def test_site_key_prefers_id_then_route_mrm_then_name():
    """Road-site identity prefers id, then route+mrm, then the site name."""
    assert _site_key({"id": "6683", "route": "I-90", "mrm": 16.5}) == "6683"
    assert _site_key({"route": "I-29", "mrm": "179"}) == "I-29 179"
    assert _site_key({"route": "I-29", "mrm": "unavailable", "name": "Town"}) == "Town"
    assert _site_key({"route": "I-29", "mrm": "unavailable"}) == "Unknown"
    assert _site_key({"name": "Town"}) == "Town"


def test_active_status_maps_boolean():
    """The boolean active flag becomes the platform status vocabulary."""
    assert _active_status(True) == "Enabled"
    assert _active_status(False) == "Disabled"
    assert _active_status(None) is None


def test_strip_html_removes_tags():
    """HTML tags are removed from free-text event reports."""
    assert _strip_html("STAY ALIVE<br><br>DON'T DRINK & DRIVE") == (
        "STAY ALIVE DON'T DRINK & DRIVE"
    )
    assert _strip_html("plain text") == "plain text"
    assert _strip_html(None) is None
    assert _strip_html("<b></b>") is None


async def test_flat_camera_parse(hass, aioclient_mock):
    """One camera per feature is normalized from the SC-style schema."""
    aioclient_mock.get(
        _url(FlatCamerasProvider.base_url, "cameras"),
        json={
            "total_streams": 1,
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-80.997286, 33.948503],
                    },
                    "properties": {
                        "guid": "b22cd0fa2004472fa3e063db",
                        "id": "2735",
                        "name": "10002",
                        "description": "I-77 S @ MM 4.9",
                        "route": "I-77",
                        "direction": "SB",
                        "image_url": "https://example.com/thumb.png",
                        "https_url": "https://example.com/playlist.m3u8",
                        "active": True,
                    },
                }
            ],
        },
    )

    cameras = await _provider(hass, FlatCamerasProvider).async_get_cameras()

    assert len(cameras) == 1
    camera = cameras[0]
    assert camera.id == "2735"
    assert camera.name == "I-77 S @ MM 4.9"
    assert camera.image_url == "https://example.com/thumb.png"
    assert camera.video_url == "https://example.com/playlist.m3u8"
    assert camera.road == "I-77"
    assert camera.direction == "SB"
    assert camera.latitude == 33.948503
    assert camera.longitude == -80.997286
    assert camera.status == "Enabled"


async def test_flat_camera_missing_fields_fall_back(hass, aioclient_mock):
    """Missing identity fields produce stable Unknown ids and names."""
    aioclient_mock.get(
        _url(FlatCamerasProvider.base_url, "cameras"),
        json={"features": [{}]},
    )

    cameras = await _provider(hass, FlatCamerasProvider).async_get_cameras()

    assert cameras[0].id == "Unknown"
    assert cameras[0].name == "Unknown"
    assert cameras[0].image_url is None
    assert cameras[0].status is None


async def test_nested_camera_parse(hass, aioclient_mock):
    """Road-site features flatten into one camera per nested camera."""
    aioclient_mock.get(
        _url(NestedCamerasProvider.base_url, "cameras"),
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-108.621555, 44.96677],
                    },
                    "properties": {
                        "id": "6683",
                        "route": "WY US-310",
                        "cameras": [
                            {
                                "id": "6683-1",
                                "name": "View Facing South",
                                "direction": "South",
                                "image": "https://example.com/6683.jpg",
                            }
                        ],
                    },
                },
                {
                    "geometry": {"type": "Point", "coordinates": [-97.06, 44.95]},
                    "properties": {
                        "route": "I-29",
                        "mrm": "179",
                        "name": "Watertown North",
                        "cameras": [
                            {
                                "id": "1",
                                "name": "Camera Looking South",
                                "image": "https://example.com/1.jpg",
                            }
                        ],
                    },
                },
            ],
        },
    )

    cameras = await _provider(hass, NestedCamerasProvider).async_get_cameras()

    assert [camera.id for camera in cameras] == ["6683-1", "I-29 179-1"]
    assert cameras[0].name == "View Facing South"
    assert cameras[0].road == "WY US-310"
    assert cameras[0].direction == "South"
    assert cameras[0].latitude == 44.96677
    assert cameras[0].longitude == -108.621555
    assert cameras[0].image_url == "https://example.com/6683.jpg"
    assert cameras[1].road == "I-29"
    assert cameras[1].latitude == 44.95


async def test_nested_site_without_cameras_yields_nothing(hass, aioclient_mock):
    """A road site with no cameras array contributes no cameras."""
    aioclient_mock.get(
        _url(NestedCamerasProvider.base_url, "cameras"),
        json={"features": [{"properties": {"route": "I-29"}}]},
    )

    cameras = await _provider(hass, NestedCamerasProvider).async_get_cameras()

    assert cameras == []


async def test_incident_and_construction_parse(hass, aioclient_mock):
    """Live incidents keep their headline type; construction is roadwork."""
    aioclient_mock.get(
        _url(EventsProvider.base_url, "incident"),
        json={
            "features": [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-80.384034, 33.570697],
                    },
                    "id": "event_1151450",
                    "properties": {
                        "event_id": "event_1151450",
                        "headline": "Crash",
                        "route": "I-95",
                        "location_description": "I-95N: at MM 106",
                    },
                }
            ]
        },
    )
    aioclient_mock.get(
        _url(EventsProvider.base_url, "construction"),
        json={
            "features": [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": ["-80.984183", "34.967800"],
                    },
                    "properties": {
                        "event_id": "event_1151290",
                        "headline": "construction work",
                        "route": "I-77",
                        "location_description": "I-77S: between MM 81 and Exit 77",
                    },
                }
            ]
        },
    )

    incidents = await _provider(hass, EventsProvider).async_get_incidents()

    assert len(incidents) == 2
    live, roadwork = incidents
    assert live.id == "event_1151450"
    assert live.title == "Crash"
    assert live.event_type == "Crash"
    assert live.road == "I-95"
    assert live.description == "I-95N: at MM 106"
    assert live.latitude == 33.570697
    assert roadwork.id == "event_1151290"
    assert roadwork.title == "construction work"
    assert roadwork.event_type == "Roadwork"
    assert roadwork.latitude == 34.9678


async def test_event_report_html_is_stripped(hass, aioclient_mock):
    """MT-style rich-text reports are cleaned for the description."""
    aioclient_mock.get(
        _url(EventsProvider.base_url, "incident"),
        json={"features": []},
    )
    aioclient_mock.get(
        _url(EventsProvider.base_url, "construction"),
        json={
            "features": [
                {
                    "geometry": {"coordinates": [-112.36, 47.5]},
                    "properties": {
                        "event_id": "1037070",
                        "headline": "Road Work",
                        "route": "MT-21",
                        "report": (
                            "road construction in progress<br />Travelers can expect "
                            "reduced speeds."
                        ),
                    },
                }
            ]
        },
    )

    incidents = await _provider(hass, EventsProvider).async_get_incidents()

    assert incidents[0].description == (
        "road construction in progress Travelers can expect reduced speeds."
    )
