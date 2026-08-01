"""Config flow for The 511 integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import CONF_PROVIDER, DOMAIN, NAME
from .providers import BaseProvider, get_provider_class, get_provider_classes


class The511ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for The 511."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow with per-run state."""
        self._provider_class: type[BaseProvider] | None = None
        self._user_input: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: Mapping[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        provider_classes = get_provider_classes()
        if not provider_classes:
            return self.async_abort(reason="no_providers_available")

        if user_input is not None:
            self._user_input = dict(user_input)
            provider_id = str(user_input[CONF_PROVIDER])
            self._provider_class = get_provider_class(provider_id)
            for existing in self._async_current_entries():
                if existing.data.get(CONF_PROVIDER) == provider_id:
                    return self.async_abort(
                        reason="already_configured",
                        description_placeholders={
                            "provider": self._provider_class.name
                        },
                    )
            if self._provider_class.required_config_keys:
                return await self.async_step_provider_config()
            return self._create_entry()

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(provider_classes),
        )

    async def async_step_provider_config(
        self, user_input: Mapping[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect the selected provider's required credentials."""
        if self._provider_class is None:
            return self.async_abort(reason="provider_not_selected")

        if user_input is not None:
            self._user_input.update(user_input)
            return self._create_entry()

        return self.async_show_form(
            step_id="provider_config",
            data_schema=_build_credentials_schema(self._provider_class),
            description_placeholders={"provider": self._provider_class.name},
        )

    def _create_entry(self) -> ConfigFlowResult:
        """Create the config entry from the collected user input."""
        return self.async_create_entry(
            title=str(self._user_input[CONF_NAME]),
            data=self._user_input,
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


def _build_credentials_schema(provider_class: type[BaseProvider]) -> vol.Schema:
    """Build a schema collecting the provider's required config keys."""
    fields: dict[Any, Any] = {}
    for key in provider_class.required_config_keys:
        if key in provider_class.secret_config_keys:
            fields[vol.Required(key)] = selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                )
            )
        else:
            fields[vol.Required(key)] = str
    return vol.Schema(fields)
