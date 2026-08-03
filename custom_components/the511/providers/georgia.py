"""Georgia 511 provider.

Data source: https://511ga.org/developers/doc — requires a developer API
key (query string ``key``), throttled to 10 calls per 60 seconds. The
platform serves cameras and events using the same "GET" REST shape as
Wisconsin; it does not publish road conditions, weather stations, or
travel times.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class GeorgiaProvider(TravelIQProvider):
    """Provider for the Georgia 511 system (511GA)."""

    provider_id = "georgia"
    name = "Georgia"
    region = "Georgia"
    base_url = "https://511ga.org"

    supports_cameras = True
    supports_incidents = True
