"""Base provider class for The 511."""

from __future__ import annotations

from aiohttp import ClientSession

from ..models import (
    CameraData,
    IncidentData,
    ProviderData,
    RoadConditionData,
    WeatherStationData,
)


class BaseProvider:
    """Base class for all The 511 providers.

    Subclasses declare their identity and capabilities as class
    attributes and implement the ``async_get_*`` methods for each
    supported capability. Unsupported capabilities return empty results
    so callers can treat every provider uniformly.
    """

    #: Unique slug used to look this provider up in the registry and in
    #: config entry data (must be overridden).
    provider_id: str = ""

    #: Human-readable name (must be overridden).
    name: str = ""

    #: Geographic region served (must be overridden).
    region: str = ""

    #: Capability flags — set to True for each implemented fetch method.
    supports_cameras: bool = False
    supports_incidents: bool = False
    supports_weather: bool = False
    supports_road_conditions: bool = False
    supports_travel_times: bool = False
    supports_message_signs: bool = False

    def __init__(self, session: ClientSession) -> None:
        """Initialize the provider with a shared aiohttp session."""
        self._session = session

    @property
    def session(self) -> ClientSession:
        """Return the shared aiohttp session."""
        return self._session

    async def async_update(self) -> ProviderData:
        """Fetch all supported data in a single update pass."""
        data = ProviderData()
        if self.supports_cameras:
            data.cameras = await self.async_get_cameras()
        if self.supports_incidents:
            data.incidents = await self.async_get_incidents()
        if self.supports_road_conditions:
            data.road_conditions = await self.async_get_road_conditions()
        if self.supports_weather:
            data.weather_stations = await self.async_get_weather()
        return data

    async def async_get_cameras(self) -> list[CameraData]:
        """Return camera data. Override when ``supports_cameras`` is True."""
        return []

    async def async_get_incidents(self) -> list[IncidentData]:
        """Return incidents. Override when ``supports_incidents`` is True."""
        return []

    async def async_get_road_conditions(self) -> list[RoadConditionData]:
        """Return road conditions. Override when ``supports_road_conditions``
        is True."""
        return []

    async def async_get_weather(self) -> list[WeatherStationData]:
        """Return weather station data. Override when ``supports_weather`` is True."""
        return []
