"""Shared entity base for The 511 entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .coordinator import The511DataUpdateCoordinator


class The511Entity(CoordinatorEntity[The511DataUpdateCoordinator]):
    """Base entity attached to the device for one provider config entry."""

    def __init__(self, coordinator: The511DataUpdateCoordinator) -> None:
        """Initialize the entity with device info for the provider entry."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer=NAME,
            model=coordinator.provider.name,
        )
