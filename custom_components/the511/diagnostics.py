"""Diagnostics support for The 511."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Phase 3+: redact provider credentials (api keys, tokens) from
    # entry.data and provider data before returning.
    return {
        "title": entry.title,
        "data": entry.data,
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "data": _json_safe(coordinator.data),
        },
    }


def _json_safe(value: Any) -> Any:
    """Recursively convert dataclasses and datetimes to JSON-safe values."""
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe(asdict(value))
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    return value
