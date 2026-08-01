"""Config flow for The 511 integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import CONF_PROVIDER, DOMAIN, NAME
from .providers import BaseProvider, get_provider_classes


class The511ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for The 511."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Mapping[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        provider_classes = get_provider_classes()
        if not provider_classes:
            return self.async_abort(reason="no_providers_available")

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(provider_classes),
        )


def _build_schema(provider_classes: tuple[type[BaseProvider], ...]) -> vol.Schema:
    """Build the user step schema from the registered provider classes."""
    options = [
        selector.SelectOptionDict(
            value=provider.provider_id,
            label=f"{provider.name} ({provider.region})",
        )
        for provider in provider_classes
    ]
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=NAME): str,
            vol.Required(CONF_PROVIDER): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        }
    )
