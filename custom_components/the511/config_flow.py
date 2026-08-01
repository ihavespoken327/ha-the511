"""Config flow for The 511 integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME

from .const import DOMAIN, NAME


# Phase 2: extend this schema with the provider selector once the
# provider registry exists. The form pattern below is kept deliberately
# simple so that extension is a drop-in change.
class The511ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for The 511."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Mapping[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_NAME, default=NAME): str},
            ),
        )
