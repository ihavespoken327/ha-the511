"""Nevada 511 provider.

Data source: https://www.nvroads.com/developers/doc — requires a developer
API key (query string ``key``), throttled to 10 calls per 60 seconds. The
platform serves cameras, events, road conditions (published under the
``roadconditions`` resource rather than ``winterroads``), and weather
stations using the same "GET" REST shape as Wisconsin; it does not
publish travel times.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class NevadaProvider(TravelIQProvider):
    """Provider for the Nevada 511 system (NVRoads)."""

    provider_id = "nevada"
    name = "Nevada"
    region = "Nevada"
    base_url = "https://www.nvroads.com"

    road_conditions_resource = "roadconditions"
    road_conditions_api_version = 3

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
    supports_weather = True
