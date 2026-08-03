"""Camera platform for The 511."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientTimeout
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN
from .coordinator import The511DataUpdateCoordinator
from .entity import The511Entity
from .models import CameraData
from .selection import safe_name

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up The 511 cameras from the coordinator's camera data.

    The created set mirrors ``coordinator.cameras``: a camera that leaves
    the filtered selection (falls out of the nearest-N cap) is removed.
    """
    coordinator: The511DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: dict[str, The511Camera] = {}
    entity_registry = async_get_entity_registry(hass)

    def add_new_cameras() -> None:
        current_ids = {camera.id for camera in coordinator.cameras}
        for camera_id in set(entities) - current_ids:
            entity = entities.pop(camera_id)
            unique_id = entity.unique_id
            if unique_id and (
                registered := entity_registry.async_get_entity_id(
                    Platform.CAMERA, DOMAIN, unique_id
                )
            ):
                entity_registry.async_remove(registered)
        new = [
            The511Camera(coordinator, camera)
            for camera in coordinator.cameras
            if camera.id not in entities
        ]
        if new:
            for entity in new:
                entities[entity.camera_id] = entity
            async_add_entities(new)

    add_new_cameras()
    coordinator.async_add_listener(add_new_cameras)


class The511Camera(The511Entity, Camera):
    """A traffic camera from a 511 provider."""

    def __init__(
        self, coordinator: The511DataUpdateCoordinator, camera: CameraData
    ) -> None:
        """Initialize the camera entity."""
        super().__init__(coordinator)
        Camera.__init__(self)
        self.camera_id = camera.id
        self._attr_unique_id = f"{coordinator.provider.provider_id}-{camera.id}"
        self._attr_name = safe_name(camera.name)
        self._attr_icon = "mdi:cctv"

    @property
    def _camera(self) -> CameraData | None:
        """Return the freshest data for this camera, if still present."""
        return next(
            (
                camera
                for camera in self.coordinator.cameras
                if camera.id == self.camera_id
            ),
            None,
        )

    @property
    def available(self) -> bool:
        """Return True if the coordinator succeeded and the camera exists."""
        return super().available and self._camera is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return camera metadata as state attributes."""
        camera = self._camera
        return {
            "road": camera.road if camera else None,
            "direction": camera.direction if camera else None,
            "latitude": camera.latitude if camera else None,
            "longitude": camera.longitude if camera else None,
            "status": camera.status if camera else None,
            "video_url": camera.video_url if camera else None,
        }

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Fetch the latest still image for this camera."""
        camera = self._camera
        if camera is None or camera.image_url is None:
            return None
        try:
            async with async_get_clientsession(self.hass).get(
                camera.image_url, timeout=ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.read()
        except (ClientError, TimeoutError) as err:
            _LOGGER.debug("Failed to fetch image for %s: %s", self.entity_id, err)
            return None
