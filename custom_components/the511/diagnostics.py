"""Diagnostics support for The 511."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PROVIDER, DOMAIN
from .providers import UnknownProviderError, get_provider_class


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "title": entry.title,
        "data": _redact(entry.data, _secret_config_keys(entry)),
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "data": _json_safe(coordinator.data),
        },
    }


def _secret_config_keys(entry: ConfigEntry) -> set[str]:
    """Return the configured provider's secret config entry keys."""
    provider_id = entry.data.get(CONF_PROVIDER)
    if not isinstance(provider_id, str):
        return set()
    try:
        provider_class = get_provider_class(provider_id)
    except UnknownProviderError:
        return set()
    return set(provider_class.secret_config_keys)


def _redact(data: Mapping[str, Any], secret_keys: set[str]) -> dict[str, Any]:
    """Return a copy of ``data`` with values for secret keys replaced."""
    return {
        key: "[REDACTED]" if key in secret_keys else _json_safe(value)
        for key, value in data.items()
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
