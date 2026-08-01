# The 511

A Home Assistant custom integration for traffic cameras, road conditions,
incidents, weather stations, travel times, and message signs from North
American 511 systems.

**Domain:** `the511` · **Display name:** The 511 · **Subtitle:** Traffic
Cameras & Road Conditions

> [!WARNING]
> Work in progress. Current milestone: **Phase 1 — bootstrap**. The
> integration loads, can be configured from the UI, and unloads cleanly,
> but exposes no entities yet.

## Architecture

```
Config Flow
    ↓
Config Entry
    ↓
DataUpdateCoordinator     ← the only object that talks to providers
    ↓
Provider (plugin)         ← e.g. WisconsinProvider
    ↓
Normalized Data Models    ← CameraData, IncidentData, ...
    ↓
Home Assistant Entities   ← cameras, sensors, binary_sensors, images
```

- **Config entries only** — no YAML configuration.
- **Fully async** — aiohttp + asyncio, no blocking I/O.
- **Provider plugin architecture** — each provider inherits `BaseProvider`,
  advertises capabilities (`supports_cameras`, `supports_incidents`, ...) and
  translates its native API into standardized models. Only supported entities
  are created.
- **Entities never perform API calls** — they read from `coordinator.data`.

## Development

### Setup

```bash
uv venv
uv pip install -e ".[dev]"
```

### Checks

```bash
ruff check .
ruff format --check .
black --check custom_components tests
mypy custom_components
pytest
```

> `pytest` uses `pytest-homeassistant-custom-component`, so tests run against
> a real Home Assistant harness.

## Roadmap

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Bootstrap integration | ✅ |
| 2 | Provider framework | ✅ |
| 3 | Wisconsin provider | |
| 4 | Camera entities | |
| 5 | Incident entities | |
| 6 | Road condition sensors | |
| 7 | Weather stations | |
| 8 | Travel times | |
| 9 | Map support | |
| 10 | Multi-provider support | |

## License

MIT
