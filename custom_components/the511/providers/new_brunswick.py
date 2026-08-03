"""New Brunswick 511 provider.

Data source: hosted on the Arcadis/IBI platform. The consumer portal is
https://511.gnb.ca (not ``nb511.ca``); its developer page
(``/developers/doc``) issues keys self-serve after a free account signup.
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
