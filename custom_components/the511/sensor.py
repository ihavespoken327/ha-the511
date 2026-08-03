"""Sensor platform for The 511 road conditions, weather, and travel times."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN
from .coordinator import The511DataUpdateCoordinator
from .entity import The511Entity
from .models import RoadConditionData, TravelTimeData, WeatherStationData
from .selection import safe_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up The 511 sensors from the coordinator's data.

    Weather stations are a small, stable set and are added once. Road
    conditions and travel times mirror ``coordinator.road_conditions`` /
    ``coordinator.travel_times`` so an item that leaves its cap is removed.
    """
    coordinator: The511DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()
    road_entities: dict[str, The511RoadConditionSensor] = {}
    travel_entities: dict[str, The511TravelTimeSensor] = {}
    entity_registry = async_get_entity_registry(hass)

    def sweep_stale_sensors() -> None:
        """Remove registry entries no longer in the selection.

        Runs at setup so entities registered by an earlier install (before a
        cap was lowered) are scrubbed instead of lingering as unavailable
        restored entities. Only owns sensor entities for this config entry.
        """
        current = (
            {
                f"{coordinator.provider.provider_id}-road-{condition.road}"
                for condition in coordinator.road_conditions
            }
            | {
                f"{coordinator.provider.provider_id}-travel-time-{travel_time.id}"
                for travel_time in coordinator.travel_times
            }
            | {
                f"{coordinator.provider.provider_id}-station-{station.station_id}"
                for station in coordinator.data.weather_stations
            }
        )
        stale = [
            entity.entity_id
            for entity in entity_registry.entities.values()
            if (
                entity.platform == DOMAIN
                and entity.domain == Platform.SENSOR
                and entity.config_entry_id == entry.entry_id
                and entity.unique_id not in current
            )
        ]
        for entity_id in stale:
            entity_registry.async_remove(entity_id)

    def add_new_stations() -> None:
        entities: list[The511Entity] = []
        for station in coordinator.data.weather_stations:
            key = f"station-{station.station_id}"
            if key not in added:
                added.add(key)
                entities.append(The511WeatherStationSensor(coordinator, station))
        if entities:
            async_add_entities(entities)

    def update_road_conditions() -> None:
        current_keys = {condition.road for condition in coordinator.road_conditions}
        for road in set(road_entities) - current_keys:
            entity = road_entities.pop(road)
            unique_id = entity.unique_id
            if unique_id and (
                registered := entity_registry.async_get_entity_id(
                    Platform.SENSOR, DOMAIN, unique_id
                )
            ):
                entity_registry.async_remove(registered)
        new = [
            The511RoadConditionSensor(coordinator, condition)
            for condition in coordinator.road_conditions
            if condition.road not in road_entities
        ]
        if new:
            for entity in new:
                road_entities[entity.road] = entity
            async_add_entities(new)

    def update_travel_times() -> None:
        current_ids = {travel_time.id for travel_time in coordinator.travel_times}
        for travel_time_id in set(travel_entities) - current_ids:
            entity = travel_entities.pop(travel_time_id)
            unique_id = entity.unique_id
            if unique_id and (
                registered := entity_registry.async_get_entity_id(
                    Platform.SENSOR, DOMAIN, unique_id
                )
            ):
                entity_registry.async_remove(registered)
        new = [
            The511TravelTimeSensor(coordinator, travel_time)
            for travel_time in coordinator.travel_times
            if travel_time.id not in travel_entities
        ]
        if new:
            for entity in new:
                travel_entities[entity.travel_time_id] = entity
            async_add_entities(new)

    sweep_stale_sensors()
    add_new_stations()
    update_road_conditions()
    update_travel_times()
    coordinator.async_add_listener(add_new_stations)
    coordinator.async_add_listener(update_road_conditions)
    coordinator.async_add_listener(update_travel_times)


class The511RoadConditionSensor(The511Entity, SensorEntity):
    """Surface status for a road segment with readings as attributes."""

    def __init__(
        self, coordinator: The511DataUpdateCoordinator, condition: RoadConditionData
    ) -> None:
        """Initialize the road condition sensor."""
        super().__init__(coordinator)
        self.road = condition.road
        self._attr_unique_id = (
            f"{coordinator.provider.provider_id}-road-{condition.road}"
        )
        self._attr_name = safe_name(condition.road)
        self._attr_icon = "mdi:road-variant"

    @property
    def _condition(self) -> RoadConditionData | None:
        """Return the freshest data for this road, if still present."""
        return next(
            (
                condition
                for condition in self.coordinator.data.road_conditions
                if condition.road == self.road
            ),
            None,
        )

    @property
    def native_value(self) -> str | None:
        """Return the road surface status."""
        condition = self._condition
        return condition.surface if condition else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return road condition readings as state attributes."""
        condition = self._condition
        return {
            "surface": condition.surface if condition else None,
            "pavement_temperature": (
                condition.pavement_temperature if condition else None
            ),
            "air_temperature": condition.air_temperature if condition else None,
            "visibility": condition.visibility if condition else None,
            "wind_speed": condition.wind_speed if condition else None,
            "snow": condition.snow if condition else None,
            "ice": condition.ice if condition else None,
        }


class The511WeatherStationSensor(The511Entity, SensorEntity):
    """Temperature at a weather station with readings as attributes."""

    def __init__(
        self, coordinator: The511DataUpdateCoordinator, station: WeatherStationData
    ) -> None:
        """Initialize the weather station sensor."""
        super().__init__(coordinator)
        self.station_id = station.station_id
        self._attr_unique_id = (
            f"{coordinator.provider.provider_id}-station-{station.station_id}"
        )
        self._attr_name = safe_name(station.name or station.station_id)
        self._attr_icon = "mdi:weather-partly-cloudy"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def _station(self) -> WeatherStationData | None:
        """Return the freshest data for this station, if still present."""
        return next(
            (
                station
                for station in self.coordinator.data.weather_stations
                if station.station_id == self.station_id
            ),
            None,
        )

    @property
    def native_value(self) -> float | None:
        """Return the temperature reading."""
        station = self._station
        return station.temperature if station else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return station readings as state attributes."""
        station = self._station
        return {
            "humidity": station.humidity if station else None,
            "dewpoint": station.dewpoint if station else None,
            "wind": station.wind if station else None,
            "visibility": station.visibility if station else None,
        }


class The511TravelTimeSensor(The511Entity, SensorEntity):
    """Current travel time for a route segment with details as attributes."""

    def __init__(
        self, coordinator: The511DataUpdateCoordinator, travel_time: TravelTimeData
    ) -> None:
        """Initialize the travel time sensor."""
        super().__init__(coordinator)
        self.travel_time_id = travel_time.id
        self._attr_unique_id = (
            f"{coordinator.provider.provider_id}-travel-time-{travel_time.id}"
        )
        self._attr_name = safe_name(travel_time.name)
        self._attr_icon = "mdi:map-clock"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES

    @property
    def _travel_time(self) -> TravelTimeData | None:
        """Return the freshest data for this route, if still present."""
        return next(
            (
                travel_time
                for travel_time in self.coordinator.travel_times
                if travel_time.id == self.travel_time_id
            ),
            None,
        )

    @property
    def native_value(self) -> float | None:
        """Return the current travel time in minutes."""
        travel_time = self._travel_time
        return travel_time.minutes if travel_time else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return route details as state attributes."""
        travel_time = self._travel_time
        return {
            "road": travel_time.road if travel_time else None,
            "normal_minutes": travel_time.normal_minutes if travel_time else None,
            "delay": travel_time.delay if travel_time else None,
            "distance": travel_time.distance if travel_time else None,
            "region": travel_time.region if travel_time else None,
            "start_latitude": travel_time.start_latitude if travel_time else None,
            "start_longitude": travel_time.start_longitude if travel_time else None,
            "end_latitude": travel_time.end_latitude if travel_time else None,
            "end_longitude": travel_time.end_longitude if travel_time else None,
        }
