"""Shared base for 511 providers on the Iteris/ATG GeoJSON platform.

A second family of state 511 systems (South Carolina, Montana, South
Dakota, and more) is hosted by Iteris/ATG and publishes its traffic
layers as open GeoJSON FeatureCollections on a per-state CDN::

    GET https://<host>/geojson/icons/metadata/icons.<layer>.geojson

Each layer carries a Point geometry plus layer-specific properties. The
layer set and schemas vary by state: South Carolina serves one feature
per camera while Montana and South Dakota group the cameras for a road
site into a ``cameras`` array on one feature. No developer key is
required for the layers these providers use, so subclasses keep the
default empty ``required_config_keys`` and the config flow skips the
credentials step.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ..models import CameraData, IncidentData
from .base import BaseProvider

_LAYER_PATH = "/geojson/icons/metadata/icons.{layer}.geojson"

_TAGS_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


class IterisAtisProvider(BaseProvider):
    """Base for state providers hosted on the Iteris/ATG GeoJSON platform."""

    #: Root of the state's GeoJSON CDN, e.g. ``https://sc.cdn.iteris-atis.com``.
    #: Required.
    base_url: str = ""

    #: Layers (in fetch order) whose features are live incidents. The
    #: ``construction`` layer feeds planned road work, tagged as such so
    #: the existing "hide roadwork" option keeps it off by default.
    incident_layers: tuple[str, ...] = ()

    #: ``cameras`` features group cameras per road site (a ``cameras``
    #: array per feature) instead of one feature per camera.
    cameras_nested: bool = False

    async def _get_layer(self, layer: str) -> list[dict[str, Any]]:
        """Fetch ``layer`` and return its features."""
        url = f"{self.base_url}{_LAYER_PATH.format(layer=layer)}"
        async with self.session.get(url) as response:
            response.raise_for_status()
            payload = await response.json()
        features = payload.get("features") if isinstance(payload, dict) else None
        return [feature for feature in features or [] if isinstance(feature, dict)]

    async def async_get_cameras(self) -> list[CameraData]:
        """Return normalized camera data."""
        cameras: list[CameraData] = []
        for feature in await self._get_layer("cameras"):
            if self.cameras_nested:
                cameras.extend(self._parse_camera_site(feature))
            else:
                cameras.append(self._parse_camera(feature))
        return cameras

    async def async_get_incidents(self) -> list[IncidentData]:
        """Return normalized incident data from every incident layer."""
        incidents: list[IncidentData] = []
        for layer in self.incident_layers:
            for feature in await self._get_layer(layer):
                incidents.append(self._parse_event(feature, layer))
        return incidents

    def _parse_camera(self, feature: dict[str, Any]) -> CameraData:
        """Convert a one-camera-per-feature layer into CameraData."""
        props = feature.get("properties") or {}
        latitude, longitude = _feature_point(feature)
        camera_id = str(props.get("id") or props.get("guid") or "Unknown")
        return CameraData(
            id=camera_id,
            name=props.get("description") or props.get("name") or "Unknown",
            image_url=props.get("image_url") or props.get("https_url"),
            road=props.get("route"),
            direction=props.get("direction"),
            latitude=latitude,
            longitude=longitude,
            video_url=props.get("https_url") or props.get("ios_url"),
            status=_active_status(props.get("active")),
        )

    def _parse_camera_site(self, feature: dict[str, Any]) -> list[CameraData]:
        """Flatten a road-site camera feature into one CameraData per camera."""
        props = feature.get("properties") or {}
        cameras = props.get("cameras")
        if not isinstance(cameras, list):
            return []
        latitude, longitude = _feature_point(feature)
        site_key = _site_key(props)
        road = props.get("route") or props.get("name") or None
        return [
            self._nested_camera(camera, site_key, index, latitude, longitude, road)
            for index, camera in enumerate(cameras)
            if isinstance(camera, dict)
        ]

    def _nested_camera(
        self,
        camera: dict[str, Any],
        site_key: str,
        index: int,
        latitude: float | None,
        longitude: float | None,
        road: str | None,
    ) -> CameraData:
        """Convert one member of a site's ``cameras`` array into CameraData."""
        camera_id = str(camera.get("id") or f"cam{index}")
        if camera_id.startswith(site_key):
            camera_id = camera_id[len(site_key) :].lstrip("-")
        camera_id = f"{site_key}-{camera_id}"
        return CameraData(
            id=camera_id,
            name=camera.get("name") or camera.get("description") or camera_id,
            image_url=camera.get("image"),
            road=road,
            direction=camera.get("direction"),
            latitude=latitude,
            longitude=longitude,
        )

    def _parse_event(self, feature: dict[str, Any], layer: str) -> IncidentData:
        """Convert an incident or construction feature into IncidentData."""
        props = feature.get("properties") or {}
        latitude, longitude = _feature_point(feature)
        return IncidentData(
            id=str(props.get("event_id") or feature.get("id") or "Unknown"),
            title=props.get("headline") or props.get("name") or "Unknown",
            description=(
                props.get("location_description")
                or _strip_html(props.get("report") or props.get("enhanced_report"))
            ),
            event_type="Roadwork" if layer == "construction" else props.get("headline"),
            latitude=latitude,
            longitude=longitude,
            road=props.get("route"),
        )


def _feature_point(
    feature: dict[str, Any],
) -> tuple[float | None, float | None]:
    """Return (latitude, longitude) from a GeoJSON Point feature."""
    geometry = feature.get("geometry") or {}
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, (list, tuple)) or len(coordinates) < 2:
        return None, None
    try:
        longitude = float(coordinates[0])
        latitude = float(coordinates[1])
    except (TypeError, ValueError):
        return None, None
    return latitude, longitude


def _site_key(props: Mapping[str, Any]) -> str:
    """Return a stable identifier for a road-site camera feature."""
    site_id = props.get("id")
    if site_id:
        return str(site_id)
    mrm = props.get("mrm")
    if mrm is not None and str(mrm).lower() != "unavailable":
        return f"{props.get('route') or 'Unknown'} {mrm}"
    return str(props.get("name") or "Unknown")


def _active_status(value: Any) -> str | None:
    """Map a boolean ``active`` flag onto the platform's status vocabulary."""
    if value is None:
        return None
    return "Enabled" if value else "Disabled"


def _strip_html(value: Any) -> str | None:
    """Return text with HTML tags and stray whitespace removed."""
    if value is None:
        return None
    text = _TAGS_RE.sub(" ", str(value))
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text or None
