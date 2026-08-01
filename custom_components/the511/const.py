"""Constants for The 511 integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "the511"
NAME = "The 511"
SUBTITLE = "Traffic Cameras & Road Conditions"

# How often the coordinator polls the configured provider.
SCAN_INTERVAL = timedelta(minutes=5)

# Platforms the integration forwards. Grows as entity phases land.
PLATFORMS: list[Platform] = []
