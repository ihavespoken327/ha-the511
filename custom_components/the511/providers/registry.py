"""Provider registry for The 511."""

from __future__ import annotations

from .base import BaseProvider


class UnknownProviderError(LookupError):
    """Raised when a provider id is not registered."""


#: All registered provider classes, keyed by ``provider_id``.
#: Populated once at import time by the provider modules listed in
#: ``providers/__init__.py``; must not be mutated at runtime.
PROVIDERS: dict[str, type[BaseProvider]] = {}


def get_provider_class(provider_id: str) -> type[BaseProvider]:
    """Return the provider class for ``provider_id``."""
    try:
        return PROVIDERS[provider_id]
    except KeyError as err:
        raise UnknownProviderError(
            f"Provider {provider_id!r} is not registered"
        ) from err


def get_provider_classes() -> tuple[type[BaseProvider], ...]:
    """Return the registered provider classes sorted by id."""
    return tuple(PROVIDERS[key] for key in sorted(PROVIDERS))


def get_provider_ids() -> tuple[str, ...]:
    """Return the ids of all registered providers, sorted."""
    return tuple(sorted(PROVIDERS))
