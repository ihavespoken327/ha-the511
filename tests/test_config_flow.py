"""Tests for The 511 config flow."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_NAME

from custom_components.the511.const import CONF_PROVIDER, DOMAIN


async def test_user_step_aborts_without_providers(hass):
    """With no registered providers the flow should abort."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == "abort"
    assert result["reason"] == "no_providers_available"


async def test_user_step_shows_provider_form(hass, fake_provider_class):
    """With a registered provider the flow should show the user form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == "form"
    assert result["step_id"] == "user"


async def test_user_step_creates_entry(hass, fake_provider_class):
    """Submitting the form should create a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Wisconsin", CONF_PROVIDER: "fake"},
    )

    assert result["type"] == "create_entry"
    assert result["title"] == "Wisconsin"
    assert result["data"][CONF_NAME] == "Wisconsin"
    assert result["data"][CONF_PROVIDER] == "fake"


async def test_config_flow_unique_id(hass, fake_provider_class):
    """Each flow run should produce a unique flow id."""
    first = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    second = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert first["flow_id"] != second["flow_id"]
