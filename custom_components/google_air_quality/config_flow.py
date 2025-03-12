from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

DOMAIN = "google_air_quality"

class GoogleAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Google Air Quality", data=user_input)

        data_schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("latitude"): float,
            vol.Required("longitude"): float,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

