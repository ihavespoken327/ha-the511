"""Montana 511 provider.

Data source: https://mt.cdn.iteris-atis.com — the Iteris/ATG GeoJSON
CDN that feeds 511mt.net. Layers are open (no developer key needed):
``cameras`` (grouped per road site, stills under ``camera_images``),
planned ``construction`` road work, and ``dms`` dynamic message signs
whose ``report`` property carries the live sign text. The live incident
layer is not publicly served, so incidents surface as construction
events only.
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
    supports_message_signs = True

    cameras_nested = True

    incident_layers = ("construction",)

    message_sign_layers = ("dms",)
