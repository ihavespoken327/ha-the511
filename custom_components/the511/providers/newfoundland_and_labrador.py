"""Newfoundland and Labrador 511 provider.

Data source: https://nl511.ca/developers/doc — requires a developer API
key (query string ``key``). Cameras, events, and winter road conditions
use the same "GET" REST shape as the other Travel-IQ provinces; weather
stations and travel times are not published.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class NewfoundlandLabradorProvider(TravelIQProvider):
    """Provider for the Newfoundland and Labrador 511 system (nl511.ca)."""

    provider_id = "newfoundland_and_labrador"
    name = "Newfoundland & Labrador"
    region = "Newfoundland and Labrador"
    base_url = "https://nl511.ca"

    road_conditions_status_field = "Primary Condition"

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
