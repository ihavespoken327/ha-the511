"""Tests for the shared Travel-IQ provider base."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY

from custom_components.the511.providers.travel_iq import (
    _first_enabled_view,
    _format_wind,
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
