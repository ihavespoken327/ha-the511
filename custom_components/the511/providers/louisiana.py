"""Louisiana 511 provider.

Data source: https://511la.org/developers/doc — requires a developer API
key (query string ``key``), throttled to 10 calls per 60 seconds. The
platform serves cameras, events, and travel times using the same "GET"
REST shape as Wisconsin.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class LouisianaProvider(TravelIQProvider):
    """Provider for the Louisiana 511 system (511LA)."""

    provider_id = "louisiana"
    name = "Louisiana"
    region = "Louisiana"
    base_url = "https://511la.org"

    supports_cameras = True
    supports_incidents = True
    supports_travel_times = True
