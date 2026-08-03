"""Tests for the Montana 511 provider."""

from __future__ import annotations

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.the511.providers import get_provider_class
from custom_components.the511.providers.montana import MontanaProvider


def _url(layer: str) -> str:
    """Build the expected CDN URL for a layer."""
    return f"{MontanaProvider.base_url}/geojson/icons/metadata/icons.{layer}.geojson"


def _provider(hass):
    """Build a provider bound to the mocked aiohttp session."""
    return MontanaProvider(session=async_get_clientsession(hass), config={})


def test_montana_provider_registered():
    """Montana should be registered under its provider_id."""
    assert get_provider_class("montana") is MontanaProvider


def test_montana_capabilities():
    """Montana supports cameras and construction incidents, keylessly."""
    provider = MontanaProvider(session=None, config={})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.cameras_nested
    assert MontanaProvider.incident_layers == ("construction",)
    assert not provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times
    assert MontanaProvider.required_config_keys == ()


async def test_update_fetches_cameras_and_construction(hass, aioclient_mock):
    """async_update should query the cameras and construction layers."""
    for layer in ("cameras", "construction"):
        aioclient_mock.get(_url(layer), json={"features": []})

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 2
