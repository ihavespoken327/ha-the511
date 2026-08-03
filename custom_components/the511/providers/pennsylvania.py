"""Pennsylvania 511 provider.

Data source: https://511pa.com — requires a developer API key (query
string ``key``). Pennsylvania publishes no API documentation, so the
capability set is limited to the resources that every Travel-IQ portal
serves (cameras, events); road conditions, weather, and travel times are
left disabled until a real key confirms them.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class PennsylvaniaProvider(TravelIQProvider):
    """Provider for the Pennsylvania 511 system (511pa.com)."""

    provider_id = "pennsylvania"
    name = "Pennsylvania"
    region = "Pennsylvania"
    base_url = "https://511pa.com"

    supports_cameras = True
    supports_incidents = True
