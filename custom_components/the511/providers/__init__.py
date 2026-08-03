"""Provider plugins for The 511.

Provider modules are imported here so their classes are registered in
the ``PROVIDERS`` mapping at import time.
"""

from .alaska import AlaskaProvider
from .alberta import AlbertaProvider
from .arizona import ArizonaProvider
from .base import BaseProvider
from .connecticut import ConnecticutProvider
from .florida import FloridaProvider
from .georgia import GeorgiaProvider
from .idaho import IdahoProvider
from .louisiana import LouisianaProvider
from .manitoba import ManitobaProvider
from .nevada import NevadaProvider
from .new_brunswick import NewBrunswickProvider
from .new_york import NewYorkProvider
from .newfoundland_and_labrador import NewfoundlandLabradorProvider
from .nova_scotia import NovaScotiaProvider
from .ontario import OntarioProvider
from .registry import (
    PROVIDERS,
    UnknownProviderError,
    get_provider_class,
    get_provider_classes,
    get_provider_ids,
)
from .saskatchewan import SaskatchewanProvider
from .utah import UtahProvider
from .wisconsin import WisconsinProvider

PROVIDERS[AlaskaProvider.provider_id] = AlaskaProvider
PROVIDERS[AlbertaProvider.provider_id] = AlbertaProvider
PROVIDERS[ArizonaProvider.provider_id] = ArizonaProvider
PROVIDERS[ConnecticutProvider.provider_id] = ConnecticutProvider
PROVIDERS[FloridaProvider.provider_id] = FloridaProvider
PROVIDERS[GeorgiaProvider.provider_id] = GeorgiaProvider
PROVIDERS[IdahoProvider.provider_id] = IdahoProvider
PROVIDERS[LouisianaProvider.provider_id] = LouisianaProvider
PROVIDERS[ManitobaProvider.provider_id] = ManitobaProvider
PROVIDERS[NevadaProvider.provider_id] = NevadaProvider
PROVIDERS[NewBrunswickProvider.provider_id] = NewBrunswickProvider
PROVIDERS[NewYorkProvider.provider_id] = NewYorkProvider
PROVIDERS[NewfoundlandLabradorProvider.provider_id] = NewfoundlandLabradorProvider
PROVIDERS[NovaScotiaProvider.provider_id] = NovaScotiaProvider
PROVIDERS[OntarioProvider.provider_id] = OntarioProvider
PROVIDERS[SaskatchewanProvider.provider_id] = SaskatchewanProvider
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
