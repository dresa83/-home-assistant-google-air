from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Google Air Quality sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        GoogleAirQualitySensor(coordinator, "AQI", "Air Quality Index"),
        GoogleAirQualitySensor(coordinator, "PM2_5", "PM 2.5 Concentration"),
        GoogleAirQualitySensor(coordinator, "PM10", "PM10 Concentration"),
        GoogleAirQualitySensor(coordinator, "CO", "CO Concentration"),
        GoogleAirQualitySensor(coordinator, "O3", "Ozone Concentration"),
        GoogleAirQualitySensor(coordinator, "NO2", "NO2 Concentration")
    ]

    async_add_entities(sensors)

class GoogleAirQualitySensor(CoordinatorEntity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type.lower()}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type, {}).get("value", "Unknown")
