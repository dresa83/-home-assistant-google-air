from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_LANGUAGE, DEFAULT_SCAN_INTERVAL

class GoogleAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Air Quality."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if user_input is not None:
            return self.async_create_entry(title="Google Air Quality", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("latitude"): float,
                vol.Required("longitude"): float,
                vol.Optional("language", default=DEFAULT_LANGUAGE): vol.In(["en", "da", "de", "fr", "es", "it", "nl"]),
                vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int
            })
        )

class GoogleAirQualityOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow for Google Air Quality."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options step."""
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("language", default=self.config_entry.options.get("language", DEFAULT_LANGUAGE)):
                    vol.In(["en", "da", "de", "fr", "es", "it", "nl"]),
                vol.Optional("scan_interval", default=self.config_entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)): int,
            })
        )
