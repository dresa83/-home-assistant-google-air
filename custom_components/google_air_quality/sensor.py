from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

# Define health recommendation groups
RECOMMENDATION_GROUPS = [
    "generalPopulation",
    "elderly",
    "lungDiseasePopulation",
    "heartDiseasePopulation",
    "athletes",
    "pregnantWomen",
    "children"
]

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    # Create pollutant sensors
    for pollutant in coordinator.data.get("pollutants", {}):
        sensors.append(GoogleAirQualitySensor(coordinator, pollutant))

    # Create the health recommendation sensor
    sensors.append(GoogleAirQualityHealthSensor(coordinator))

    async_add_entities(sensors)

class GoogleAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality pollutant sensor."""

    def __init__(self, coordinator, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Google Air Quality {sensor_type.upper()} Concentration"
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._last_state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {}).get("value", "Unknown")

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
        """Force update to trigger Logbook correctly."""
        current_state = self.state

        # Force write state even if value didn't change
        if current_state != self._last_state or current_state == "Unknown":
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
    """Representation of a single Health Recommendation sensor."""

    def __init__(self, coordinator):
        """Initialize the health recommendation sensor."""
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality Health Recommendations"
        self._attr_unique_id = f"{DOMAIN}_health_recommendations"

    @property
    def state(self):
        """Static state just to represent presence."""
        return "Available"

    @property
    def extra_state_attributes(self):
        """Return health recommendations as attributes."""
        recommendations = self.coordinator.data.get("recommendations", {})
        return {
            group: recommendations.get(group, "No recommendation available.")
            for group in RECOMMENDATION_GROUPS
        }

    def _handle_coordinator_update(self):
        """Force update to trigger Logbook correctly."""
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
