"""Wisconsin 511 provider.

Data source: https://511wi.gov/developers/doc — requires a developer API
key (query string ``key``), throttled to 10 calls per 60 seconds. The
coordinator polls once per ``SCAN_INTERVAL`` and fetches at most three
resources, which stays comfortably inside that budget.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class WisconsinProvider(TravelIQProvider):
    """Provider for the Wisconsin 511 system (511WI)."""

    provider_id = "wisconsin"
    name = "Wisconsin"
    region = "Wisconsin"
    base_url = "https://511wi.gov"

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
    supports_travel_times = True
