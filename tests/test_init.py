"""Tests for The 511 entry setup and unload."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY, CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.the511.const import CONF_PROVIDER, DOMAIN, NAME


async def test_setup_and_unload_entry(hass, fake_provider_class):
    """Setting up an entry stores a coordinator; unloading removes it."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "fake"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.entry_id not in hass.data[DOMAIN]


async def test_setup_fails_for_unknown_provider(hass):
    """An entry referencing an unregistered provider should not load."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "does-not-exist"},
    )
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]


async def test_entries_are_isolated(hass, fake_provider_class, secret_provider_class):
    """Unloading one entry should leave the other provider's entities intact."""
    first = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "fake"},
    )
    first.add_to_hass(hass)
    assert await hass.config_entries.async_setup(first.entry_id)
    await hass.async_block_till_done()

    second = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "secret", CONF_API_KEY: "test-key"},
    )
    second.add_to_hass(hass)
    assert await hass.config_entries.async_setup(second.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("camera.the_511_test_camera") is not None
    assert len(hass.data[DOMAIN]) == 2

    assert await hass.config_entries.async_unload(second.entry_id)
    await hass.async_block_till_done()

    assert second.entry_id not in hass.data[DOMAIN]
    assert first.entry_id in hass.data[DOMAIN]
    assert hass.states.get("camera.the_511_test_camera") is not None
