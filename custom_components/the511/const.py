"""Constants for The 511 integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "the511"
NAME = "The 511"
SUBTITLE = "Traffic Cameras & Road Conditions"

# Config entry data keys.
CONF_PROVIDER = "provider"

# Config entry option keys, tunable from the options flow. These bound how
# many entities The 511 creates and which incidents are worth surfacing;
# live Wisconsin feeds would otherwise register thousands of entities.
CONF_MAX_CAMERAS = "max_cameras"
CONF_MAX_INCIDENTS = "max_incidents"
CONF_INCIDENT_RADIUS = "incident_radius"  # miles
CONF_MAX_TRAVEL_TIMES = "max_travel_times"
CONF_MAX_ROAD_CONDITIONS = "max_road_conditions"
CONF_SHOW_ROADWORK = "show_roadwork"

DEFAULT_MAX_CAMERAS = 25
DEFAULT_MAX_INCIDENTS = 25
DEFAULT_INCIDENT_RADIUS = 50  # miles
DEFAULT_MAX_TRAVEL_TIMES = 25
DEFAULT_MAX_ROAD_CONDITIONS = 25
DEFAULT_SHOW_ROADWORK = False

# Cap entity display names so the entity_ids derived from them stay well
# inside HA's 255-character limit. Live incident titles (full closures with
# detour text) easily blow past it and hard-fail entity creation.
MAX_ENTITY_NAME_LENGTH = 100

KM_PER_MILE = 1.609344

# How often the coordinator polls the configured provider.
SCAN_INTERVAL = timedelta(minutes=5)

# Platforms the integration forwards. Grows as entity phases land.
PLATFORMS: list[Platform] = [
    Platform.CAMERA,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.GEO_LOCATION,
]
