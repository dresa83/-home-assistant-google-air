import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

API_URL = "https://airquality.googleapis.com/v1/currentConditions:lookup"
SCAN_INTERVAL = timedelta(minutes=30)

class GoogleAirQualityDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching Google Air Quality data."""

    def __init__(self, hass, api_key, latitude, longitude, language):
        """Initialize the coordinator."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.language = language

        super().__init__(
            hass,
            _LOGGER,
            name="Google Air Quality",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        payload = {
            "universalAqi": True,
            "location": {"latitude": self.latitude, "longitude": self.longitude},
            "extraComputations": [
                "HEALTH_RECOMMENDATIONS",
                "POLLUTANT_CONCENTRATION",
                "LOCAL_AQI",
                "DOMINANT_POLLUTANT_CONCENTRATION"
            ],
            "languageCode": self.language
        }

        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{API_URL}?key={self.api_key}", json=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                _LOGGER.error(f"API Client Error: {e}")
                return {}
