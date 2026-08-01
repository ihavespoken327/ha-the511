"""Binary sensor platform for The 511 incidents."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import The511DataUpdateCoordinator
from .entity import The511Entity
from .models import IncidentData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up The 511 incidents from the coordinator's incident data."""
    coordinator: The511DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    def add_new_incidents() -> None:
        entities = [
            The511IncidentBinarySensor(coordinator, incident)
            for incident in coordinator.data.incidents
            if incident.id not in added
        ]
        if entities:
            added.update(entity.incident_id for entity in entities)
            async_add_entities(entities)

    add_new_incidents()
    coordinator.async_add_listener(add_new_incidents)


class The511IncidentBinarySensor(The511Entity, BinarySensorEntity):
    """A traffic incident that is on while it is active."""

    def __init__(
        self, coordinator: The511DataUpdateCoordinator, incident: IncidentData
    ) -> None:
        """Initialize the incident entity."""
        super().__init__(coordinator)
        self.incident_id = incident.id
        self._attr_unique_id = (
            f"{coordinator.provider.provider_id}-incident-{incident.id}"
        )
        self._attr_name = incident.title
        self._attr_icon = "mdi:alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def _incident(self) -> IncidentData | None:
        """Return the freshest data for this incident, if still present."""
        return next(
            (
                incident
                for incident in self.coordinator.data.incidents
                if incident.id == self.incident_id
            ),
            None,
        )

    @property
    def is_on(self) -> bool:
        """Return True while the incident is active."""
        return self._incident is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return incident details as state attributes."""
        incident = self._incident
        return {
            "description": incident.description if incident else None,
            "severity": incident.severity if incident else None,
            "event_type": incident.event_type if incident else None,
            "road": incident.road if incident else None,
            "latitude": incident.latitude if incident else None,
            "longitude": incident.longitude if incident else None,
        }
