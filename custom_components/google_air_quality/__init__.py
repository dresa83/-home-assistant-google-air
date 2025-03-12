from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .coordinator import GoogleAirQualityDataUpdateCoordinator
from .sensor import GoogleAirQualitySensor
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Google Air Quality from a config entry."""
    api_key = entry.data.get("api_key")
    latitude = entry.data.get("latitude")
    longitude = entry.data.get("longitude")
    language = entry.data.get("language", "en")

    coordinator = GoogleAirQualityDataUpdateCoordinator(hass, api_key, latitude, longitude, language)
    await coordinator.async_config_entry_first_refresh()

    sensors = [
        GoogleAirQualitySensor(coordinator, "AQI", "Air Quality Index"),
        GoogleAirQualitySensor(coordinator, "PM2_5", "PM 2.5 Concentration"),
        GoogleAirQualitySensor(coordinator, "PM10", "PM10 Concentration"),
        GoogleAirQualitySensor(coordinator, "CO", "CO Concentration"),
        GoogleAirQualitySensor(coordinator, "O3", "Ozone Concentration"),
        GoogleAirQualitySensor(coordinator, "NO2", "NO2 Concentration")
    ]

    async_add_entities(sensors, True)
    return True
