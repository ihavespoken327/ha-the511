"""South Carolina 511 provider.

Data source: https://sc.cdn.iteris-atis.com — the Iteris/ATG GeoJSON
CDN that feeds sc511.org. Layers are open (no developer key needed):
``cameras`` (one feature per camera, stills on scdotsnap), live
``incident`` events, and planned ``construction`` road work.
"""

from __future__ import annotations

from .iteris_atis import IterisAtisProvider


class SouthCarolinaProvider(IterisAtisProvider):
    """Provider for the South Carolina 511 system (sc511.org)."""

    provider_id = "south_carolina"
    name = "South Carolina"
    region = "South Carolina"
    base_url = "https://sc.cdn.iteris-atis.com"

    supports_cameras = True
    supports_incidents = True

    incident_layers = ("incident", "construction")
