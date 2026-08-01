"""Shared fixtures for The 511 tests."""

from __future__ import annotations

import pytest
from homeassistant.const import CONF_API_KEY

from custom_components.the511.models import (
    CameraData,
    IncidentData,
    RoadConditionData,
    TravelTimeData,
    WeatherStationData,
)
from custom_components.the511.providers import PROVIDERS, BaseProvider


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations so hass can load the511."""
    return enable_custom_integrations


@pytest.fixture
def fake_provider_class():
    """Register a fake provider in the registry, unregistering afterwards."""

    class FakeProvider(BaseProvider):
        provider_id = "fake"
        name = "Fake 511"
        region = "Fake Region"
        supports_cameras = True
        supports_incidents = True
        supports_road_conditions = True
        supports_weather = True
        supports_travel_times = True

        async def async_get_cameras(self) -> list[CameraData]:
            return [
                CameraData(
                    id="cam-1",
                    name="Test Camera",
                    image_url="https://example.com/cam-1.jpg",
                    road="I-94",
                    direction="East",
                    latitude=43.0,
                    longitude=-89.0,
                    video_url="https://example.com/cam-1.m3u8",
                    status="Enabled",
                )
            ]

        async def async_get_incidents(self) -> list[IncidentData]:
            return [
                IncidentData(
                    id="inc-1",
                    title="Test Incident",
                    description="Left lane blocked",
                    severity="Moderate",
                    event_type="Crash",
                    latitude=43.1,
                    longitude=-89.1,
                    road="I-94",
                )
            ]

        async def async_get_road_conditions(self) -> list[RoadConditionData]:
            return [
                RoadConditionData(
                    road="I-94",
                    surface="Clear Roads",
                    pavement_temperature=2.0,
                    air_temperature=1.0,
                    visibility=10.0,
                    wind_speed=15.0,
                    snow=False,
                    ice=True,
                )
            ]

        async def async_get_weather(self) -> list[WeatherStationData]:
            return [
                WeatherStationData(
                    station_id="ws-1",
                    name="Test Station",
                    temperature=1.0,
                    humidity=85.0,
                    dewpoint=-1.0,
                    wind="W 15 km/h",
                    visibility=8.0,
                )
            ]

        async def async_get_travel_times(self) -> list[TravelTimeData]:
            return [
                TravelTimeData(
                    id="tt-1",
                    name="I-39/90 NB US 12/18 to Badger Interchange",
                    road="I-39/90",
                    minutes=12.0,
                    normal_minutes=10.0,
                    delay=2.0,
                    distance=4.0,
                    region="Dane",
                )
            ]

    PROVIDERS[FakeProvider.provider_id] = FakeProvider
    yield FakeProvider
    PROVIDERS.pop(FakeProvider.provider_id, None)


@pytest.fixture
def secret_provider_class():
    """Register a provider that requires an api key, unregistering afterwards."""

    class SecretProvider(BaseProvider):
        provider_id = "secret"
        name = "Secret 511"
        region = "Secret Region"
        supports_cameras = True

        required_config_keys = (CONF_API_KEY,)
        secret_config_keys = (CONF_API_KEY,)

        async def async_get_cameras(self) -> list[CameraData]:
            return []

    PROVIDERS[SecretProvider.provider_id] = SecretProvider
    yield SecretProvider
    PROVIDERS.pop(SecretProvider.provider_id, None)
