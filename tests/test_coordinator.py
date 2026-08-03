"""Tests for The 511 coordinator."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.the511.const import CONF_PROVIDER, DOMAIN, NAME
from custom_components.the511.coordinator import The511DataUpdateCoordinator
from custom_components.the511.models import ProviderData


async def test_coordinator_refresh_pulls_provider_data(hass, fake_provider_class):
    """A refresh should populate coordinator.data from the provider."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "fake"},
    )
    provider = fake_provider_class(session=async_get_clientsession(hass), config={})
    coordinator = The511DataUpdateCoordinator(hass, entry, provider)

    await coordinator.async_refresh()

    assert coordinator.last_update_success
    assert isinstance(coordinator.data, ProviderData)
    assert [cam.id for cam in coordinator.data.cameras] == ["cam-1"]
    assert [incident.id for incident in coordinator.data.incidents] == ["inc-1"]
    assert [condition.road for condition in coordinator.data.road_conditions] == [
        "I-94"
    ]
    assert [station.station_id for station in coordinator.data.weather_stations] == [
        "ws-1"
    ]
    assert [travel_time.id for travel_time in coordinator.data.travel_times] == ["tt-1"]
    assert [sign.id for sign in coordinator.data.message_signs] == ["dms-1"]
    assert [sign.id for sign in coordinator.message_signs] == ["dms-1"]
