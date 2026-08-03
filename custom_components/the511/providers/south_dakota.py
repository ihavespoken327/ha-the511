"""South Dakota 511 provider.

Data source: https://sd.cdn.iteris-atis.com — the Iteris/ATG GeoJSON
CDN that feeds sd511.org. Only the ``cameras`` layer is publicly served
(cameras grouped per road site, stills under ``camera_images``); the
incident, construction, and weather layers return 403, so incidents are
left disabled.
"""

from __future__ import annotations

from .iteris_atis import IterisAtisProvider


class SouthDakotaProvider(IterisAtisProvider):
    """Provider for the South Dakota 511 system (sd511.org)."""

    provider_id = "south_dakota"
    name = "South Dakota"
    region = "South Dakota"
    base_url = "https://sd.cdn.iteris-atis.com"

    supports_cameras = True

    cameras_nested = True
