from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
import aiohttp
import logging
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

DOMAIN = "google_air_quality"
API_URL = "https://airquality.googleapis.com/v1/currentConditions:lookup"
SCAN_INTERVAL = timedelta(minutes=30)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Google Air Quality sensors."""
    api_key = entry.data.get("api_key")
    latitude = entry.data.get("latitude")
    longitude = entry.data.get("longitude")
    language = entry.data.get("language", "en")

    sensor_manager = AirQualitySensorManager(hass, api_key, latitude, longitude, language, async_add_entities)
    hass.data[DOMAIN]["sensor_manager"] = sensor_manager

    # Perform initial fetch
    await sensor_manager.auto_update()

    # Automatic updates
    async_track_time_interval(hass, sensor_manager.auto_update, SCAN_INTERVAL)

    return True

class AirQualitySensorManager:
    """Manager for creating and updating air quality sensors."""

    def __init__(self, hass, api_key, latitude, longitude, language, async_add_entities):
        self.hass = hass
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
        self.async_add_entities = async_add_entities
        self.sensors = {}

    async def fetch_air_quality_data(self):
        """Fetch data from the API."""
        payload = {
            "universalAqi": True,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "extraComputations": [
                "HEALTH_RECOMMENDATIONS",
                "DOMINANT_POLLUTANT_CONCENTRATION",
                "POLLUTANT_CONCENTRATION",
                "LOCAL_AQI",
                "POLLUTANT_ADDITIONAL_INFO"
            ],
            "languageCode": self.language
        }
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{API_URL}?key={self.api_key}", json=payload, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error(f"API Error: HTTP {response.status}")
                        return None
                    return await response.json()
            except aiohttp.ClientError as e:
                _LOGGER.error(f"API Client Error: {e}")
                return None

    async def auto_update(self, *_):
        """Automatically update data."""
        await self._update_sensors()

    async def _update_sensors(self):
        """Fetch data and update or create sensors."""
        data = await self.fetch_air_quality_data()
        if not data:
            return

        indexes = data.get("indexes", [{}])[0]
        pollutants = {pollutant["code"]: pollutant for pollutant in data.get("pollutants", [])}

        await self._create_or_update_sensor("AQI", indexes.get("aqi", "Unknown"))

        for code, pollutant in pollutants.items():
            value = pollutant.get("concentration", {}).get("value", "Unknown")
            await self._create_or_update_sensor(code.upper(), value)

    async def _create_or_update_sensor(self, name, state):
        """Create or update sensor."""
        if name in self.sensors:
            self.sensors[name].update_state(state)
        else:
            sensor = GoogleAirQualitySensor(name, state)
            self.sensors[name] = sensor
            self.async_add_entities([sensor])

class GoogleAirQualitySensor(Entity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, name, state):
        self._name = name
        self._state = state

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
        """Update state."""
        self._state = new_state
        self.async_schedule_update_ha_state()
