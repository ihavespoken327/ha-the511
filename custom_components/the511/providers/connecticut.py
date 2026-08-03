"""Connecticut 511 provider.

Data source: http://ctroads.org/developers/doc — requires a developer API
key (query string ``key``), throttled to 10 calls per 60 seconds. Unlike
most states on this platform, Connecticut only publishes events; cameras,
road conditions, weather stations, and travel times are not available.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class ConnecticutProvider(TravelIQProvider):
    """Provider for the Connecticut travel information system (ctroads)."""

    provider_id = "connecticut"
    name = "Connecticut"
    region = "Connecticut"
    base_url = "https://ctroads.org"

    supports_incidents = True
