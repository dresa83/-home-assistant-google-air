import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, SCAN_INTERVAL

class GoogleAirQualityDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator for fetching Google Air Quality data."""

    def __init__(self, hass: HomeAssistant, api_key, latitude, longitude, language):
        """Initialize the coordinator."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name="Google Air Quality",
            update_interval=timedelta(minutes=SCAN_INTERVAL),
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

        async with self.session.post(
            f"https://airquality.googleapis.com/v1/currentConditions:lookup?key={self.api_key}", json=payload, headers=headers
        ) as response:
            response.raise_for_status()
            return await response.json()
