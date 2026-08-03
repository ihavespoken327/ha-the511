"""Tests for The 511 geo_location platform."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.the511.const import CONF_PROVIDER, DOMAIN, NAME
from custom_components.the511.selection import haversine_km


async def _setup_entry(hass, fake_provider_class):
    """Set up a config entry for the fake provider and return it."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "fake"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


async def test_incident_marker_is_created(hass, fake_provider_class):
    """Setup should create a geo marker for each active incident."""
    await _setup_entry(hass, fake_provider_class)

    state = hass.states.get("geo_location.test_incident")
    assert state is not None
    assert state.name == "Test Incident"
    assert state.attributes["source"] == NAME
    assert state.attributes["latitude"] == 43.1
    assert state.attributes["longitude"] == -89.1
    assert state.attributes["unit_of_measurement"] == "km"
    assert float(state.state) > 0


async def test_cleared_incident_removes_marker(hass, fake_provider_class):
    """An incident that disappears should have its marker removed."""
    entry = await _setup_entry(hass, fake_provider_class)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    coordinator.data.incidents = []
    coordinator.async_update_listeners()
    await hass.async_block_till_done()

    assert hass.states.get("geo_location.test_incident") is None


def test_haversine_km():
    """The haversine helper should approximate the great-circle distance."""
    distance = haversine_km(52.3730, 4.8909, 52.3730, 4.8909)
    assert distance == 0.0

    distance = haversine_km(0.0, 0.0, 0.0, 90.0)
    assert 10000 < distance < 10100
