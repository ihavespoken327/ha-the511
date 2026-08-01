"""Tests for The 511 sensor platform."""

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


async def test_road_condition_entity(hass, fake_provider_class):
    """Road conditions should surface surface status with readings as attrs."""
    await _setup_entry(hass, fake_provider_class)

    state = hass.states.get("sensor.the_511_i_94")
    assert state is not None
    assert state.state == "Clear Roads"
    assert state.attributes["surface"] == "Clear Roads"
    assert state.attributes["pavement_temperature"] == 2.0
    assert state.attributes["air_temperature"] == 1.0
    assert state.attributes["visibility"] == 10.0
    assert state.attributes["wind_speed"] == 15.0
    assert state.attributes["snow"] is False
    assert state.attributes["ice"] is True

    entity = async_get_entity_registry(hass).async_get("sensor.the_511_i_94")
    assert entity.unique_id == "fake-road-I-94"


async def test_weather_station_entity(hass, fake_provider_class):
    """Weather stations should surface temperature with station readings."""
    await _setup_entry(hass, fake_provider_class)

    state = hass.states.get("sensor.the_511_test_station")
    assert state is not None
    assert state.state == "1.0"
    assert state.attributes["unit_of_measurement"] == "°C"
    assert state.attributes["device_class"] == "temperature"
    assert state.attributes["humidity"] == 85.0
    assert state.attributes["dewpoint"] == -1.0
    assert state.attributes["wind"] == "W 15 km/h"
    assert state.attributes["visibility"] == 8.0

    entity = async_get_entity_registry(hass).async_get("sensor.the_511_test_station")
    assert entity.unique_id == "fake-station-ws-1"


async def test_travel_time_entity(hass, fake_provider_class):
    """Travel times should surface minutes with route details as attrs."""
    await _setup_entry(hass, fake_provider_class)

    entity_id = async_get_entity_registry(hass).async_get_entity_id(
        "sensor", DOMAIN, "fake-travel-time-tt-1"
    )
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == "12.0"
    assert state.attributes["unit_of_measurement"] == "min"
    assert state.attributes["device_class"] == "duration"
    assert state.attributes["road"] == "I-39/90"
    assert state.attributes["normal_minutes"] == 10.0
    assert state.attributes["delay"] == 2.0
    assert state.attributes["distance"] == 4.0
    assert state.attributes["region"] == "Dane"
