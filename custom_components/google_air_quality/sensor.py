import logging
import requests
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE

_LOGGER = logging.getLogger(__name__)

DOMAIN = "google_air_quality"
API_URL = "https://www.googleapis.com/airquality/v1/current"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the Google Air Quality integration."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Google Air Quality from a config entry."""
    coordinator = GoogleAirQualityCoordinator(
        hass,
        entry.data[CONF_API_KEY],
        entry.data[CONF_LATITUDE],
        entry.data[CONF_LONGITUDE]
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

class GoogleAirQualityCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api_key: str, latitude: float, longitude: float):
        """Initialize the coordinator."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=30),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            response = requests.get(API_URL, params={
                "key": self.api_key,
                "lat": self.latitude,
                "lon": self.longitude
            })
            response.raise_for_status()
            return response.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

class GoogleAirQualitySensor(Entity):
    def __init__(self, coordinator: GoogleAirQualityCoordinator, name: str):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self.coordinator.data.get("aqi")

    @property
    def extra_state_attributes(self):
        return {
            "pm2_5": self.coordinator.data.get("pm2_5"),
            "pm10": self.coordinator.data.get("pm10"),
            "co": self.coordinator.data.get("co"),
            "no2": self.coordinator.data.get("no2"),
        }

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()
