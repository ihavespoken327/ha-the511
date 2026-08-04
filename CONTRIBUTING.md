# Contributing

Thanks for helping The 511 grow! The most common contribution is a new state
or province provider. This guide keeps new providers consistent and
reviewable.

## Adding a provider

Each provider is a thin `BaseProvider` subclass that advertises capabilities
and translates one native 511 API into the integration's normalized models
(`CameraData`, `IncidentData`, `RoadConditionData`, `WeatherStationData`,
`TravelTimeData`, `MessageSignData`).

Most North American 511 systems run on one of two shared vendor platforms, so
pick the base that matches:

1. **Arcadis/IBI "GET" platform** (`GET /api/v{version}/get/<resource>?key=`).
   Subclass `TravelIQProvider` in `custom_components/the511/providers/travel_iq.py`
   and only supply what differs: `provider_id`, `base_url`,
   `required_config_keys` (set back to `()` for open feeds), capability flags,
   and any per-resource API versions / resource names / field aliases.
   Good examples: `wisconsin.py`, `ontario.py` (open), `utah.py` (aliases).
2. **Iteris/ATG GeoJSON CDN** (open GeoJSON layers, no key). Subclass
   `IterisAtisProvider` in `providers/iteris_atis.py` and set `base_url`,
   `provider_id`, `incident_layers`, `cameras_nested`, and `message_sign_layers`.
   Good example: `montana.py`.

If the target 511 system runs a different platform entirely, you'll write a
new `BaseProvider` subclass. Probe the live feed first and only enable
capabilities you can actually verify — conservative beats speculative.

Register the provider in `providers/__init__.py` (the config flow lists
providers automatically; no flow changes needed).

### Capability contract

- Only set `supports_*` for feeds you verified live.
- Capability data must dedupe to one entity per stable id: cameras by camera
  id, incidents by event id, road conditions by road name (see
  `select_road_conditions`), message signs by sign id.
- Never hardcode a single state's quirks into `base.py`; add an overridable
  class attribute with a sensible default instead (see `travel_iq.py`).

## Development

```bash
uv venv
uv pip install -e ".[dev]"
```

Run every check locally before pushing — CI runs the same set:

```bash
ruff check .
ruff format --check .
black --check custom_components tests
mypy custom_components
pytest
```

- Python 3.14.2+, Black at 88 cols, ruff, mypy --strict.
- Tests use `pytest-homeassistant-custom-component`, so they run against a
  real Home Assistant harness. Mock HTTP with `aioclient_mock` (see
  `tests/test_wisconsin.py`); the fake provider in `tests/conftest.py` drives
  the platform tests.
- Add tests for any new parsing and for the provider's capabilities.
- No generated or bulk code: keep PRs small and reviewable, one provider (or
  one phase) per PR.

## Secrets

Never commit real API keys. Provider tests use mocks only; `secrets.yaml` is
not part of this repository. Open feeds need no key at all.
