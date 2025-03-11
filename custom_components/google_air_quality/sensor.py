import aiohttp
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Google Air Quality sensor based on a config entry."""
    coordinator = GoogleAirQualityCoordinator(
        hass,
        entry.data["api_key"],
        entry.data["latitude"],
        entry.data["longitude"],
    )
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([GoogleAirQualitySensor(coordinator)], True)

class GoogleAirQualityCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api_key: str, latitude: float, longitude: float):
        """Initialize."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.session = aiohttp.ClientSession()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=30),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with self.session.post(
                f"{API_URL}?key={self.api_key}",
                json={
                    "location": {
                        "latitude": self.latitude,
                        "longitude": self.longitude
                    }
                },
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    _LOGGER.error("API returned status code %s", response.status)
                    return {}
                data = await response.json()
                _LOGGER.debug("API Response: %s", data)
                return data
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            return {}

class GoogleAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality Sensor."""

    def __init__(self, coordinator: GoogleAirQualityCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality Sensor"
        self._attr_unique_id = f"google_air_quality_{coordinator.latitude}_{coordinator.longitude}"

    @property
    def native_value(self):
        """Return the current AQI."""
        indexes = self.coordinator.data.get("indexes", [])
        if indexes:
            return indexes[0].get("aqi")
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        indexes = self.coordinator.data.get("indexes", [])
        if indexes:
            return {
                "category": indexes[0].get("category"),
                "dominant_pollutant": indexes[0].get("dominantPollutant"),
                "aqi_display": indexes[0].get("aqiDisplay"),
                "region_code": self.coordinator.data.get("regionCode")
            }
        return {}
