"""Utah 511 provider.

Data source: https://www.udottraffic.utah.gov/developers/doc — requires a
developer API key (query string ``key``), throttled to 10 calls per 60
seconds. The platform serves cameras, events, road conditions (published
under the ``roadconditions`` resource with the surface status in
``RoadCondition``), and weather stations using the same "GET" REST shape
as Wisconsin; it does not publish travel times.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class UtahProvider(TravelIQProvider):
    """Provider for the Utah traffic system (UDOT Traffic)."""

    provider_id = "utah"
    name = "Utah"
    region = "Utah"
    base_url = "https://www.udottraffic.utah.gov"

    road_conditions_resource = "roadconditions"
    road_conditions_api_version = 2
    road_conditions_status_field = "RoadCondition"

    weather_dewpoint_fields = ("DewpointTemp", "Dewpoint", "DewpointTemperature")
    weather_wind_speed_fields = ("WindSpeedAvg", "WindSpeed", "Wind")

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
    supports_weather = True
