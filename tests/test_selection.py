"""Tests for The 511 selection helpers (phase 11 entity bounds)."""

from __future__ import annotations

from custom_components.the511.const import (
    CONF_INCIDENT_RADIUS,
    CONF_MAX_CAMERAS,
    CONF_MAX_INCIDENTS,
    CONF_MAX_MESSAGE_SIGNS,
    CONF_MAX_ROAD_CONDITIONS,
    CONF_MAX_TRAVEL_TIMES,
    CONF_SHOW_ROADWORK,
    MAX_ENTITY_NAME_LENGTH,
)
from custom_components.the511.models import (
    CameraData,
    IncidentData,
    MessageSignData,
    RoadConditionData,
    TravelTimeData,
)
from custom_components.the511.selection import (
    haversine_km,
    is_roadwork,
    safe_name,
    select_cameras,
    select_incidents,
    select_message_signs,
    select_road_conditions,
    select_travel_times,
)

HOME_LAT = 43.0389
HOME_LON = -89.4575


def _options(overrides: dict | None = None) -> dict:
    """Return an options dict with defaults overridable for a test."""
    options = {
        CONF_MAX_CAMERAS: 25,
        CONF_MAX_INCIDENTS: 25,
        CONF_INCIDENT_RADIUS: 50,
        CONF_MAX_TRAVEL_TIMES: 25,
        CONF_MAX_ROAD_CONDITIONS: 25,
        CONF_MAX_MESSAGE_SIGNS: 25,
        CONF_SHOW_ROADWORK: False,
    }
    if overrides:
        options.update(overrides)
    return options


def _incident(incident_id: str, **fields) -> IncidentData:
    """Build an incident with sensible defaults and test overrides."""
    data = {
        "id": incident_id,
        "title": f"Incident {incident_id}",
        "event_type": "Crash",
        "latitude": HOME_LAT,
        "longitude": HOME_LON,
    }
    data.update(fields)
    return IncidentData(**data)


def _camera(camera_id: str, **fields) -> CameraData:
    """Build a camera with sensible defaults and test overrides."""
    data = {
        "id": camera_id,
        "name": f"Camera {camera_id}",
        "latitude": HOME_LAT,
        "longitude": HOME_LON,
    }
    data.update(fields)
    return CameraData(**data)


def _travel_time(travel_time_id: str, **fields) -> TravelTimeData:
    """Build a travel time route with sensible defaults and test overrides."""
    data = {
        "id": travel_time_id,
        "name": f"Route {travel_time_id}",
        "start_latitude": HOME_LAT,
        "start_longitude": HOME_LON,
    }
    data.update(fields)
    return TravelTimeData(**data)


def _road_condition(road: str, **fields) -> RoadConditionData:
    """Build a road condition with a road name and test overrides."""
    data = {"road": road}
    data.update(fields)
    return RoadConditionData(**data)


def _message_sign(sign_id: str, **fields) -> MessageSignData:
    """Build a message sign with sensible defaults and test overrides."""
    data = {"id": sign_id, "name": f"Sign {sign_id}"}
    data.update(fields)
    return MessageSignData(**data)


def test_haversine_km_zero():
    """Two identical coordinates are zero kilometers apart."""
    assert haversine_km(HOME_LAT, HOME_LON, HOME_LAT, HOME_LON) == 0.0


def test_haversine_km_known_distance():
    """The distance from home to a nearby city is a plausible few kilometers."""
    distance = haversine_km(HOME_LAT, HOME_LON, HOME_LAT + 0.05, HOME_LON)
    assert 5.0 < distance < 6.0


def test_safe_name_keeps_short_names():
    """Short names pass through untouched."""
    assert safe_name("I-94 at Rawson Ave") == "I-94 at Rawson Ave"


def test_safe_name_truncates_long_names():
    """Over-long names are truncated with a trailing ellipsis."""
    long_name = "X" * (MAX_ENTITY_NAME_LENGTH + 50)
    result = safe_name(long_name)
    assert len(result) == MAX_ENTITY_NAME_LENGTH
    assert result.endswith("…")
    assert result.startswith("X" * (MAX_ENTITY_NAME_LENGTH - 1))


def test_safe_name_falls_back_to_unknown():
    """Empty or missing names fall back to 'Unknown'."""
    assert safe_name(None) == "Unknown"
    assert safe_name("   ") == "Unknown"


def test_is_roadwork_detects_planned_events():
    """Planned construction events are flagged by title or event type."""
    assert is_roadwork(
        _incident("rw", title="Roadwork on I-90 EB", event_type="Roadwork")
    )
    assert not is_roadwork(_incident("crash", event_type="Crash"))


def test_select_incidents_drops_roadwork_by_default():
    """With show_roadwork off, planned events never surface."""
    incidents = [
        _incident("rw-1", title="Roadwork on I-94", event_type="Roadwork"),
        _incident("crash-1", event_type="Crash"),
    ]
    selected = select_incidents(hass_fake(), _entry(), incidents)
    assert [incident.id for incident in selected] == ["crash-1"]


def test_select_incidents_keeps_roadwork_when_requested():
    """With show_roadwork on, planned events surface too."""
    incidents = [
        _incident("rw-1", title="Roadwork on I-94", event_type="Roadwork"),
        _incident("crash-1", event_type="Crash"),
    ]
    selected = select_incidents(
        hass_fake(),
        _entry(_options({CONF_SHOW_ROADWORK: True})),
        incidents,
    )
    assert {incident.id for incident in selected} == {"crash-1", "rw-1"}


def test_select_incidents_applies_radius():
    """Incidents beyond the radius are dropped."""
    incidents = [
        _incident("near", latitude=HOME_LAT, longitude=HOME_LON),
        _incident(
            "far",
            latitude=HOME_LAT + 10.0,
            longitude=HOME_LON,
        ),
    ]
    selected = select_incidents(
        hass_fake(),
        _entry(_options({CONF_INCIDENT_RADIUS: 50})),
        incidents,
    )
    assert [incident.id for incident in selected] == ["near"]


def test_select_incidents_keeps_unknown_location_incidents():
    """Incidents without coordinates are not dropped by the radius."""
    incidents = [
        _incident("near", latitude=HOME_LAT, longitude=HOME_LON),
        _incident("no-coords", latitude=None, longitude=None),
        _incident(
            "far",
            latitude=HOME_LAT + 10.0,
            longitude=HOME_LON,
        ),
    ]
    selected = select_incidents(
        hass_fake(),
        _entry(_options({CONF_INCIDENT_RADIUS: 50})),
        incidents,
    )
    assert [incident.id for incident in selected] == ["near", "no-coords"]


def test_select_incidents_caps_and_ranks_nearest_first():
    """Only the nearest max_incidents are kept, in distance order."""
    incidents = [
        _incident(
            "far",
            latitude=HOME_LAT + 1.0,
            longitude=HOME_LON,
        ),
        _incident("near", latitude=HOME_LAT, longitude=HOME_LON),
        _incident(
            "mid",
            latitude=HOME_LAT + 0.5,
            longitude=HOME_LON,
        ),
    ]
    selected = select_incidents(
        hass_fake(),
        _entry(_options({CONF_MAX_INCIDENTS: 2})),
        incidents,
    )
    assert [incident.id for incident in selected] == ["near", "mid"]


def test_select_cameras_ranks_nearest_first():
    """Cameras are ranked by distance from home."""
    cameras = [
        _camera(
            "far",
            latitude=HOME_LAT + 2.0,
            longitude=HOME_LON,
        ),
        _camera("near", latitude=HOME_LAT, longitude=HOME_LON),
    ]
    selected = select_cameras(hass_fake(), _entry(), cameras)
    assert [camera.id for camera in selected] == ["near", "far"]


def test_select_cameras_caps():
    """Only the nearest max_cameras are kept."""
    cameras = [_camera(f"cam-{index}") for index in range(5)]
    selected = select_cameras(
        hass_fake(),
        _entry(_options({CONF_MAX_CAMERAS: 2})),
        cameras,
    )
    assert len(selected) == 2


def test_select_cameras_sorts_unknown_location_last():
    """Cameras without coordinates sort after positioned ones."""
    cameras = [
        _camera("no-coords", latitude=None, longitude=None),
        _camera("near", latitude=HOME_LAT, longitude=HOME_LON),
    ]
    selected = select_cameras(hass_fake(), _entry(), cameras)
    assert [camera.id for camera in selected] == ["near", "no-coords"]


def test_select_message_signs_ranks_nearest_first():
    """Message signs are ranked by distance from home."""
    signs = [
        _message_sign(
            "far",
            latitude=HOME_LAT + 2.0,
            longitude=HOME_LON,
        ),
        _message_sign("near", latitude=HOME_LAT, longitude=HOME_LON),
    ]
    selected = select_message_signs(hass_fake(), _entry(), signs)
    assert [sign.id for sign in selected] == ["near", "far"]


def test_select_message_signs_caps():
    """Only the nearest max_message_signs are kept."""
    signs = [_message_sign(f"sign-{index}") for index in range(5)]
    selected = select_message_signs(
        hass_fake(),
        _entry(_options({CONF_MAX_MESSAGE_SIGNS: 2})),
        signs,
    )
    assert len(selected) == 2


def test_select_travel_times_ranks_and_caps():
    """Travel times use their start coordinate to rank nearest first."""
    travel_times = [
        _travel_time(
            "far",
            start_latitude=HOME_LAT + 3.0,
            start_longitude=HOME_LON,
        ),
        _travel_time(
            "near",
            start_latitude=HOME_LAT,
            start_longitude=HOME_LON,
        ),
    ]
    selected = select_travel_times(
        hass_fake(),
        _entry(_options({CONF_MAX_TRAVEL_TIMES: 1})),
        travel_times,
    )
    assert [travel_time.id for travel_time in selected] == ["near"]


def test_select_road_conditions_sorts_alphabetically():
    """Road conditions are ordered by road name, independent of feed order."""
    conditions = [
        _road_condition("US 12/18"),
        _road_condition("I-39/90"),
        _road_condition("WIS 30"),
    ]
    selected = select_road_conditions(hass_fake(), _entry(), conditions)
    assert [condition.road for condition in selected] == [
        "I-39/90",
        "US 12/18",
        "WIS 30",
    ]


def test_select_road_conditions_caps():
    """Only the first max_road_conditions by name are kept."""
    conditions = [_road_condition(f"road-{index}") for index in range(5)]
    selected = select_road_conditions(
        hass_fake(),
        _entry(_options({CONF_MAX_ROAD_CONDITIONS: 2})),
        conditions,
    )
    assert len(selected) == 2


def test_select_road_conditions_dedupes_by_road():
    """Duplicate road names collapse to one entity, first reading wins."""
    conditions = [
        _road_condition("I-39", surface="Icy"),
        _road_condition("I-39", surface="Wet"),
        _road_condition("WIS 30"),
    ]
    selected = select_road_conditions(hass_fake(), _entry(), conditions)
    assert [condition.road for condition in selected] == ["I-39", "WIS 30"]
    assert selected[0].surface == "Icy"


def test_no_home_coordinates_keeps_all_within_cap():
    """Without home coordinates everything passes the radius and is kept."""
    incidents = [
        _incident("a", latitude=HOME_LAT, longitude=HOME_LON),
        _incident(
            "b",
            latitude=HOME_LAT + 10.0,
            longitude=HOME_LON,
        ),
    ]
    hass = hass_fake(home_latitude=None, home_longitude=None)
    selected = select_incidents(
        hass,
        _entry(_options({CONF_INCIDENT_RADIUS: 50})),
        incidents,
    )
    assert {incident.id for incident in selected} == {"a", "b"}


def _entry(options: dict | None = None) -> dict:
    """Return a fake ConfigEntry-like options holder."""
    entry = _FakeEntry()
    entry.options = dict(options or _options())
    return entry


def hass_fake(
    home_latitude: float | None = HOME_LAT,
    home_longitude: float | None = HOME_LON,
):
    """Return a fake hass with config coordinates."""
    return _FakeHass(home_latitude, home_longitude)


class _FakeEntry:
    """Minimal ConfigEntry stand-in exposing options."""

    def __init__(self) -> None:
        self.options: dict = {}


class _FakeHass:
    """Minimal HomeAssistant stand-in exposing config coordinates."""

    def __init__(self, latitude: float | None, longitude: float | None) -> None:
        self.config = _FakeConfig(latitude, longitude)


class _FakeConfig:
    """Minimal Config stand-in exposing coordinates."""

    def __init__(self, latitude: float | None, longitude: float | None) -> None:
        self.latitude = latitude
        self.longitude = longitude
