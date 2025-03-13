from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    # Create pollutant sensors
    for pollutant in coordinator.data.get("pollutants", {}):
        sensors.append(GoogleAirQualitySensor(coordinator, pollutant, f"{pollutant.upper()} Concentration"))

    # Create a dedicated health recommendations sensor
    sensors.append(GoogleAirQualityHealthSensor(coordinator))

    async_add_entities(sensors)

class GoogleAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._sensor_type = sensor_type
        self._last_state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        pollutant_data = self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {})
        value = pollutant_data.get("value")
        return value if value is not None else "Unknown"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        pollutant = self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {})
        return {
            "unit": pollutant.get("unit", "Unknown"),
            "sources": pollutant.get("sources", "Unknown"),
            "effects": pollutant.get("effects", "Unknown")
        }

    def _handle_coordinator_update(self):
        """Force update to trigger Logbook properly."""
        current_state = self.state

        # If state didn't change, force an 'Unknown' state and reset
        if current_state == self._last_state:
            self._last_state = "Unknown"
            self.async_write_ha_state()
        
        self._last_state = current_state
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "google_air_quality")},
            "name": "Google Air Quality",
            "manufacturer": "Google",
            "model": "Air Quality API",
            "entry_type": "service",
            "configuration_url": "https://developers.google.com/maps/documentation/air-quality"
        }

class GoogleAirQualityHealthSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality Health Recommendations sensor."""

    def __init__(self, coordinator):
        """Initialize the health recommendations sensor."""
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality Health Recommendations"
        self._attr_unique_id = f"{DOMAIN}_health_recommendations"

    @property
    def state(self):
        """Return a generic state for recommendations."""
        return "Available"

    @property
    def extra_state_attributes(self):
        """Return all health recommendations as attributes."""
        recommendations = self.coordinator.data.get("recommendations", {})
        return {category: recommendations.get(category, "No recommendation available.") for category in recommendations}

    def _handle_coordinator_update(self):
        """Force update for health recommendations."""
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "google_air_quality")},
            "name": "Google Air Quality",
            "manufacturer": "Google",
            "model": "Air Quality API",
            "entry_type": "service",
            "configuration_url": "https://developers.google.com/maps/documentation/air-quality"
        }
