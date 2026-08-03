"""New York 511 provider.

Data source: https://511ny.org/developers/doc — requires a developer API
key (query string ``key``), throttled to 10 calls per 60 seconds. The
platform serves cameras, events, and winter road conditions using the same
"GET" REST shape as Wisconsin; it does not publish weather stations or
travel times.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class NewYorkProvider(TravelIQProvider):
    """Provider for the New York 511 system (511NY)."""

    provider_id = "new_york"
    name = "New York"
    region = "New York"
    base_url = "https://511ny.org"

    road_conditions_api_version = 3

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
