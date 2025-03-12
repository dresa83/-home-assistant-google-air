from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

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
        """Return the state of the sensor (numeric AQI)."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self._attributes

    @property
    def icon(self):
        """Set custom icon based on AQI value."""
        if self._state is not None:
            if self._state <= 50:
                return "mdi:emoticon-happy"
            elif self._state <= 100:
                return "mdi:emoticon-neutral"
            elif self._state <= 150:
                return "mdi:emoticon-sad"
            else:
                return "mdi:emoticon-dead"
        return "mdi:cloud-question"

    async def async_update(self):
        """Fetch new data from the API."""
        url = f"{API_URL}?key={self._api_key}"
        payload = {
            "universalAqi": True,
            "location": {
                "latitude": self._latitude,
                "longitude": self._longitude
            },
            "extraComputations": [
                "HEALTH_RECOMMENDATIONS",
                "DOMINANT_POLLUTANT_CONCENTRATION",
                "POLLUTANT_CONCENTRATION",
                "LOCAL_AQI",
                "POLLUTANT_ADDITIONAL_INFO"
            ],
            "languageCode": "en"
        }
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        self._state = "Error"
                        self._attributes = {"error": f"HTTP {response.status}"}
                        _LOGGER.error(f"API Error: HTTP {response.status}")
                        return

                    data = await response.json()
                    _LOGGER.debug(f"API Response: {data}")

                    indexes = data.get("indexes", [{}])[0]
                    pollutants = {pollutant["code"]: pollutant for pollutant in data.get("pollutants", [])}

                    self._state = indexes.get("aqi", "Unknown")
                    self._attributes = {
                        "aqi_display": indexes.get("aqiDisplay", "Unknown"),
                        "category": indexes.get("category", "Unknown"),
                        "dominant_pollutant": indexes.get("dominantPollutant", "Unknown"),
                        "region_code": data.get("regionCode", "Unknown"),
                        "date_time": data.get("dateTime", "Unknown"),
                        "pm2_5": pollutants.get("pm25", {}).get("concentration", {}).get("value", "Unknown"),
                        "pm10": pollutants.get("pm10", {}).get("concentration", {}).get("value", "Unknown"),
                        "co": pollutants.get("co", {}).get("concentration", {}).get("value", "Unknown"),
                        "ozone": pollutants.get("o3", {}).get("concentration", {}).get("value", "Unknown"),
                        "no2": pollutants.get("no2", {}).get("concentration", {}).get("value", "Unknown"),
                        "so2": pollutants.get("so2", {}).get("concentration", {}).get("value", "Unknown"),
                        "health_recommendations": data.get("healthRecommendations", {})
                    }
            except aiohttp.ClientError as e:
                self._state = "Error"
                self._attributes = {"error": str(e)}
                _LOGGER.error(f"API Client Error: {e}")
