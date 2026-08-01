"""DataUpdateCoordinator for The 511 integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

# Phase 2 replaces this mapping with typed normalized models
# (CameraData, IncidentData, ...) produced by the active provider.
The511Data = dict[str, Any]


class The511DataUpdateCoordinator(DataUpdateCoordinator[The511Data]):
    """Coordinate updates across all The 511 entities for one config entry.

    This is the only object in the integration that communicates with
    providers. Entities read from ``coordinator.data`` and never perform
    network I/O themselves.
    """

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> The511Data:
        """Fetch fresh data from the configured provider.

        Phase 1: no providers are wired yet, so this returns an empty
        mapping. Phase 2 delegates to the provider owned by this
        coordinator.
        """
        return {}
