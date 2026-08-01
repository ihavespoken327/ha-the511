"""Tests for normalized data models."""

from __future__ import annotations

from custom_components.the511.models import (
    CameraData,
    IncidentData,
    ProviderData,
    RoadConditionData,
    WeatherStationData,
)


def test_camera_data_requires_identity():
    """Camera identity fields are required; the rest default to None."""
    camera = CameraData(
        id="1",
        name="Cam",
        image_url="https://example.com/cam.jpg",
    )

    assert camera.road is None
    assert camera.direction is None
    assert camera.latitude is None
    assert camera.longitude is None
    assert camera.status is None
    assert camera.last_updated is None


def test_incident_data_defaults():
    """Incident optional fields default to None."""
    incident = IncidentData(id="1", title="Crash")

    assert incident.description is None
    assert incident.severity is None
    assert incident.event_type is None
    assert incident.road is None


def test_road_condition_data_defaults():
    """Road condition optional fields default to None."""
    condition = RoadConditionData(road="I-94")

    assert condition.surface is None
    assert condition.pavement_temperature is None
    assert condition.air_temperature is None
    assert condition.snow is None
    assert condition.ice is None


def test_weather_station_defaults():
    """Weather station optional fields default to None."""
    station = WeatherStationData(station_id="s1")

    assert station.temperature is None
    assert station.humidity is None
    assert station.dewpoint is None
    assert station.wind is None
    assert station.visibility is None


def test_provider_data_defaults_to_empty_lists():
    """ProviderData defaults every capability to an empty list."""
    data = ProviderData()

    assert data.cameras == []
    assert data.incidents == []
    assert data.road_conditions == []
    assert data.weather_stations == []
