"""Arizona 511 provider.

Data source: https://az511.com/developers/doc — requires a developer API
key (query string ``key``), throttled to 10 calls per 60 seconds. The
platform serves cameras, events, and weather stations using the same
"GET" REST shape as Wisconsin; it does not publish road conditions or
travel times. Arizona weather stations carry no name or dewpoint field,
so those fall back to ``Unknown`` and null respectively.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class ArizonaProvider(TravelIQProvider):
    """Provider for the Arizona 511 system (az511.com)."""

    provider_id = "arizona"
    name = "Arizona"
    region = "Arizona"
    base_url = "https://az511.com"

    supports_cameras = True
    supports_incidents = True
    supports_weather = True
