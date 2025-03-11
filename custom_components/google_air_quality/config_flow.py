import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from .const import DOMAIN

class GoogleAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Air Quality."""

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                # Convert commas to dots for latitude and longitude
                user_input[CONF_LATITUDE] = float(str(user_input[CONF_LATITUDE]).replace(",", "."))
                user_input[CONF_LONGITUDE] = float(str(user_input[CONF_LONGITUDE]).replace(",", "."))
                return self.async_create_entry(title="Google Air Quality", data=user_input)
            except ValueError:
                errors["base"] = "invalid_coordinates"

        data_schema = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Required(CONF_LATITUDE): str,
            vol.Required(CONF_LONGITUDE): str
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
