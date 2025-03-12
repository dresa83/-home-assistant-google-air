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

    sensors = [
        GoogleAirQualitySensor(api_key, latitude, longitude, "aqi", "AQI"),
        GoogleAirQualitySensor(api_key, latitude, longitude, "pm2_5", "PM2.5"),
        GoogleAirQualitySensor(api_key, latitude, longitude, "pm10", "PM10"),
        GoogleAirQualitySensor(api_key, latitude, longitude, "co", "CO"),
        GoogleAirQualitySensor(api_key, latitude, longitude, "ozone", "Ozone"),
        GoogleAirQualitySensor(api_key, latitude, longitude, "no2", "NO2"),
        GoogleAirQualitySensor(api_key, latitude, longitude, "so2", "SO2")
    ]
    async_add_entities(sensors)

class GoogleAirQualitySensor(Entity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, api_key, latitude, longitude, sensor_type, name):
        """Initialize the sensor."""
        self._api_key = api_key
        self._latitude = latitude
        self._longitude = longitude
        self._sensor_type = sensor_type
        self._name = name
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return f"Google Air Quality {self._name}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_update(self):
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
                    pollutants = {pollutant["code"]: pollutant for pollutant in data.get("pollutants", [])}

                    if self._sensor_type == "aqi":
                        indexes = data.get("indexes", [{}])[0]
                        self._state = indexes.get("aqi", "Unknown")
                        self._attributes = {
                            "category": indexes.get("category", "Unknown"),
                            "dominant_pollutant": indexes.get("dominantPollutant", "Unknown"),
                            "region_code": data.get("regionCode", "Unknown"),
                            "date_time": data.get("dateTime", "Unknown"),
                            "health_recommendations": data.get("healthRecommendations", {})
                        }
                    else:
                        self._state = pollutants.get(self._sensor_type, {}).get("concentration", {}).get("value", "Unknown")
                        self._attributes = {
                            "unit": pollutants.get(self._sensor_type, {}).get("concentration", {}).get("units", "Unknown"),
                            "sources": pollutants.get(self._sensor_type, {}).get("additionalInfo", {}).get("sources", "Unknown"),
                            "effects": pollutants.get(self._sensor_type, {}).get("additionalInfo", {}).get("effects", "Unknown")
                        }
            except aiohttp.ClientError as e:
                self._state = "Error"
                self._attributes = {"error": str(e)}
                _LOGGER.error(f"API Client Error: {e}")
