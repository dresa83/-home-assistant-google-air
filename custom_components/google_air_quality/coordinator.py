import aiohttp
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

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
        """Fetch data from the API."""
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

        try:
            async with self.session.post(
                f"https://airquality.googleapis.com/v1/currentConditions:lookup?key={self.api_key}",
                json=payload, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug(f"API Response: {data}")

                # Validate and return data
                if not data or "indexes" not in data:
                    _LOGGER.error("No valid data returned from API")
                    return {}

                return {
                    "AQI": data.get("indexes", [{}])[0].get("aqi", "Unknown"),
                    "PM2_5": data.get("pollutants", [{}])[0].get("concentration", {}).get("value", "Unknown"),
                    "PM10": data.get("pollutants", [{}])[1].get("concentration", {}).get("value", "Unknown")
                }

        except aiohttp.ClientError as e:
            _LOGGER.error(f"API Client Error: {e}")
            return {}
