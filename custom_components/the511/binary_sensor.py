"""Binary sensor platform for The 511 incidents."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN
from .coordinator import The511DataUpdateCoordinator
from .entity import The511Entity
from .models import IncidentData
from .selection import safe_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up The 511 incidents from the coordinator's incident data.

    The created set mirrors ``coordinator.incidents``: when an incident
    leaves the filtered selection (clears, moves out of the radius, or gets
    crowded out of the cap) its entity is removed from the registry and the
    state machine.
    """
    coordinator: The511DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: dict[str, The511IncidentBinarySensor] = {}
    entity_registry = async_get_entity_registry(hass)

    def update_incidents() -> None:
        current_ids = {incident.id for incident in coordinator.incidents}
        for incident_id in set(entities) - current_ids:
            entity = entities.pop(incident_id)
            unique_id = entity.unique_id
            if unique_id and (
                registered := entity_registry.async_get_entity_id(
                    Platform.BINARY_SENSOR, DOMAIN, unique_id
                )
            ):
                entity_registry.async_remove(registered)
        new = [
            The511IncidentBinarySensor(coordinator, incident)
            for incident in coordinator.incidents
            if incident.id not in entities
        ]
        if new:
            for entity in new:
                entities[entity.incident_id] = entity
            async_add_entities(new)

    update_incidents()
    coordinator.async_add_listener(update_incidents)


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
        self._attr_name = safe_name(incident.title)
        self._attr_icon = "mdi:alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def _incident(self) -> IncidentData | None:
        """Return the freshest data for this incident, if still present."""
        return next(
            (
                incident
                for incident in self.coordinator.incidents
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
