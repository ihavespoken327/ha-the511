"""Idaho 511 provider.

Data source: https://511.idaho.gov/developers/doc — requires a developer
API key (query string ``key``), throttled to 10 calls per 60 seconds. The
platform serves cameras, events, winter road conditions, and weather
stations using the same "GET" REST shape as Wisconsin; it does not
publish travel times.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class IdahoProvider(TravelIQProvider):
    """Provider for the Idaho 511 system (511.idaho.gov)."""

    provider_id = "idaho"
    name = "Idaho"
    region = "Idaho"
    base_url = "https://511.idaho.gov"

    road_conditions_api_version = 3

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
    supports_weather = True
