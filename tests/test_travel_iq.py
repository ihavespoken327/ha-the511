"""Tests for the shared Travel-IQ provider base."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY

from custom_components.the511.providers.travel_iq import (
    _degrees_to_cardinal,
    _first_enabled_view,
    _first_present,
    _format_wind,
    _normalize_surface,
    _normalize_wind_direction,
    _parse_float,
    _parse_percent,
    _parse_temperature,
)


def test_parse_float_handles_units_and_junk():
    """Leading numbers are parsed; nulls and junk become None."""
    assert _parse_float("2 mph") == 2.0
    assert _parse_float(" 19.5 °F") == 19.5
    assert _parse_float(-5) == -5.0
    assert _parse_float(None) is None
    assert _parse_float("n/a") is None
    assert _parse_float(True) is None


def test_parse_temperature_converts_fahrenheit_to_celsius():
    """Fahrenheit readings are converted to Celsius for the sensor unit."""
    assert _parse_temperature("32 °F") == 0.0
    assert _parse_temperature("19 °F") == -7.2
    assert _parse_temperature("-5 °F") == -20.6
    assert _parse_temperature(None) is None


def test_parse_temperature_passes_celsius_through():
    """Metric providers report Celsius already; no conversion applies."""
    assert _parse_temperature("14.4", from_fahrenheit=False) == 14.4
    assert _parse_temperature("-3", from_fahrenheit=False) == -3.0
    assert _parse_temperature(None, from_fahrenheit=False) is None


def test_normalize_surface_joins_lists():
    """Road surface values may be a single string or a list of strings."""
    assert _normalize_surface("Bare Dry") == "Bare Dry"
    assert _normalize_surface(["No Report"]) == "No Report"
    assert _normalize_surface(["Bare Dry", "Loose Snow"]) == "Bare Dry, Loose Snow"
    assert _normalize_surface(None) is None
    assert _normalize_surface([]) is None
    assert _normalize_surface("") is None


def test_normalize_wind_direction_converts_bearings():
    """Numeric compass bearings become cardinal points; words pass through."""
    assert _normalize_wind_direction("W") == "W"
    assert _normalize_wind_direction("NE") == "NE"
    assert _normalize_wind_direction("286") == "WNW"
    assert _normalize_wind_direction(90) == "E"
    assert _normalize_wind_direction(None) is None


def test_degrees_to_cardinal_maps_16_points():
    """Compass bearings map onto the 16-point compass rose."""
    assert _degrees_to_cardinal(0) == "N"
    assert _degrees_to_cardinal(90) == "E"
    assert _degrees_to_cardinal(180) == "S"
    assert _degrees_to_cardinal(270) == "W"
    assert _degrees_to_cardinal(360) == "N"
    assert _degrees_to_cardinal(286) == "WNW"
    assert _degrees_to_cardinal(22.5) == "NNE"


def test_parse_percent():
    """Percentage strings are parsed as floats."""
    assert _parse_percent("100 %") == 100.0
    assert _parse_percent(None) is None


def test_format_wind_combines_direction_and_speed():
    """Wind direction and speed join into a display string."""
    assert _format_wind("2 mph", "W") == "W 2 mph"
    assert _format_wind("2 mph", None) == "2 mph"
    assert _format_wind(None, "W") == "W"
    assert _format_wind(None, None) is None


def test_format_wind_converts_numeric_bearings():
    """Bearing-style directions are converted before joining."""
    assert _format_wind("9.7", "286") == "WNW 9.7"
    assert _format_wind("9.7", None) == "9.7"


def test_first_present_returns_first_non_none_field():
    """The first present field wins, in declaration order."""
    mapping = {"Wind": "4 mph", "WindSpeed": "2 mph"}
    assert _first_present(mapping, "WindSpeed", "Wind") == "2 mph"
    assert _first_present(mapping, "Wind", "WindSpeed") == "4 mph"
    assert _first_present({"Dewpoint": None}, "Dewpoint") is None
    assert _first_present({}, "AirTemperature") is None


def test_first_enabled_view_prefers_enabled():
    """The first enabled view wins, falling back to the first."""
    views = [
        {"Url": "disabled.jpg", "Status": "Disabled"},
        {"Url": "live.jpg", "Status": "Enabled"},
    ]
    assert _first_enabled_view(views)["Url"] == "live.jpg"
    assert _first_enabled_view([{"Url": "only.jpg"}])["Url"] == "only.jpg"
    assert _first_enabled_view(None) is None
    assert _first_enabled_view([]) is None


def test_travel_iq_requires_api_key():
    """The platform family requires an api key for setup."""
    from custom_components.the511.providers.travel_iq import TravelIQProvider

    assert CONF_API_KEY in TravelIQProvider.required_config_keys
    assert CONF_API_KEY in TravelIQProvider.secret_config_keys
