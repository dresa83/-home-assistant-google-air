from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
import aiohttp
import logging
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

DOMAIN = "google_air_quality"
API_URL = "https://airquality.googleapis.com/v1/currentConditions:lookup"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Google Air Quality as a service with persistent sensors."""
    api_key = entry.data.get("api_key")
    latitude = entry.data.get("latitude")
    longitude = entry.data.get("longitude")
    sensors = {}

    async def fetch_air_quality():
        """Fetch air quality data and update sensors."""
        payload = {
            "universalAqi": True,
            "location": {
                "latitude": latitude,
                "longitude": longitude
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
                async with session.post(f"{API_URL}?key={api_key}", json=payload, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"API Error: HTTP {response.status}")
                        return
                    data = await response.json()
                    _LOGGER.debug(f"API Response: {data}")

                    indexes = data.get("indexes", [{}])[0]
                    pollutants = {pollutant["code"]: pollutant for pollutant in data.get("pollutants", [])}

                    # Update or create AQI sensor
                    if "AQI" not in sensors:
                        sensors["AQI"] = GoogleAirQualitySensor("AQI")
                        hass.helpers.entity_platform.async_add_entities([sensors["AQI"]])
                    sensors["AQI"].update_state(indexes.get("aqi", "Unknown"))

                    # Update or create pollutant sensors
                    for code, pollutant in pollutants.items():
                        sensor_name = code.upper()
                        if sensor_name not in sensors:
                            sensors[sensor_name] = GoogleAirQualitySensor(sensor_name)
                            hass.helpers.entity_platform.async_add_entities([sensors[sensor_name]])
                        sensors[sensor_name].update_state(pollutant.get("concentration", {}).get("value", "Unknown"))

                    # Update or create health recommendation sensors
                    recommendations = data.get("healthRecommendations", {})
                    for group, recommendation in recommendations.items():
                        sensor_name = f"recommendation_{group}"
                        if sensor_name not in sensors:
                            sensors[sensor_name] = GoogleAirQualitySensor(sensor_name)
                            hass.helpers.entity_platform.async_add_entities([sensors[sensor_name]])
                        sensors[sensor_name].update_state(recommendation)

            except aiohttp.ClientError as e:
                _LOGGER.error(f"API Client Error: {e}")

    async def handle_get_data(call: ServiceCall):
        """Handle manual service call to update air quality data."""
        await fetch_air_quality()

    # Register the service
    hass.services.async_register(DOMAIN, "get_data", handle_get_data)

    # Schedule automatic updates every 30 minutes
    async_track_time_interval(hass, fetch_air_quality, timedelta(minutes=30))

    return True

class GoogleAirQualitySensor(Entity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, name):
        self._name = name
        self._state = None

    @property
    def name(self):
        return f"Google Air Quality {self._name}"

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return f"google_air_quality_{self._name.lower()}"

    def update_state(self, new_state):
        """Update the state and notify Home Assistant."""
        self._state = new_state
        self.async_schedule_update_ha_state()

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the service when the integration is removed."""
    hass.services.async_remove(DOMAIN, "get_data")
    return True
