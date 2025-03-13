from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from datetime import datetime, timezone
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

# Mapping pollutants to icons
POLLUTANT_ICONS = {
    "pm25": "mdi:weather-hazy",
    "pm10": "mdi:weather-windy",
    "co": "mdi:molecule-co",
    "no2": "mdi:molecule",
    "o3": "mdi:weather-cloudy",
    "so2": "mdi:chemical-weapon"
}

def get_color_category(sensor_type, value):
    """Determine color category based on pollutant value."""
    if value == "Unknown" or value is None:
        return "unknown"

    value = float(value)

    if sensor_type == "pm25":
        if value <= 12: return "green"
        elif value <= 35.4: return "yellow"
        elif value <= 55.4: return "orange"
        elif value <= 150.4: return "red"
        elif value <= 250.4: return "purple"
        else: return "maroon"

    elif sensor_type == "pm10":
        if value <= 54: return "green"
        elif value <= 154: return "yellow"
        elif value <= 254: return "orange"
        elif value <= 354: return "red"
        elif value <= 424: return "purple"
        else: return "maroon"

    elif sensor_type == "co":
        if value <= 4.4: return "green"
        elif value <= 9.4: return "yellow"
        elif value <= 12.4: return "orange"
        elif value <= 15.4: return "red"
        elif value <= 30.4: return "purple"
        else: return "maroon"

    elif sensor_type == "no2":
        if value <= 53: return "green"
        elif value <= 100: return "yellow"
        elif value <= 360: return "orange"
        elif value <= 649: return "red"
        elif value <= 1249: return "purple"
        else: return "maroon"

    elif sensor_type == "o3":
        if value <= 54: return "green"
        elif value <= 70: return "yellow"
        elif value <= 85: return "orange"
        elif value <= 105: return "red"
        elif value <= 200: return "purple"
        else: return "maroon"

    elif sensor_type == "so2":
        if value <= 35: return "green"
        elif value <= 75: return "yellow"
        elif value <= 185: return "orange"
        elif value <= 304: return "red"
        elif value <= 604: return "purple"
        else: return "maroon"

    return "unknown"

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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {}).get("value", "Unknown")

    @property
    def icon(self):
        """Assign custom icon based on pollutant type."""
        return POLLUTANT_ICONS.get(self._sensor_type, "mdi:cloud")

    @property
    def extra_state_attributes(self):
        """Return additional attributes including last updated and color category."""
        pollutant = self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {})
        value = pollutant.get("value", "Unknown")
        last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S")
        color_category = get_color_category(self._sensor_type, value)

        return {
            "unit": pollutant.get("unit", "Unknown"),
            "sources": pollutant.get("sources", "Unknown"),
            "effects": pollutant.get("effects", "Unknown"),
            "last_updated": last_updated,
            "color_category": color_category
        }

    def _handle_coordinator_update(self):
        """Force state update and fire custom event for Logbook."""
        self.async_write_ha_state()

        self.hass.bus.async_fire(
            "google_air_quality_state_changed",
            {
                "entity_id": self.entity_id,
                "new_state": self.state,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        )

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
        """Static state to indicate availability."""
        return "Available"

    @property
    def icon(self):
        """Custom icon for health recommendations."""
        return "mdi:heart-pulse"

    @property
    def extra_state_attributes(self):
        """Return health recommendations as attributes, with last updated."""
        recommendations = self.coordinator.data.get("recommendations", {})
        last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        return {
            group: recommendations.get(group, "No recommendation available.")
            for group in RECOMMENDATION_GROUPS
        } | {"last_updated": last_updated}

    def _handle_coordinator_update(self):
        """Force state update and fire custom event for Logbook."""
        self.async_write_ha_state()

        self.hass.bus.async_fire(
            "google_air_quality_state_changed",
            {
                "entity_id": self.entity_id,
                "new_state": self.state,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        )

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
