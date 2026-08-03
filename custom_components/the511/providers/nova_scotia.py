"""Nova Scotia 511 provider.

Data source: hosted on the Arcadis/IBI platform (no public portal domain
resolves, so the vendor endpoint is used directly). Requires a developer
API key (query string ``key``). Nova Scotia publishes no API
documentation, so the capability set is limited to the resources that
every Travel-IQ portal serves (cameras, events); road conditions, weather,
and travel times are left disabled until a real key confirms them.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class NovaScotiaProvider(TravelIQProvider):
    """Provider for the Nova Scotia 511 system (Nova Scotia 511)."""

    provider_id = "nova_scotia"
    name = "Nova Scotia"
    region = "Nova Scotia"
    base_url = "https://prod-ns.ibi511.com"

    supports_cameras = True
    supports_incidents = True
