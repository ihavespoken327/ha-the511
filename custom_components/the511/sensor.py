"""Sensor platform for The 511 road conditions, weather, and travel times."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import The511DataUpdateCoordinator
from .entity import The511Entity
from .models import RoadConditionData, TravelTimeData, WeatherStationData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up The 511 sensors from the coordinator's data."""
    coordinator: The511DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    def add_new_sensors() -> None:
        entities: list[The511Entity] = []
        for condition in coordinator.data.road_conditions:
            key = f"road-{condition.road}"
            if key not in added:
                added.add(key)
                entities.append(The511RoadConditionSensor(coordinator, condition))
        for station in coordinator.data.weather_stations:
            key = f"station-{station.station_id}"
            if key not in added:
                added.add(key)
                entities.append(The511WeatherStationSensor(coordinator, station))
        for travel_time in coordinator.data.travel_times:
            key = f"travel-time-{travel_time.id}"
            if key not in added:
                added.add(key)
                entities.append(The511TravelTimeSensor(coordinator, travel_time))
        if entities:
            async_add_entities(entities)

    add_new_sensors()
    coordinator.async_add_listener(add_new_sensors)


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
        self._attr_name = condition.road
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
        self._attr_name = station.name or station.station_id
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
        self._attr_name = travel_time.name
        self._attr_icon = "mdi:map-clock"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES

    @property
    def _travel_time(self) -> TravelTimeData | None:
        """Return the freshest data for this route, if still present."""
        return next(
            (
                travel_time
                for travel_time in self.coordinator.data.travel_times
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
