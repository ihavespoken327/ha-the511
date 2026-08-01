"""Tests for the provider framework."""

from __future__ import annotations

import pytest

from custom_components.the511.models import CameraData, ProviderData
from custom_components.the511.providers import (
    BaseProvider,
    UnknownProviderError,
    get_provider_class,
    get_provider_ids,
)


class CamerasOnlyProvider(BaseProvider):
    """A provider that only supports cameras."""

    provider_id = "cameras-only"
    name = "Cameras Only"
    region = "Test Region"
    supports_cameras = True

    async def async_get_cameras(self) -> list[CameraData]:
        return [
            CameraData(
                id="cam-1",
                name="Test Camera",
                image_url="https://example.com/cam-1.jpg",
            )
        ]


async def test_update_composes_supported_capabilities():
    """async_update should fetch only supported capabilities."""
    provider = CamerasOnlyProvider(session=None)

    data = await provider.async_update()

    assert isinstance(data, ProviderData)
    assert [cam.id for cam in data.cameras] == ["cam-1"]
    assert data.incidents == []
    assert data.road_conditions == []
    assert data.weather_stations == []


async def test_unsupported_capabilities_return_empty_list():
    """Default capability methods return empty lists."""
    provider = CamerasOnlyProvider(session=None)

    assert await provider.async_get_incidents() == []
    assert await provider.async_get_road_conditions() == []
    assert await provider.async_get_weather() == []


def test_unknown_provider_raises():
    """Looking up an unregistered provider should raise."""
    with pytest.raises(UnknownProviderError):
        get_provider_class("missing")


def test_provider_ids_are_sorted(fake_provider_class):
    """Registered provider ids are returned sorted."""
    assert "fake" in get_provider_ids()


def test_get_provider_class_returns_registered_class(fake_provider_class):
    """Lookup returns the class registered for the id."""
    assert get_provider_class("fake") is fake_provider_class
