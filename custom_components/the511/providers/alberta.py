"""Alberta 511 provider.

Data source: https://511.alberta.ca/developers/doc — Alberta publishes its
feed openly, so no developer API key is required (the ``key`` parameter is
omitted). Cameras, events, winter road conditions, and weather stations
use the same "GET" REST shape as the other Travel-IQ provinces; travel
times are not published. Weather temperatures arrive as bare Celsius
numbers (``"14.4"``) and wind direction as a compass bearing in degrees.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class AlbertaProvider(TravelIQProvider):
    """Provider for the Alberta 511 system (511.alberta.ca)."""

    provider_id = "alberta"
    name = "Alberta"
    region = "Alberta"
    base_url = "https://511.alberta.ca"

    required_config_keys = ()
    secret_config_keys = ()

    road_conditions_status_field = "Primary Condition"
    weather_temperature_celsius = True
    weather_wind_speed_fields = ("Speed",)

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
    supports_weather = True
