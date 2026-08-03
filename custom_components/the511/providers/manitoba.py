"""Manitoba 511 provider.

Data source: hosted on the Arcadis/IBI platform. The consumer portal is
https://www.manitoba511.ca (not ``mb511.ca``); its developer page
(``/developers/doc``) issues keys self-serve after a free account signup.
Requires a developer API key (query string ``key``). Cameras, events, and
winter road conditions use the same "GET" REST shape as the other
Travel-IQ provinces; weather stations and travel times are not published.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class ManitobaProvider(TravelIQProvider):
    """Provider for the Manitoba 511 system (Manitoba 511)."""

    provider_id = "manitoba"
    name = "Manitoba"
    region = "Manitoba"
    base_url = "https://prod-mb.ibi511.com"

    road_conditions_status_field = "Primary Condition"

    supports_cameras = True
    supports_incidents = True
    supports_road_conditions = True
