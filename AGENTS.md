# AGENTS.md

Home Assistant custom integration **The 511** (`the511`) — traffic cameras,
road conditions, incidents, weather stations, travel times and message signs
from North American 511 systems.

## Project rules

- **Config entries only.** Never add YAML-based configuration.
- **Fully async.** aiohttp + asyncio, no blocking I/O, no global mutable state.
- **Coordinator owns the network.** `The511DataUpdateCoordinator` is the only
  object that talks to providers; entities only read `coordinator.data`.
- **Provider plugin architecture.** New states are new `BaseProvider`
  subclasses that advertise capabilities; never hardcode a single state.
- **Follow HA core patterns.** Prefer native HA architecture over custom
  inventions; design for extensibility before adding features.

## Repository layout

- `custom_components/the511/` — the integration
  - `providers/` — provider plugin package (`base.py`, `registry.py`, one
    file per state provider)
  - `models.py` — normalized dataclasses (`CameraData`, `IncidentData`, ...)
  - `entity.py` — shared entity base classes
  - `coordinator.py`, `config_flow.py`, `diagnostics.py`, `services.py`
- `tests/` — pytest suite (uses `pytest-homeassistant-custom-component`)

## Workflow

- Work in **small, pull-request-sized increments** (one phase per PR). Each
  increment must compile, pass lint, and be testable.
- Python version: **3.12+**. Formatting: **Black** (88 cols). Lint: **ruff**.
  Types: **mypy --strict**. Tests: **pytest**.
- Do not generate large amounts of code in one shot.

## Checks

```bash
ruff check .
ruff format --check .
black --check custom_components tests
mypy custom_components
pytest
```

## Phase status

Phase 1 (bootstrap) done. Next: **Phase 2 — provider framework**
(`providers/base.py`, `providers/registry.py`).
