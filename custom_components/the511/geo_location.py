"""Geo location platform for The 511 incident map markers."""

from __future__ import annotations

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME
from .coordinator import The511DataUpdateCoordinator
from .models import IncidentData
from .selection import haversine_km, safe_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up The 511 incident map markers from the coordinator's data."""
    coordinator: The511DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: dict[str, The511IncidentGeolocation] = {}

    def update_markers() -> None:
        current_ids = {incident.id for incident in coordinator.incidents}
        for incident_id in set(entities) - current_ids:
            entity = entities.pop(incident_id)
            hass.async_create_task(entity.async_remove(force_remove=True))
        for incident in coordinator.incidents:
            if incident.id not in entities:
                entity = The511IncidentGeolocation(coordinator, incident)
                entities[incident.id] = entity
                async_add_entities([entity])

    update_markers()
    coordinator.async_add_listener(update_markers)


class The511IncidentGeolocation(
    CoordinatorEntity[The511DataUpdateCoordinator], GeolocationEvent
):
    """A map marker for an active traffic incident."""

    _attr_icon = "mdi:alert"
    _attr_should_poll = False
    _attr_source = NAME
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS

    def __init__(
        self, coordinator: The511DataUpdateCoordinator, incident: IncidentData
    ) -> None:
        """Initialize the incident map marker."""
        super().__init__(coordinator)
        self.incident_id = incident.id
        self._refresh(incident)

    async def async_added_to_hass(self) -> None:
        """Compute the distance to home once hass is available."""
        await super().async_added_to_hass()
        self._refresh(self._incident)

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

    def _refresh(self, incident: IncidentData | None) -> None:
        """Update the marker position from the freshest incident data."""
        self._attr_name = safe_name(incident.title if incident else None)
        self._attr_latitude = incident.latitude if incident else None
        self._attr_longitude = incident.longitude if incident else None
        self._attr_distance = self._distance_to_home(incident)

    def _distance_to_home(self, incident: IncidentData | None) -> float | None:
        """Return the straight-line distance from home in kilometers."""
        if (
            incident is None
            or incident.latitude is None
            or incident.longitude is None
            or self.hass is None
        ):
            return None
        home_latitude = self.hass.config.latitude
        home_longitude = self.hass.config.longitude
        if home_latitude is None or home_longitude is None:
            return None
        return haversine_km(
            home_latitude, home_longitude, incident.latitude, incident.longitude
        )

    def _handle_coordinator_update(self) -> None:
        """Refresh the marker when the coordinator publishes new data."""
        self._refresh(self._incident)
        self.async_write_ha_state()
