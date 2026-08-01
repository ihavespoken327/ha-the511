"""Tests for diagnostics support."""

from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.const import CONF_API_KEY, CONF_NAME
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.the511.const import CONF_PROVIDER, DOMAIN, NAME
from custom_components.the511.diagnostics import (
    _json_safe,
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_serializes_provider_data(hass, fake_provider_class):
    """Diagnostics should include JSON-safe coordinator data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={CONF_NAME: NAME, CONF_PROVIDER: "fake"},
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["title"] == NAME
    cameras = result["coordinator"]["data"]["cameras"]
    assert cameras == [
        {
            "id": "cam-1",
            "name": "Test Camera",
            "image_url": "https://example.com/cam-1.jpg",
            "road": "I-94",
            "direction": "East",
            "latitude": 43.0,
            "longitude": -89.0,
            "video_url": "https://example.com/cam-1.m3u8",
            "status": "Enabled",
            "last_updated": None,
        }
    ]


def test_json_safe_serializes_datetime():
    """_json_safe should render datetimes as ISO strings."""
    value = datetime(2026, 8, 1, 12, 0, 0, tzinfo=UTC)
    assert _json_safe(value) == "2026-08-01T12:00:00+00:00"


async def test_diagnostics_redacts_secret_config_keys(hass, secret_provider_class):
    """Secrets in entry.data should be redacted from diagnostics."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        data={
            CONF_NAME: NAME,
            CONF_PROVIDER: "secret",
            CONF_API_KEY: "super-secret-value",
        },
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["data"][CONF_API_KEY] == "[REDACTED]"
    assert result["data"][CONF_PROVIDER] == "secret"
    assert result["data"][CONF_NAME] == NAME
