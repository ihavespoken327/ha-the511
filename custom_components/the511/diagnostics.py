"""Diagnostics support for The 511."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Phase 2: redact provider credentials (api keys, tokens) from
    # entry.data and provider data before returning.
    return {
        "title": entry.title,
        "data": entry.data,
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update": coordinator.last_update,
            "data": coordinator.data,
        },
    }
