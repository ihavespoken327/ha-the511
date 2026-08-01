"""DataUpdateCoordinator for The 511 integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .models import ProviderData
from .providers import BaseProvider

_LOGGER = logging.getLogger(__name__)


class The511DataUpdateCoordinator(DataUpdateCoordinator[ProviderData]):
    """Coordinate updates across all The 511 entities for one config entry.

    This is the only object in the integration that communicates with
    providers. Entities read from ``coordinator.data`` and never perform
    network I/O themselves.
    """

    provider: BaseProvider
    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        provider: BaseProvider,
    ) -> None:
        """Initialize the coordinator with its provider."""
        self.provider = provider
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> ProviderData:
        """Fetch fresh data from the configured provider."""
        return await self.provider.async_update()
