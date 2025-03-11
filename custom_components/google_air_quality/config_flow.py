import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, API_URL

class GoogleAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Google Air Quality."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate the API key by making a test request
            session = aiohttp_client.async_get_clientsession(self.hass)
            try:
                async with session.post(
                    f"{API_URL}?key={user_input['api_key']}",
                    json={
                        "location": {
                            "latitude": user_input['latitude'],
                            "longitude": user_input['longitude']
                        }
                    },
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        return self.async_create_entry(title="Google Air Quality", data=user_input)
                    else:
                        errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("latitude"): float,
            vol.Required("longitude"): float,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
