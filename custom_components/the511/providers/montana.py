"""Montana 511 provider.

Data source: https://mt.cdn.iteris-atis.com — the Iteris/ATG GeoJSON
CDN that feeds 511mt.net. Layers are open (no developer key needed):
``cameras`` (grouped per road site, stills under ``camera_images``) and
planned ``construction`` road work. The live incident layer is not
publicly served, so incidents surface as construction events only.
"""

from __future__ import annotations

from .iteris_atis import IterisAtisProvider


class MontanaProvider(IterisAtisProvider):
    """Provider for the Montana 511 system (511mt.net)."""

    provider_id = "montana"
    name = "Montana"
    region = "Montana"
    base_url = "https://mt.cdn.iteris-atis.com"

    supports_cameras = True
    supports_incidents = True

    cameras_nested = True

    incident_layers = ("construction",)
