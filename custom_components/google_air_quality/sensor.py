from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import aiohttp

DOMAIN = "google_air_quality"
API_URL = "https://airquality.googleapis.com/v1/currentConditions:lookup"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Google Air Quality sensors."""
    api_key = entry.data.get("api_key")
    latitude = entry.data.get("latitude")
    longitude = entry.data.get("longitude")
    async_add_entities([GoogleAirQualitySensor(api_key, latitude, longitude)])

class GoogleAirQualitySensor(Entity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, api_key, latitude, longitude):
        """Initialize the sensor."""
        self._api_key = api_key
        self._latitude = latitude
        self._longitude = longitude
        self._state = None
        self._attributes = {}
        self._attr_name = "Google Air Quality"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    async def async_update(self):
        """Fetch new data from the API."""
        params = {
            "location": f"{self._latitude},{self._longitude}",
            "key": self._api_key
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, params=params) as response:
                    if response.status != 200:
                        self._state = "Error"
                        self._attributes = {"error": f"HTTP {response.status}"}
                        return

                    data = await response.json()
                    self._state = data.get("index", {}).get("aqi", "Unknown")
                    self._attributes = {
                        "pm2_5": data.get("pollutants", {}).get("pm2_5", {}).get("concentration", "Unknown"),
                        "pm10": data.get("pollutants", {}).get("pm10", {}).get("concentration", "Unknown"),
                        "co": data.get("pollutants", {}).get("co", {}).get("concentration", "Unknown"),
                        "ozone": data.get("pollutants", {}).get("o3", {}).get("concentration", "Unknown"),
                        "no2": data.get("pollutants", {}).get("no2", {}).get("concentration", "Unknown"),
                        "health_recommendations": data.get("health_recommendations", "None")
                    }
            except aiohttp.ClientError as e:
                self._state = "Error"
                self._attributes = {"error": str(e)}
