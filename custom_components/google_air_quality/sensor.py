import aiohttp
import asyncio
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Google Air Quality sensor based on config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id] = GoogleAirQualityCoordinator(
        hass,
        entry.data["api_key"],
        entry.data["latitude"],
        entry.data["longitude"],
    )
    await coordinator.async_request_refresh()
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
        """Fetch data from the API asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
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
