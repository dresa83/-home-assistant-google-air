from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from datetime import datetime, timezone
from .const import DOMAIN

# Define EAQI icon
EAQI_ICON = "mdi:weather-cloudy"

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    # Create pollutant sensors
    for pollutant in coordinator.data.get("pollutants", {}):
        sensors.append(GoogleAirQualitySensor(coordinator, pollutant))

    # Create the EAQI sensor
    sensors.append(GoogleAirQualityEAQISensor(coordinator))

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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {}).get("value", "Unknown")

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        pollutant = self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {})
        last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        return {
            "value": pollutant.get("value", "Unknown"),
            "unit": pollutant.get("unit", "Unknown"),
            "sources": pollutant.get("sources", "Unknown"),
            "effects": pollutant.get("effects", "Unknown"),
            "last_updated": last_updated
        }

class GoogleAirQualityEAQISensor(CoordinatorEntity, SensorEntity):
    """Representation of the European AQI (EAQI) sensor."""

    def __init__(self, coordinator):
        """Initialize the EAQI sensor."""
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality EAQI"
        self._attr_unique_id = f"{DOMAIN}_eaqi"

    @property
    def state(self):
        """Return the EAQI value."""
        index = self._get_eaqi_index()
        return index.get("aqi", "Unknown")

    @property
    def extra_state_attributes(self):
        """Return additional EAQI attributes."""
        index = self._get_eaqi_index()
        last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        return {
            "display_name": index.get("displayName", "Unknown"),
            "category": index.get("category", "Unknown"),
            "dominant_pollutant": index.get("dominantPollutant", "Unknown"),
            "last_updated": last_updated
        }

    @property
    def icon(self):
        """Return icon for EAQI."""
        return EAQI_ICON

    def _get_eaqi_index(self):
        """Extract EAQI index from coordinator data."""
        indexes = self.coordinator.data.get("indexes", [])
        return next((i for i in indexes if i.get("code") == "eaqi"), {})

class GoogleAirQualityHealthSensor(CoordinatorEntity, SensorEntity):
    """Representation of the Health Recommendation sensor."""

    def __init__(self, coordinator):
        """Initialize the health recommendation sensor."""
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality Health Recommendations"
        self._attr_unique_id = f"{DOMAIN}_health_recommendations"

    @property
    def state(self):
        """Static state to indicate availability."""
        return "Available"

    @property
    def extra_state_attributes(self):
        """Return health recommendations as attributes."""
        recommendations = self.coordinator.data.get("recommendations", {})
        last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        return {
            "generalPopulation": recommendations.get("generalPopulation", "No recommendation available."),
            "elderly": recommendations.get("elderly", "No recommendation available."),
            "lungDiseasePopulation": recommendations.get("lungDiseasePopulation", "No recommendation available."),
            "heartDiseasePopulation": recommendations.get("heartDiseasePopulation", "No recommendation available."),
            "athletes": recommendations.get("athletes", "No recommendation available."),
            "pregnantWomen": recommendations.get("pregnantWomen", "No recommendation available."),
            "children": recommendations.get("children", "No recommendation available."),
            "last_updated": last_updated
        }
