"""The 511 integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_PROVIDER, DOMAIN, PLATFORMS
from .coordinator import The511DataUpdateCoordinator
from .providers import BaseProvider, UnknownProviderError, get_provider_class

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up The 511 from a config entry."""
    provider = _create_provider(hass, entry)
    if provider is None:
        return False

    coordinator = The511DataUpdateCoordinator(hass, entry, provider)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    # Phase 4+: forward to platforms once entities exist.
    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


def _create_provider(hass: HomeAssistant, entry: ConfigEntry) -> BaseProvider | None:
    """Instantiate the provider configured in the entry, if it exists."""
    provider_id = entry.data.get(CONF_PROVIDER)
    if not isinstance(provider_id, str):
        _LOGGER.error("Config entry %s has no provider configured", entry.title)
        return None
    try:
        provider_class = get_provider_class(provider_id)
    except UnknownProviderError:
        _LOGGER.error(
            "Provider %r is not registered; refusing to set up %s",
            provider_id,
            entry.title,
        )
        return None
    return provider_class(async_get_clientsession(hass), entry.data)
