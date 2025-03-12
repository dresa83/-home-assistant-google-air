from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_LANGUAGE
from .const import DOMAIN

class GoogleAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type.lower()}_{coordinator.latitude}_{coordinator.longitude}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.latitude}_{coordinator.longitude}")},
            "name": "Google Air Quality",
            "manufacturer": "Google",
            "model": "Air Quality API",
            "entry_type": "service"
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type, {}).get("value", "Unknown")

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return self.coordinator.data.get(self._sensor_type, {})
