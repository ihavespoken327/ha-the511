"""Normalized data models for The 511 providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class CameraData:
    """A traffic camera."""

    id: str
    name: str
    image_url: str | None = None
    road: str | None = None
    direction: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    video_url: str | None = None
    status: str | None = None
    last_updated: datetime | None = None


@dataclass(slots=True)
class IncidentData:
    """A traffic incident."""

    id: str
    title: str
    description: str | None = None
    severity: str | None = None
    event_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    road: str | None = None


@dataclass(slots=True)
class RoadConditionData:
    """Road condition readings for a road segment."""

    road: str
    surface: str | None = None
    pavement_temperature: float | None = None
    air_temperature: float | None = None
    visibility: float | None = None
    wind_speed: float | None = None
    snow: bool | None = None
    ice: bool | None = None


@dataclass(slots=True)
class WeatherStationData:
    """Readings from a weather station."""

    station_id: str
    temperature: float | None = None
    humidity: float | None = None
    dewpoint: float | None = None
    wind: str | None = None
    visibility: float | None = None


@dataclass(slots=True)
class ProviderData:
    """Normalized data a provider returns in one update pass."""

    cameras: list[CameraData] = field(default_factory=list)
    incidents: list[IncidentData] = field(default_factory=list)
    road_conditions: list[RoadConditionData] = field(default_factory=list)
    weather_stations: list[WeatherStationData] = field(default_factory=list)
