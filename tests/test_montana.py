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
    """Montana supports cameras, construction incidents, and message signs."""
    provider = MontanaProvider(session=None, config={})

    assert provider.supports_cameras
    assert provider.supports_incidents
    assert provider.supports_message_signs
    assert provider.cameras_nested
    assert MontanaProvider.incident_layers == ("construction",)
    assert MontanaProvider.message_sign_layers == ("dms",)
    assert not provider.supports_road_conditions
    assert not provider.supports_weather
    assert not provider.supports_travel_times
    assert MontanaProvider.required_config_keys == ()


async def test_update_fetches_cameras_construction_and_signs(hass, aioclient_mock):
    """async_update should query the cameras, construction, and dms layers."""
    for layer in ("cameras", "construction", "dms"):
        aioclient_mock.get(_url(layer), json={"features": []})

    await _provider(hass).async_update()

    assert aioclient_mock.call_count == 3


async def test_message_signs_parse_live_text(hass, aioclient_mock):
    """The dms layer yields signs with their current text."""
    aioclient_mock.get(
        _url("dms"),
        json={
            "features": [
                {
                    "geometry": {"coordinates": [-111.1134433, 44.78238]},
                    "properties": {
                        "id": "dms_3",
                        "name": "Bozeman - 36-030",
                        "report": "EYES UP PHONE DOWN",
                        "route": "",
                    },
                }
            ]
        },
    )

    signs = await _provider(hass).async_get_message_signs()

    assert len(signs) == 1
    assert signs[0].id == "dms_3"
    assert signs[0].name == "Bozeman - 36-030"
    assert signs[0].message == "EYES UP PHONE DOWN"
