"""Florida 511 provider.

Data source: https://fl511.com — requires a developer API key (query string
``key``), throttled to 10 calls per 60 seconds. The platform serves cameras
and events using the same "GET" REST shape as Wisconsin (confirmed by the
platform's ``Invalid Key`` response on the v2 endpoints). Florida publishes
no API documentation, so resource names and versions use platform defaults
and the capability set is limited to the verified endpoints.
"""

from __future__ import annotations

from .travel_iq import TravelIQProvider


class FloridaProvider(TravelIQProvider):
    """Provider for the Florida 511 system (FL511)."""

    provider_id = "florida"
    name = "Florida"
    region = "Florida"
    base_url = "https://fl511.com"

    supports_cameras = True
    supports_incidents = True
