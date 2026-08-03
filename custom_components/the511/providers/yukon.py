"""Yukon 511 provider.

Data source: https://511yukon.ca (also served via the vendor host
prod-yt.ibi511.com) — requires a developer API key (query string
``key``). Yukon publishes no API documentation, so the capability set is
limited to the resources that every Travel-IQ portal serves (cameras,
events); road conditions, weather, and travel times are left disabled
until a real key confirms them.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class YukonProvider(TravelIQProvider):
    """Provider for the Yukon 511 system (511yukon.ca)."""

    provider_id = "yukon"
    name = "Yukon"
    region = "Yukon"
    base_url = "https://511yukon.ca"

    supports_cameras = True
    supports_incidents = True
