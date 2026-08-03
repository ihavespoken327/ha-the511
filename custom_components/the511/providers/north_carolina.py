"""North Carolina 511 provider.

Data source: https://drivenc.gov — requires a developer API key (query
string ``key``). North Carolina publishes no API documentation, so the
capability set is limited to the resources that every Travel-IQ portal
serves (cameras, events); road conditions, weather, and travel times are
left disabled until a real key confirms them.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class NorthCarolinaProvider(TravelIQProvider):
    """Provider for the North Carolina 511 system (drivenc.gov)."""

    provider_id = "north_carolina"
    name = "North Carolina"
    region = "North Carolina"
    base_url = "https://drivenc.gov"

    supports_cameras = True
    supports_incidents = True
