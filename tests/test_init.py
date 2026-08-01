"""Tests for The 511 entry setup and unload."""

from __future__ import annotations

from homeassistant.const import CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.the511.const import DOMAIN, NAME


async def test_setup_and_unload_entry(hass):
    """Setting up an entry stores a coordinator; unloading removes it."""
    entry = MockConfigEntry(domain=DOMAIN, title=NAME, data={CONF_NAME: NAME})
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.entry_id not in hass.data[DOMAIN]
