"""Provider plugins for The 511.

Provider modules are imported here so their classes are registered in
the ``PROVIDERS`` mapping at import time.
"""

from .base import BaseProvider
from .registry import (
    PROVIDERS,
    UnknownProviderError,
    get_provider_class,
    get_provider_classes,
    get_provider_ids,
)
from .wisconsin import WisconsinProvider

PROVIDERS[WisconsinProvider.provider_id] = WisconsinProvider

__all__ = [
    "PROVIDERS",
    "BaseProvider",
    "UnknownProviderError",
    "get_provider_class",
    "get_provider_classes",
    "get_provider_ids",
]
