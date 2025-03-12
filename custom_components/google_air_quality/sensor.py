from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        GoogleAirQualitySensor(coordinator, "AQI", "Air Quality Index"),
        GoogleAirQualitySensor(coordinator, "PM2_5", "PM 2.5 Concentration"),
        GoogleAirQualitySensor(coordinator, "PM10", "PM10 Concentration")
    ]
    async_add_entities(sensors)

class GoogleAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._sensor_type = sensor_type
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "google_air_quality")},
            "name": "Google Air Quality",
            "manufacturer": "Google",
            "model": "Air Quality API",
            "entry_type": "service"
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type, {}).get("value", "Unknown")
