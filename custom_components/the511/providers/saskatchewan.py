"""Saskatchewan 511 provider.

Data source: hosted on the Arcadis/IBI platform (no public portal domain
resolves, so the vendor endpoint is used directly). Requires a developer
API key (query string ``key``). Saskatchewan publishes no API
documentation, so the capability set is limited to the resources that
every Travel-IQ portal serves (cameras, events); road conditions, weather,
and travel times are left disabled until a real key confirms them.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class SaskatchewanProvider(TravelIQProvider):
    """Provider for the Saskatchewan 511 system (Saskatchewan 511)."""

    provider_id = "saskatchewan"
    name = "Saskatchewan"
    region = "Saskatchewan"
    base_url = "https://prod-sk.ibi511.com"

    supports_cameras = True
    supports_incidents = True
