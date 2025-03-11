from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import HomeAssistantType, ConfigType
from datetime import timedelta
import requests
from .const import DOMAIN, API_URL

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Google Air Quality sensor based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id] = GoogleAirQualityCoordinator(
        hass,
        entry.data["api_key"],
        entry.data["latitude"],
        entry.data["longitude"],
    )
    async_add_entities([GoogleAirQualitySensor(coordinator)], True)

class GoogleAirQualityCoordinator:
    def __init__(self, hass, api_key, latitude, longitude):
        """Initialize the coordinator."""
        self.hass = hass
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.data = {}
        self.update_interval = timedelta(minutes=30)

    async def async_request_refresh(self):
        """Refresh the data from API."""
        self.data = await self._async_update_data()

    async def _async_update_data(self):
        """Fetch data from the API."""
        try:
            response = requests.get(API_URL, params={
                "key": self.api_key,
                "lat": self.latitude,
                "lon": self.longitude
            })
            response.raise_for_status()
            return response.json()
        except Exception as err:
            raise Exception(f"Error fetching data: {err}")

class GoogleAirQualitySensor(CoordinatorEntity, Entity):
    """Representation of a Google Air Quality Sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality Sensor"
        self._attr_unique_id = f"google_air_quality_{coordinator.latitude}_{coordinator.longitude}"

    @property
    def state(self):
        """Return the current AQI."""
        return self.coordinator.data.get("aqi")

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return {
            "pm2_5": self.coordinator.data.get("pm2_5"),
            "pm10": self.coordinator.data.get("pm10"),
            "co": self.coordinator.data.get("co"),
            "no2": self.coordinator.data.get("no2"),
        }
