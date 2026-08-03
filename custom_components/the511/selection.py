"""Selection helpers that bound and rank the entities The 511 creates.

Live state-wide 511 feeds (Wisconsin in summer construction season) carry
thousands of cameras, travel-time segments, and incidents. Creating an
entity for each one floods the entity registry and the map. These helpers
turn a raw provider payload plus a config entry's options into the small,
home-relative lists the platforms actually surface: roadwork dropped,
radius bounded, nearest-first, capped.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from math import asin, cos, radians, sin, sqrt
from typing import TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_INCIDENT_RADIUS,
    CONF_MAX_CAMERAS,
    CONF_MAX_INCIDENTS,
    CONF_MAX_MESSAGE_SIGNS,
    CONF_MAX_ROAD_CONDITIONS,
    CONF_MAX_TRAVEL_TIMES,
    CONF_SHOW_ROADWORK,
    DEFAULT_INCIDENT_RADIUS,
    DEFAULT_MAX_CAMERAS,
    DEFAULT_MAX_INCIDENTS,
    DEFAULT_MAX_MESSAGE_SIGNS,
    DEFAULT_MAX_ROAD_CONDITIONS,
    DEFAULT_MAX_TRAVEL_TIMES,
    DEFAULT_SHOW_ROADWORK,
    KM_PER_MILE,
    MAX_ENTITY_NAME_LENGTH,
)
from .models import (
    CameraData,
    IncidentData,
    MessageSignData,
    RoadConditionData,
    TravelTimeData,
)

T = TypeVar("T")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance between two coordinates in kilometers."""
    earth_radius_km = 6371.0
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_lon / 2) ** 2
    )
    return earth_radius_km * 2 * asin(sqrt(a))


def safe_name(value: str | None, *, max_length: int = MAX_ENTITY_NAME_LENGTH) -> str:
    """Return a display-safe name capped so its entity_id stays in bounds."""
    name = (value or "").strip() or "Unknown"
    if len(name) <= max_length:
        return name
    return name[: max_length - 1].rstrip() + "…"


def is_roadwork(incident: IncidentData) -> bool:
    """Return True for planned construction events, which dominate the feed."""
    return "roadwork" in f"{incident.title} {incident.event_type}".lower()


def select_incidents(
    hass: HomeAssistant, entry: ConfigEntry, incidents: Sequence[IncidentData]
) -> list[IncidentData]:
    """Return incidents to surface: non-roadwork, in radius, nearest-first."""
    max_count = int(entry.options.get(CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS))
    radius_km = (
        float(entry.options.get(CONF_INCIDENT_RADIUS, DEFAULT_INCIDENT_RADIUS))
        * KM_PER_MILE
    )
    show_roadwork = bool(entry.options.get(CONF_SHOW_ROADWORK, DEFAULT_SHOW_ROADWORK))
    candidates = incidents if show_roadwork else _without_roadwork(incidents)
    return _nearest(
        hass,
        candidates,
        max_count,
        radius_km=radius_km,
        coordinates=lambda incident: (incident.latitude, incident.longitude),
    )


def select_cameras(
    hass: HomeAssistant, entry: ConfigEntry, cameras: Sequence[CameraData]
) -> list[CameraData]:
    """Return cameras to surface: the nearest ``max_cameras`` to home."""
    max_count = int(entry.options.get(CONF_MAX_CAMERAS, DEFAULT_MAX_CAMERAS))
    return _nearest(
        hass,
        cameras,
        max_count,
        coordinates=lambda camera: (camera.latitude, camera.longitude),
    )


def select_message_signs(
    hass: HomeAssistant, entry: ConfigEntry, signs: Sequence[MessageSignData]
) -> list[MessageSignData]:
    """Return message signs to surface: the nearest ``max_message_signs`` to home."""
    max_count = int(
        entry.options.get(CONF_MAX_MESSAGE_SIGNS, DEFAULT_MAX_MESSAGE_SIGNS)
    )
    return _nearest(
        hass,
        signs,
        max_count,
        coordinates=lambda sign: (sign.latitude, sign.longitude),
    )


def select_travel_times(
    hass: HomeAssistant, entry: ConfigEntry, travel_times: Sequence[TravelTimeData]
) -> list[TravelTimeData]:
    """Return travel times to surface: the nearest ``max_travel_times`` to home."""
    max_count = int(entry.options.get(CONF_MAX_TRAVEL_TIMES, DEFAULT_MAX_TRAVEL_TIMES))
    return _nearest(
        hass,
        travel_times,
        max_count,
        coordinates=lambda travel_time: (
            travel_time.start_latitude,
            travel_time.start_longitude,
        ),
    )


def select_road_conditions(
    hass: HomeAssistant, entry: ConfigEntry, conditions: Sequence[RoadConditionData]
) -> list[RoadConditionData]:
    """Return road conditions to surface: the first ``max_road_conditions`` by name.

    Road condition resources carry no coordinates, so there is nothing to rank
    by distance. Feeds can return several readings for one roadway, but the
    sensor platform keys one entity per road name, so duplicates are collapsed
    (first reading wins). The set is then sorted by road name to keep the cap
    deterministic across polls, and truncated.
    """
    max_count = int(
        entry.options.get(CONF_MAX_ROAD_CONDITIONS, DEFAULT_MAX_ROAD_CONDITIONS)
    )
    unique: dict[str, RoadConditionData] = {}
    for condition in conditions:
        unique.setdefault(condition.road, condition)
    return sorted(unique.values(), key=lambda condition: condition.road)[:max_count]


def _without_roadwork(
    incidents: Sequence[IncidentData],
) -> list[IncidentData]:
    """Return incidents that are not planned construction events."""
    return [incident for incident in incidents if not is_roadwork(incident)]


def _nearest[T](
    hass: HomeAssistant,
    items: Sequence[T],
    max_count: int,
    *,
    coordinates: Callable[[T], tuple[float | None, float | None]],
    radius_km: float | None = None,
) -> list[T]:
    """Return at most ``max_count`` items, nearest to home first.

    Items with coordinates are ranked by straight-line distance from home;
    items without coordinates sort after them. When ``radius_km`` is given,
    positioned items farther than that are dropped. Items without coordinates
    are never dropped by the radius (they cannot be measured) but still count
    toward the cap.
    """
    home = (hass.config.latitude, hass.config.longitude)
    positioned: list[tuple[float, T]] = []
    unknown: list[T] = []
    for item in items:
        latitude, longitude = coordinates(item)
        if latitude is None or longitude is None:
            unknown.append(item)
            continue
        if home[0] is None or home[1] is None:
            positioned.append((0.0, item))
            continue
        distance = haversine_km(home[0], home[1], latitude, longitude)
        if radius_km is not None and distance > radius_km:
            continue
        positioned.append((distance, item))
    positioned.sort(key=lambda pair: pair[0])
    ranked = [item for _, item in positioned] + unknown
    return ranked[:max_count]
