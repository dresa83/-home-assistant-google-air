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

    # Create health recommendation sensors
    for group, recommendation in coordinator.data.get("recommendations", {}).items():
        sensors.append(GoogleAirQualityRecommendationSensor(coordinator, group, recommendation))

    async_add_entities(sensors)

class GoogleAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality pollutant sensor."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the pollutant sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._sensor_type = sensor_type

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

class GoogleAirQualityRecommendationSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Health Recommendation sensor."""

    def __init__(self, coordinator, group, recommendation):
        """Initialize the health recommendation sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Health Recommendation - {group.replace('_', ' ').title()}"
        self._attr_unique_id = f"{DOMAIN}_recommendation_{group}"
        self._group = group
        self._recommendation = recommendation

    @property
    def state(self):
        """Return the recommendation text."""
        return self.coordinator.data.get("recommendations", {}).get(self._group, "No recommendation available.")

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
