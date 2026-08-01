"""Shared fixtures for The 511 tests."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations so hass can load the511."""
    return enable_custom_integrations
