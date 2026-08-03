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

Phases 1–12 done (bootstrap, provider framework, Wisconsin provider, camera,
incidents, road conditions, weather stations, travel times, map markers via
`geo_location`, multi-provider support with duplicate-provider guard,
Phase 11 entity bounds, and Phase 12 road-condition bounds).

### Phase 11: entity bounds + options flow

Live Wisconsin feeds expose thousands of cameras, travel-time segments, and
incidents, and over-long incident titles (full closures with detour text)
previously hard-failed entity creation. Phase 11 bounds the entity surface:

- `selection.py` — `haversine_km`, `safe_name` (caps display names at 100
  chars so `entity_id`s stay in bounds), `is_roadwork`,
  `select_incidents`/`select_cameras`/`select_travel_times` (radius in miles,
  nearest-to-home first, cap; items without coordinates sort last and are
  never radius-dropped). `_nearest` is the generic ranker.
- `const.py` — option keys `CONF_MAX_CAMERAS`, `CONF_MAX_INCIDENTS`,
  `CONF_INCIDENT_RADIUS` (miles), `CONF_MAX_TRAVEL_TIMES`,
  `CONF_SHOW_ROADWORK`; defaults `25 / 25 / 50 / 25 / False`;
  `MAX_ENTITY_NAME_LENGTH = 100`; `KM_PER_MILE`.
- `coordinator.py` — `incidents` / `cameras` / `travel_times` properties run
  the selections against `self.config_entry` options. Platforms read these
  filtered views, never `coordinator.data.*` directly.
- Platforms (`binary_sensor.py`, `camera.py`, `sensor.py`, `geo_location.py`)
  mirror the filtered sets: a dynamic set keyed by id, listeners add new
  entities and remove dropped ones. For registry-backed entities the registry
  entry is removed first (verified: plain `async_remove(force_remove=True)`
  only marks them `unavailable`; removing the registry entry first scrubs it).
  Travel times mirror via a second listener; road conditions and weather
  stations are small stable sets and remain add-only.
- Options flow — `The511OptionsFlowHandler` (`async_step_init`) + update
  listener in `__init__.py` that calls
  `hass.config_entries.async_schedule_reload(entry.entry_id)` (the
  `async_reload_entry` API no longer exists in HA 2026.7).

Deployment notes: HACS does not track the version file; it snapshots the
latest `main` HEAD, so bump `manifest.json` `version` for clarity but HACS
reinstall is what actually updates the installed copy.

### Phase 12: road-condition bounds

Live Wisconsin winter-roads data exposed ~190 road conditions, one sensor
each, that Phase 11's caps did not reach (road conditions have no
coordinates, so `_nearest` could not rank them). Phase 12:

- `const.py` — `CONF_MAX_ROAD_CONDITIONS` / `DEFAULT_MAX_ROAD_CONDITIONS = 25`.
- `selection.py` — `select_road_conditions` sorts by road name and truncates
  to the cap (deterministic across polls since there is nothing to rank by
  distance).
- `coordinator.py` — `road_conditions` property runs the selection.
- `sensor.py` — road conditions now mirror the filtered set like travel
  times: a second listener adds new roads and removes ones that leave the
  cap (registry entry first, then entity).
- Options flow + `translations/en.json` expose the new field.
