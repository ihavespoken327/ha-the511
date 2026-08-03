# AGENTS.md

Home Assistant custom integration **The 511** (`the511`) — traffic cameras,
road conditions, incidents, weather stations, travel times and message signs
from North American 511 systems.

## Working arrangement

- This repo/session is for **integration work** (code, tests, docs, releases):
  modifications, fixes, and additions to `custom_components/the511/`.
- **Dashboard/card work** is done in a separate chat: the dashboard YAML is
  built against the live HA instance and saved under `dashboard/` here, then
  screenshots are added to the README `## Screenshots` section.

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
  - `providers/` — provider plugin package (`base.py`, `registry.py`,
    `travel_iq.py` shared "GET"-platform base, `iteris_atis.py` shared
    Iteris/ATG GeoJSON base, one file per state provider)
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

Phases 1–19 done (bootstrap, provider framework, Wisconsin provider, camera,
incidents, road conditions, weather stations, travel times, map markers via
`geo_location`, multi-provider support with duplicate-provider guard,
Phase 11 entity bounds, Phase 12 road-condition bounds, Phase 13
multi-state providers, Phase 14 eleven state providers on the Travel-IQ
base, Phase 15 seven Canadian province providers on the same base,
Phase 16 North Carolina, Pennsylvania, and Yukon, Phase 17 South
Carolina, Montana, and South Dakota on a new Iteris/ATG GeoJSON base,
Phase 18 a road-condition dedupe fix, and Phase 19 dynamic message sign
sensors).

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
  cap (registry entry first, then entity). A startup sweep also scrubs
  registry entries an older install registered that are no longer in the
  selection (they would otherwise linger as `unavailable` restored
  entities after a cap is lowered).
- Options flow + `translations/en.json` expose the new field.

### Phase 13: multi-state providers

Many state 511 systems (WI, LA, AK, NY, GA, UT, FL and more) run on the
same Arcadis/IBI "GET" platform (`GET /api/v{version}/get/<resource>?key=`
with `format=json`), so one base class covers the whole family:

- `providers/travel_iq.py` — `TravelIQProvider(BaseProvider)`: `base_url`
  plus per-resource API versions and resource names as class attributes;
  shared `_get_json` and parsers for cameras, events, winter road
  conditions, weather stations, and travel times. Weather stations arrive
  as imperial strings (`"19 °F"`, `"100 %"`); temperatures are converted
  to Celsius to match the sensor platform's `UnitOfTemperature.CELSIUS`.
- `providers/wisconsin.py` — refactored onto `TravelIQProvider` (only a
  header now); `provider_id` stays `wisconsin` so existing entities and
  unique IDs are unchanged.
- `providers/louisiana.py` — cameras, incidents, travel times.
- `providers/alaska.py` — cameras, incidents, road conditions, weather
  stations (no travel times on the Alaska portal).
- `providers/__init__.py` registers all three; the config flow lists them
  automatically (no flow changes needed).

### Phase 14: eleven state providers

Eight more states run on the Arcadis/IBI "GET" platform and were added as
thin `TravelIQProvider` subclasses. State-specific quirks are handled by
new overridable class attributes on `travel_iq.py`, so existing providers
keep their defaults:

- `road_conditions_status_field` — JSON key carrying the surface status
  (default `"Overall Status"`); Utah reports it as `"RoadCondition"`.
- Weather field aliases (`weather_name_fields`, `weather_dewpoint_fields`,
  `weather_wind_speed_fields`, ...) — the platform ships no consistent
  weather schema across states. Nevada uses `StationName`/`Dewpoint`/`Wind`
  (covered by the default fallback order); Utah uses `DewpointTemp`/
  `WindSpeedAvg` (explicit override). Arizona weather has no name or
  dewpoint at all; parsing degrades gracefully.
- `road_conditions_resource` / `road_conditions_api_version` — Nevada and
  Utah publish road conditions as `roadconditions` (v3 / v2 respectively),
  not the `winterroads` v3 default; New York and Idaho keep `winterroads` v3.

New providers and capabilities:

- `providers/new_york.py` — cameras, incidents, road conditions (`winterroads` v3).
- `providers/georgia.py` — cameras, incidents.
- `providers/arizona.py` — cameras, incidents, weather (no name/dewpoint).
- `providers/connecticut.py` — incidents only (no camera feed on CT).
- `providers/florida.py` — cameras, incidents (verified via the platform
  `Invalid Key` response on the v2 endpoints; Florida publishes no API docs,
  so versions/resources use platform defaults until a real key confirms).
- `providers/idaho.py` — cameras, incidents, road conditions, weather.
- `providers/nevada.py` — cameras, incidents, road conditions (`roadconditions` v3), weather.
- `providers/utah.py` — cameras, incidents, road conditions (`roadconditions` v2, `RoadCondition` status), weather.

New England (newengland511.org, NE-Compass/C2C XML) and Nebraska
(511.nebraska.gov, federal CARS) are different platforms, not GET, and are
out of scope.

### Phase 15: Canadian province providers

Seven Canadian provinces were verified live (host probing + sample payloads)
and added as `TravelIQProvider` subclasses. Provincial quirks required two
new base capabilities:

- **Open (keyless) feeds** — Alberta (`511.alberta.ca`) and Ontario
  (`511on.ca`) publish openly. `BaseProvider.required_config_keys` defaults
  to `()`; `TravelIQProvider` declares `required_config_keys = (CONF_API_KEY,)`
  so subclasses must override back to `()`. `_api_key` returns `str | None`
  and `_get_json` omits the `key` parameter when the provider has none, so
  the config flow skips the credentials step for these two.
- **Metric weather** — `weather_temperature_celsius = True` on
  `TravelIQProvider` (default False) makes `_parse_weather_station` pass
  `from_fahrenheit=False`, so Alberta's plain-Celsius readings (e.g.
  `"14.4"`) are not converted; `_parse_temperature(value,
  from_fahrenheit=False)` returns the value unchanged.
- **List surfaces + bearing winds** — `_normalize_surface` joins list values
  (Ontario reports `Condition` as a list) and `_normalize_wind_direction`
  converts numeric compass bearings (Alberta's `WindDirection: "286"`) to
  16-point cardinals via `_degrees_to_cardinal`; `_format_wind` now uses both.

New providers and capabilities (all probed live this session):

- `providers/alberta.py` — cameras, incidents, road conditions (`winterroads`
  v3, `Primary Condition` status), weather (Celsius, `Speed` wind field).
  Open key. Verified live data (`511.alberta.ca`, canonical; `www` → 502).
- `providers/ontario.py` — cameras, incidents, road conditions
  (`roadconditions` v3, `Condition` status as a list). Open key. Verified
  live (`511on.ca`, canonical; `511.ontario.ca` DNS-fails).
- `providers/newfoundland_and_labrador.py` — cameras, incidents, road
  conditions (`Primary Condition`). Key-gated (`nl511.ca`).
- `providers/manitoba.py` / `providers/new_brunswick.py` — cameras,
  incidents, road conditions (`Primary Condition` / `Primary Conditions`).
  Key-gated; live only at `prod-{mb,nb}.ibi511.com` (public portals
  unreachable).
- `providers/saskatchewan.py` / `providers/nova_scotia.py` — cameras,
  incidents only (no public API docs and key-gated endpoints, so nothing
  beyond the platform defaults is enabled). Key-gated; live only at
  `prod-{sk,ns}.ibi511.com`.

AB and ON camera `Views[].Url` are `/map/Cctv/<id>` paths serving real JPEGs,
so no camera override was needed.

### Phase 16: North Carolina, Pennsylvania, Yukon

A sweep of `prod-{code}.ibi511.com` plus every unclaimed state/territory's
own 511 domain found three more key-gated GET-platform instances (all
confirmed via the `Invalid Key` signature on `key=test`):

- `providers/north_carolina.py` — `drivenc.gov`, cameras + incidents only.
- `providers/pennsylvania.py` — `511pa.com`, cameras + incidents only.
- `providers/yukon.py` — `511yukon.ca` (also served via
  `prod-yt.ibi511.com`), cameras + incidents only.

None publish API docs, so they follow the Saskatchewan/Nova Scotia
conservative pattern (platform-default cameras/event only). US states
running on other vendors (Iteris/ATG, Caltrans, ODOT, VDOT, WSDOT, etc.)
do not expose the GET signature. `newengland511.org` answers the GET API
with `Invalid Key` but is a multi-state consortium (ME/NH/VT/RI), not a
single provider, and remains out of scope.

### Phase 17: Iteris/ATG GeoJSON base + South Carolina, Montana, South Dakota

A second vendor platform was verified live. The Iteris/ATG SPAs that power
`sc511.org`, `sd511.org`, `511mt.net` (and, unreachable from this network,
`cotrip.org` / `wv511.org` / `511virginia.org`) publish their traffic layers
as open GeoJSON FeatureCollections on a per-state CDN:

- `providers/iteris_atis.py` — `IterisAtisProvider(BaseProvider)`: `base_url`
  plus `incident_layers` and `cameras_nested` class attributes. Layers live at
  `GET https://<host>/geojson/icons/metadata/icons.<layer>.geojson`; no
  developer key, so subclasses keep the default `required_config_keys = ()`
  and the config flow skips credentials. Each layer is a FeatureCollection of
  Point features; the `cameras` schema is either one feature per camera
  (`cameras_nested = False`, SC) or a road-site feature carrying a `cameras`
  array (`cameras_nested = True`, MT/SD). The `construction` layer feeds
  planned road work and is tagged `event_type="Roadwork"` so the existing
  "hide roadwork" option keeps it off by default. Helper-only units
  (`_feature_point`, `_site_key`, `_active_status`, `_strip_html`) live in the
  base and are covered by `tests/test_iteris_atis.py`.
- `providers/south_carolina.py` — `sc.cdn.iteris-atis.com`, cameras (767,
  stills on `scdotsnap`), live `incident` + `construction` events.
- `providers/montana.py` — `mt.cdn.iteris-atis.com`, cameras (grouped per road
  site), `construction` events only (the live incident layer is not publicly
  served).
- `providers/south_dakota.py` — `sd.cdn.iteris-atis.com`, cameras only (every
  other layer returns 403).

Verified live this session: SC 767 cameras / 5 events, MT 38 cameras / 78
construction events, SD 173 cameras; camera still URLs serve real JPEGs/PNGs.

Colorado, West Virginia, and Virginia run the same SPA but their data CDN is
unreachable from this network (`co.511ia.org` fails TLS; the `geojson/` paths
on the public portals are SPA catch-alls), so they remain out of scope pending
a follow-up. The Iteris `dms` layers carry real message-sign text (11 on SC,
73 on MT) but no message-sign entity platform exists yet; `supports_message_signs`
stays False until one is built.

### Phase 18: road-condition dedupe fix

Wisconsin (and any Travel-IQ provider whose winter-roads feed returns several
readings per `RoadwayName`) created one `The511RoadConditionSensor` per row.
Since the sensor's `unique_id` is `{provider_id}-road-{road}`, two rows for the
same road produced the same ID and HA aborted the duplicate at setup with
"Platform the511 does not generate unique IDs. ID … already exists - ignoring
…" (entity_platform.py). Fix: `select_road_conditions` collapses rows by road
name (first reading wins) before the sort-and-cap, matching the one-entity-per
road name platform contract. Added a dedupe test to `tests/test_selection.py`.

### Phase 19: dynamic message sign sensors

The Iteris `dms` layer carries live sign text, and `supports_message_signs`
was a documented but unimplemented flag. Phase 19 builds the platform on it —
**Montana only**, because probing showed MT's `dms` layer (75 features) is the
only one that serves text in a `report` property; SC's `dms` (10 features) is
VSL-only and stays disabled. Layered on the same nearest-to-home + cap +
mirror pattern as cameras/travel times:

- `models.py` — `MessageSignData` (id, name required; message, road,
  direction, latitude, longitude optional); `ProviderData.message_signs`.
- `providers/base.py` — default `async_get_message_signs` returns `[]`;
  `async_update` fetches signs only when `supports_message_signs`.
- `providers/iteris_atis.py` — `message_sign_layers = ()` /
  `message_sign_text_field = "report"` class attrs; `async_get_message_signs`
  loops the layers and `_parse_message_sign` reads the GeoJSON feature `id`
  (falling back to `id`/`event_id` props) and the `name`/`DMS_name`/
  `location_description` props, strips HTML from the text field, and takes
  `route`/`direction`/point.
- `providers/montana.py` — `supports_message_signs = True`,
  `message_sign_layers = ("dms",)`. (SC's docstring records why it stays off.)
- `selection.py`/`coordinator.py`/`config_flow.py` — `select_message_signs`
  (nearest-to-home via `_nearest`, capped by the new `CONF_MAX_MESSAGE_SIGNS`,
  default 25); coordinator `message_signs` property; options-flow row.
- `sensor.py` — `The511MessageSignSensor` (`unique_id`
  `{provider_id}-sign-{id}`, icon `mdi:sign-text`, `native_value` = current
  text, attributes road/direction/latitude/longitude) mirrors the coordinator
  set and sweeps stale registry entries at setup like travel times.
