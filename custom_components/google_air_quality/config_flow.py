from homeassistant import config_entries
import voluptuous as vol

DOMAIN = "google_air_quality"

class GoogleAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Air Quality."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Google Air Quality", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("latitude"): float,
                vol.Required("longitude"): float,
                vol.Optional("language", default="en"): vol.In(["en", "da", "de", "fr", "es", "it", "nl"])
            })
        )
