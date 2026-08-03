"""Tests for The 511 config flow."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_NAME

from custom_components.the511.const import (
    CONF_INCIDENT_RADIUS,
    CONF_MAX_CAMERAS,
    CONF_MAX_INCIDENTS,
    CONF_MAX_TRAVEL_TIMES,
    CONF_PROVIDER,
    CONF_SHOW_ROADWORK,
    DOMAIN,
)


async def test_user_step_aborts_without_providers(hass):
    """With no registered providers the flow should abort."""
    with patch(
        "custom_components.the511.config_flow.get_provider_classes",
        return_value=(),
    ):
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


async def test_user_step_shows_credentials_form(hass, secret_provider_class):
    """Choosing a provider with required keys should show the credentials step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Secret 511", CONF_PROVIDER: "secret"},
    )

    assert result["type"] == "form"
    assert result["step_id"] == "provider_config"


async def test_credentials_step_creates_entry(hass, secret_provider_class):
    """Submitting credentials should create a config entry with them."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Secret 511", CONF_PROVIDER: "secret"},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_API_KEY: "test-key"},
    )

    assert result["type"] == "create_entry"
    assert result["title"] == "Secret 511"
    assert result["data"][CONF_NAME] == "Secret 511"
    assert result["data"][CONF_PROVIDER] == "secret"
    assert result["data"][CONF_API_KEY] == "test-key"


async def test_config_flow_unique_id(hass, fake_provider_class):
    """Each flow run should produce a unique flow id."""
    first = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    second = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert first["flow_id"] != second["flow_id"]


async def test_duplicate_provider_aborts(hass, fake_provider_class):
    """Configuring the same provider twice should abort."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Wisconsin", CONF_PROVIDER: "fake"},
    )
    assert result["type"] == "create_entry"

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Wisconsin again", CONF_PROVIDER: "fake"},
    )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"


async def test_different_providers_create_two_entries(
    hass, fake_provider_class, secret_provider_class
):
    """A second provider should be configurable alongside the first."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Wisconsin", CONF_PROVIDER: "fake"},
    )
    assert result["type"] == "create_entry"

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Secret 511", CONF_PROVIDER: "secret"},
    )
    assert result["type"] == "form"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_API_KEY: "test-key"},
    )

    assert result["type"] == "create_entry"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 2


async def test_options_flow_shows_form(hass, fake_provider_class):
    """The options flow should present the entity-bound schema."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Wisconsin", CONF_PROVIDER: "fake"},
    )
    entry = hass.config_entries.async_entries(DOMAIN)[0]

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert CONF_MAX_CAMERAS in result["data_schema"].schema
    assert CONF_MAX_INCIDENTS in result["data_schema"].schema
    assert CONF_INCIDENT_RADIUS in result["data_schema"].schema
    assert CONF_MAX_TRAVEL_TIMES in result["data_schema"].schema
    assert CONF_SHOW_ROADWORK in result["data_schema"].schema


async def test_options_flow_updates_entry(hass, fake_provider_class):
    """Submitting the options form should persist the new values."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_NAME: "Wisconsin", CONF_PROVIDER: "fake"},
    )
    entry = hass.config_entries.async_entries(DOMAIN)[0]

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_MAX_CAMERAS: 10,
            CONF_MAX_INCIDENTS: 5,
            CONF_INCIDENT_RADIUS: 25,
            CONF_MAX_TRAVEL_TIMES: 10,
            CONF_SHOW_ROADWORK: True,
        },
    )

    assert result["type"] == "create_entry"
    options = hass.config_entries.async_get_entry(entry.entry_id).options
    assert options[CONF_MAX_CAMERAS] == 10
    assert options[CONF_MAX_INCIDENTS] == 5
    assert options[CONF_INCIDENT_RADIUS] == 25
    assert options[CONF_MAX_TRAVEL_TIMES] == 10
    assert options[CONF_SHOW_ROADWORK] is True
