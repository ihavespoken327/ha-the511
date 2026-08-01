"""Tests for The 511 binary sensor platform."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.the511.const import CONF_PROVIDER, DOMAIN, NAME


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


async def test_incident_entity_is_created(hass, fake_provider_class):
    """Setup should create an on binary sensor for each active incident."""
    await _setup_entry(hass, fake_provider_class)

    state = hass.states.get("binary_sensor.the_511_test_incident")
    assert state is not None
    assert state.state == "on"
    assert state.name == "The 511 Test Incident"
    assert state.attributes["device_class"] == "problem"
    assert state.attributes["description"] == "Left lane blocked"
    assert state.attributes["severity"] == "Moderate"
    assert state.attributes["event_type"] == "Crash"
    assert state.attributes["road"] == "I-94"
    assert state.attributes["latitude"] == 43.1
    assert state.attributes["longitude"] == -89.1


async def test_incident_entity_has_stable_unique_id(hass, fake_provider_class):
    """The incident entity should expose a provider-scoped unique id."""
    await _setup_entry(hass, fake_provider_class)

    entity = async_get_entity_registry(hass).async_get(
        "binary_sensor.the_511_test_incident"
    )

    assert entity is not None
    assert entity.unique_id == "fake-incident-inc-1"


async def test_cleared_incident_turns_off(hass, fake_provider_class):
    """An incident that disappears should read off, not unavailable."""
    entry = await _setup_entry(hass, fake_provider_class)
    coordinator = hass.data[DOMAIN][entry.entry_id]

    coordinator.data.incidents = []
    coordinator.async_update_listeners()
    await hass.async_block_till_done()

    state = hass.states.get("binary_sensor.the_511_test_incident")
    assert state is not None
    assert state.state == "off"
