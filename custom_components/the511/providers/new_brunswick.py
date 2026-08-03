"""New Brunswick 511 provider.

Data source: hosted on the Arcadis/IBI platform (the public nb511.ca portal
does not currently resolve, so the vendor endpoint is used directly).
Requires a developer API key (query string ``key``). Cameras, events, and
winter road conditions use the same "GET" REST shape as the other
Travel-IQ provinces; the winter-roads documentation sample reports the
surface status under ``Primary Conditions`` (plural). Weather stations and
travel times are not published.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class NewBrunswickProvider(TravelIQProvider):
    """Provider for the New Brunswick 511 system (New Brunswick 511)."""

    provider_id = "new_brunswick"
    name = "New Brunswick"
    region = "New Brunswick"
    base_url = "https://prod-nb.ibi511.com"

    road_conditions_status_field = "Primary Conditions"

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
