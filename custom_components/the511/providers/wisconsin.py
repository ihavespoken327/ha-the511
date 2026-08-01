"""Wisconsin 511 provider.

Data source: https://511wi.gov/developers/doc — requires a developer API
key (query string ``key``), throttled to 10 calls per 60 seconds. The
coordinator polls once per ``SCAN_INTERVAL`` and fetches at most three
resources, which stays comfortably inside that budget.
"""

from __future__ import annotations

from typing import Any

from homeassistant.const import CONF_API_KEY

from ..models import CameraData, IncidentData, RoadConditionData, TravelTimeData
from .base import BaseProvider

CAMERAS_URL = "https://511wi.gov/api/v2/get/cameras"
EVENTS_URL = "https://511wi.gov/api/v2/get/event"
WINTER_ROADS_URL = "https://511wi.gov/api/v3/get/winterroads"
TRAVEL_TIMES_URL = "https://511wi.gov/api/v2/get/traveltimes"


class WisconsinProvider(BaseProvider):
    """Provider for the Wisconsin 511 system (511WI)."""

    provider_id = "wisconsin"
    name = "Wisconsin"
    region = "Wisconsin"

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
    supports_travel_times = True

    required_config_keys = (CONF_API_KEY,)
    secret_config_keys = (CONF_API_KEY,)

    @property
    def _api_key(self) -> str:
        """Return the configured developer API key."""
        return str(self.config[CONF_API_KEY])

    async def async_get_cameras(self) -> list[CameraData]:
        """Return normalized camera data."""
        cameras = await self._get_json(CAMERAS_URL)
        return [self._parse_camera(camera) for camera in cameras]

    async def async_get_incidents(self) -> list[IncidentData]:
        """Return normalized incident data."""
        events = await self._get_json(EVENTS_URL)
        return [self._parse_event(event) for event in events]

    async def async_get_road_conditions(self) -> list[RoadConditionData]:
        """Return normalized winter road condition data."""
        conditions = await self._get_json(WINTER_ROADS_URL)
        return [self._parse_road_condition(condition) for condition in conditions]

    async def async_get_travel_times(self) -> list[TravelTimeData]:
        """Return normalized travel time data."""
        travel_times = await self._get_json(TRAVEL_TIMES_URL)
        return [self._parse_travel_time(travel_time) for travel_time in travel_times]

    async def _get_json(self, url: str) -> Any:
        """Fetch ``url`` and return the decoded JSON payload."""
        async with self.session.get(
            url, params={"key": self._api_key, "format": "json"}
        ) as response:
            response.raise_for_status()
            return await response.json()

    def _parse_camera(self, camera: dict[str, Any]) -> CameraData:
        """Convert a 511WI camera resource into CameraData."""
        view = self._first_enabled_view(camera.get("Views"))
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
        """Convert a 511WI event resource into IncidentData."""
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
        """Convert a 511WI winter roads resource into RoadConditionData."""
        return RoadConditionData(
            road=condition.get("RoadwayName") or "Unknown",
            surface=condition.get("Overall Status"),
        )

    def _parse_travel_time(self, travel_time: dict[str, Any]) -> TravelTimeData:
        """Convert a 511WI travel time resource into TravelTimeData."""
        return TravelTimeData(
            id=str(travel_time.get("Id") or "Unknown"),
            name=travel_time.get("Description") or travel_time.get("Id") or "Unknown",
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

    @staticmethod
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


def _parse_float(value: Any) -> float | None:
    """Parse a JSON value as float, tolerating null and junk."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
