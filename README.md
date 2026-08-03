# The 511

A Home Assistant custom integration for traffic cameras, road conditions,
incidents, weather stations, travel times, and message signs from North
American 511 systems.

**Domain:** `the511` · **Display name:** The 511 · **Subtitle:** Traffic
Cameras & Road Conditions

> [!WARNING]
> Work in progress. Cameras, incidents, road conditions, weather stations,
> travel times, incident map markers, multi-provider support, and entity
> bounds are all implemented. Providers are available for Wisconsin,
> Louisiana, and Alaska; each requires the state's own free 511 developer
> API key.

## Entity bounds (options flow)

Live 511 feeds can carry thousands of cameras, travel-time segments, and
incidents. Creating an entity for each one floods the entity registry and the
map, so The 511 bounds what it surfaces through the integration's **Options**
dialog (Settings > Devices & Services > The 511 > Options):

| Option | Default | Effect |
|--------|---------|--------|
| Maximum cameras | 25 | Keeps the `N` cameras nearest to home |
| Maximum incidents | 25 | Keeps the `N` incidents nearest to home |
| Incident search radius | 50 mi | Drops incidents farther than this from home |
| Maximum travel time routes | 25 | Keeps the `N` routes nearest to home |
| Maximum road conditions | 25 | Keeps the first `N` road conditions by road name |
| Show planned roadwork | off | Planned construction events dominate the feed; hidden by default |

- Cameras, incidents, and travel times are ranked by straight-line distance
  from your HA home coordinates, nearest first.
- Road conditions carry no coordinates, so they are capped by road name
  (sorted) rather than by distance.
- Incidents without coordinates always surface (subject to the cap).
- Entity display names are capped at 100 characters so their `entity_id`s stay
  well inside HA's limit, even for long closure/detour titles.
- When an incident, route, or road condition leaves the selection it is
  removed from the entity registry, keeping the registry clean.

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
  are created. Many states run on the shared Arcadis/IBI "GET" platform;
  `TravelIQProvider` implements that API once and each state (Wisconsin,
  Louisiana, Alaska) is a thin subclass supplying its base URL and
  capabilities.
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
| 3 | Wisconsin provider | ✅ |
| 4 | Camera entities | ✅ |
| 5 | Incident entities | ✅ |
| 6 | Road condition sensors | ✅ |
| 7 | Weather stations | ✅ |
| 8 | Travel times | ✅ |
| 9 | Map support (`geo_location` incident markers) | ✅ |
| 10 | Multi-provider support | ✅ |
| 11 | Entity bounds + options flow | ✅ |
| 12 | Bound road condition sensors | ✅ |
| 13 | Multi-state providers (Travel-IQ base, Louisiana, Alaska) | ✅ |

## License

MIT
