"""Shared base for 511 providers on the Arcadis/IBI "GET" platform.

A large family of state 511 systems (Wisconsin, Louisiana, Alaska, New
York, Georgia, Utah and more) run on the same vendor platform and expose
the same REST shape::

    GET https://<host>/api/v{version}/get/<resource>?key=<key>&format=json

Each resource returns a JSON array of objects with shared field names for
cameras, events, travel times, and winter road conditions. Subclasses set
``base_url`` and the capability flags they support; resource names and
API major versions default to the platform-wide values and can be
overridden per state when a portal diverges.
"""

from __future__ import annotations

import re
from typing import Any

from homeassistant.const import CONF_API_KEY

from ..models import (
    CameraData,
    IncidentData,
    RoadConditionData,
    TravelTimeData,
    WeatherStationData,
)
from .base import BaseProvider

_NUMBER_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)")


class TravelIQProvider(BaseProvider):
    """Base for state providers hosted on the Arcadis/IBI "GET" platform."""

    #: Root of the state 511 portal, e.g. ``https://511wi.gov``. Required.
    base_url: str = ""

    #: API major version per resource family.
    cameras_api_version: int = 2
    events_api_version: int = 2
    travel_times_api_version: int = 2
    road_conditions_api_version: int = 3
    weather_api_version: int = 2

    #: Resource name per family (path segment under ``/api/v{version}/get/``).
    cameras_resource: str = "cameras"
    events_resource: str = "event"
    travel_times_resource: str = "traveltimes"
    road_conditions_resource: str = "winterroads"
    weather_resource: str = "weatherstations"

    #: JSON field carrying the road surface condition (state-dependent).
    road_conditions_status_field: str = "Overall Status"

    #: Report weather temperatures in Celsius instead of Fahrenheit.
    #: Canadian provinces report metric readings; the shared conversion
    #: only applies when this is False.
    weather_temperature_celsius: bool = False

    #: JSON field names for weather stations (state-dependent; the platform
    #: ships no consistent schema across states).
    weather_name_fields: tuple[str, ...] = ("Location", "StationName", "Name")
    weather_temperature_fields: tuple[str, ...] = ("AirTemperature",)
    weather_humidity_fields: tuple[str, ...] = ("RelativeHumidity",)
    weather_dewpoint_fields: tuple[str, ...] = (
        "Dewpoint",
        "DewpointTemperature",
        "DewpointTemp",
    )
    weather_wind_speed_fields: tuple[str, ...] = ("WindSpeed", "WindSpeedAvg", "Wind")
    weather_wind_direction_fields: tuple[str, ...] = ("Direction", "WindDirection")

    required_config_keys: tuple[str, ...] = (CONF_API_KEY,)
    secret_config_keys: tuple[str, ...] = (CONF_API_KEY,)

    @property
    def _api_key(self) -> str | None:
        """Return the configured developer API key, if any.

        Alberta and Ontario publish their feeds openly, so the key is
        optional for providers that do not list ``CONF_API_KEY`` in
        ``required_config_keys``.
        """
        key = self.config.get(CONF_API_KEY)
        return str(key) if key else None

    async def _get_json(self, resource: str, version: int = 2) -> Any:
        """Fetch ``resource`` and return the decoded JSON payload."""
        url = f"{self.base_url}/api/v{version}/get/{resource}"
        params: dict[str, str] = {"format": "json"}
        if self._api_key is not None:
            params["key"] = self._api_key
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def async_get_cameras(self) -> list[CameraData]:
        """Return normalized camera data."""
        cameras = await self._get_json(
            self.cameras_resource, version=self.cameras_api_version
        )
        return [self._parse_camera(camera) for camera in cameras]

    async def async_get_incidents(self) -> list[IncidentData]:
        """Return normalized incident data."""
        events = await self._get_json(
            self.events_resource, version=self.events_api_version
        )
        return [self._parse_event(event) for event in events]

    async def async_get_road_conditions(self) -> list[RoadConditionData]:
        """Return normalized road condition data."""
        conditions = await self._get_json(
            self.road_conditions_resource,
            version=self.road_conditions_api_version,
        )
        return [self._parse_road_condition(condition) for condition in conditions]

    async def async_get_weather(self) -> list[WeatherStationData]:
        """Return normalized weather station data."""
        stations = await self._get_json(
            self.weather_resource, version=self.weather_api_version
        )
        return [self._parse_weather_station(station) for station in stations]

    async def async_get_travel_times(self) -> list[TravelTimeData]:
        """Return normalized travel time data."""
        travel_times = await self._get_json(
            self.travel_times_resource, version=self.travel_times_api_version
        )
        return [self._parse_travel_time(travel_time) for travel_time in travel_times]

    def _parse_camera(self, camera: dict[str, Any]) -> CameraData:
        """Convert a GET camera resource into CameraData."""
        view = _first_enabled_view(camera.get("Views"))
        return CameraData(
            id=str(camera.get("Id") or "Unknown"),
            name=camera.get("Location") or camera.get("Id") or "Unknown",
            road=camera.get("Roadway"),
            direction=camera.get("Direction"),
            latitude=_parse_float(camera.get("Latitude")),
            longitude=_parse_float(camera.get("Longitude")),
            image_url=view.get("Url") if view else None,
            video_url=view.get("VideoUrl") if view else None,
            status=view.get("Status") if view else None,
        )

    def _parse_event(self, event: dict[str, Any]) -> IncidentData:
        """Convert a GET event resource into IncidentData."""
        return IncidentData(
            id=str(event.get("ID") or "Unknown"),
            title=event.get("Description") or "Unknown",
            description=event.get("Comment"),
            severity=event.get("Severity"),
            event_type=event.get("EventType"),
            latitude=_parse_float(event.get("Latitude")),
            longitude=_parse_float(event.get("Longitude")),
            road=event.get("RoadwayName"),
        )

    def _parse_road_condition(self, condition: dict[str, Any]) -> RoadConditionData:
        """Convert a GET winter roads resource into RoadConditionData."""
        return RoadConditionData(
            road=condition.get("RoadwayName") or "Unknown",
            surface=_normalize_surface(
                condition.get(self.road_conditions_status_field)
            ),
        )

    def _parse_weather_station(self, station: dict[str, Any]) -> WeatherStationData:
        """Convert a GET weather station resource into WeatherStationData.

        The platform reports readings as strings (``"19 °F"``,
        ``"100 %"``); temperatures are converted to Celsius to match the
        sensor platform's unit declaration unless the provider reports
        Celsius natively. Field names differ by state, so each reading
        looks up the state-appropriate aliases in order.
        """
        return WeatherStationData(
            station_id=str(station.get("Id") or "Unknown"),
            name=_first_present(station, *self.weather_name_fields),
            temperature=_parse_temperature(
                _first_present(station, *self.weather_temperature_fields),
                from_fahrenheit=not self.weather_temperature_celsius,
            ),
            humidity=_parse_percent(
                _first_present(station, *self.weather_humidity_fields)
            ),
            dewpoint=_parse_temperature(
                _first_present(station, *self.weather_dewpoint_fields),
                from_fahrenheit=not self.weather_temperature_celsius,
            ),
            wind=_format_wind(
                _first_present(station, *self.weather_wind_speed_fields),
                _first_present(station, *self.weather_wind_direction_fields),
            ),
            visibility=None,
        )

    def _parse_travel_time(self, travel_time: dict[str, Any]) -> TravelTimeData:
        """Convert a GET travel time resource into TravelTimeData."""
        return TravelTimeData(
            id=str(travel_time.get("Id") or "Unknown"),
            name=(travel_time.get("Description") or travel_time.get("Id") or "Unknown"),
            road=travel_time.get("RoadwayName"),
            minutes=_parse_float(travel_time.get("CurrentTime")),
            normal_minutes=_parse_float(travel_time.get("NormalTime")),
            delay=_parse_float(travel_time.get("Delay")),
            distance=_parse_float(travel_time.get("Distance")),
            region=travel_time.get("Region"),
            start_latitude=_parse_float(travel_time.get("StartLatitude")),
            start_longitude=_parse_float(travel_time.get("StartLongitude")),
            end_latitude=_parse_float(travel_time.get("EndLatitude")),
            end_longitude=_parse_float(travel_time.get("EndLongitude")),
        )


def _first_enabled_view(
    views: list[dict[str, Any]] | None,
) -> dict[str, Any] | None:
    """Return the first enabled camera view, falling back to the first."""
    if not views:
        return None
    for view in views:
        if view.get("Status") == "Enabled":
            return view
    return views[0]


def _first_present(mapping: dict[str, Any], *names: str) -> Any:
    """Return the first non-None value among ``names`` in ``mapping``."""
    for name in names:
        value = mapping.get(name)
        if value is not None:
            return value
    return None


def _parse_float(value: Any) -> float | None:
    """Parse a leading number from a JSON value, tolerating units and junk."""
    if value is None or isinstance(value, bool):
        return None
    match = _NUMBER_RE.match(str(value))
    if match is None:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _parse_temperature(value: Any, from_fahrenheit: bool = True) -> float | None:
    """Parse a Fahrenheit reading (e.g. ``"19 °F"``) into Celsius.

    When ``from_fahrenheit`` is False the reading is already Celsius and
    returned as-is (Canadian provinces report metric values).
    """
    parsed = _parse_float(value)
    if parsed is None:
        return None
    if not from_fahrenheit:
        return round(parsed, 1)
    return round((parsed - 32) * 5 / 9, 1)


def _parse_percent(value: Any) -> float | None:
    """Parse a percentage reading (e.g. ``"100 %"``) into a float."""
    return _parse_float(value)


def _normalize_surface(value: Any) -> str | None:
    """Coerce a road surface value (possibly a list) into a display string."""
    if value is None:
        return None
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    text = str(value).strip()
    return text or None


def _format_wind(speed: Any, direction: Any) -> str | None:
    """Combine wind speed and direction into a display string.

    Numeric directions are compass bearings (degrees) and are converted
    to a cardinal point; word directions (``"W"``, ``"NE"``) pass through.
    """
    parts = [part for part in (_normalize_wind_direction(direction), speed) if part]
    return " ".join(str(part).strip() for part in parts) or None


def _normalize_wind_direction(value: Any) -> str | None:
    """Convert a numeric compass bearing to a cardinal point."""
    if value is None:
        return None
    text = str(value).strip()
    if _NUMBER_RE.fullmatch(text):
        bearing = _parse_float(text)
        if bearing is not None:
            return _degrees_to_cardinal(bearing)
    return text or None


def _degrees_to_cardinal(degrees: float) -> str:
    """Convert a compass bearing to a 16-point cardinal direction."""
    points = (
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    )
    index = round((degrees % 360) / 22.5) % 16
    return points[index]
