"""Provider plugins for The 511.

Provider modules are imported here so their classes are registered in
the ``PROVIDERS`` mapping at import time.
"""

from .alaska import AlaskaProvider
from .arizona import ArizonaProvider
from .base import BaseProvider
from .connecticut import ConnecticutProvider
from .florida import FloridaProvider
from .georgia import GeorgiaProvider
from .idaho import IdahoProvider
from .louisiana import LouisianaProvider
from .nevada import NevadaProvider
from .new_york import NewYorkProvider
from .registry import (
    PROVIDERS,
    UnknownProviderError,
    get_provider_class,
    get_provider_classes,
    get_provider_ids,
)
from .utah import UtahProvider
from .wisconsin import WisconsinProvider

PROVIDERS[AlaskaProvider.provider_id] = AlaskaProvider
PROVIDERS[ArizonaProvider.provider_id] = ArizonaProvider
PROVIDERS[ConnecticutProvider.provider_id] = ConnecticutProvider
PROVIDERS[FloridaProvider.provider_id] = FloridaProvider
PROVIDERS[GeorgiaProvider.provider_id] = GeorgiaProvider
PROVIDERS[IdahoProvider.provider_id] = IdahoProvider
PROVIDERS[LouisianaProvider.provider_id] = LouisianaProvider
PROVIDERS[NevadaProvider.provider_id] = NevadaProvider
PROVIDERS[NewYorkProvider.provider_id] = NewYorkProvider
PROVIDERS[UtahProvider.provider_id] = UtahProvider
PROVIDERS[WisconsinProvider.provider_id] = WisconsinProvider

__all__ = [
    "PROVIDERS",
    "BaseProvider",
    "UnknownProviderError",
    "get_provider_class",
    "get_provider_classes",
    "get_provider_ids",
]
