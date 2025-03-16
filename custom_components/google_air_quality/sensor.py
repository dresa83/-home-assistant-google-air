from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from datetime import datetime, timezone
from .const import DOMAIN

# Define icons
POLLUTANT_ICONS = {
    "pm25": "mdi:weather-hazy",
    "pm10": "mdi:weather-windy",
    "co": "mdi:molecule-co",
    "no2": "mdi:molecule",
    "o3": "mdi:weather-cloudy",
    "so2": "mdi:chemical-weapon",
    "uaqi": "mdi:cloud"
}

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    # Pollutant Sensors
    for pollutant in coordinator.data.get("pollutants", {}):
        sensors.append(GoogleAirQualitySensor(coordinator, pollutant))

    # UAQI Sensor
    sensors.append(GoogleAirQualityUAQISensor(coordinator))

    # Health Recommendation Sensor
    sensors.append(GoogleAirQualityHealthSensor(coordinator))

    async_add_entities(sensors)

class GoogleAirQualitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Google Air Quality pollutant sensor."""

    def __init__(self, coordinator, sensor_type):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Google Air Quality {sensor_type.upper()} Concentration"
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"

    @property
    def state(self):
        return self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {}).get("value", "Unknown")

    @property
    def icon(self):
        return POLLUTANT_ICONS.get(self._sensor_type, "mdi:cloud")

    @property
    def extra_state_attributes(self):
        pollutant = self.coordinator.data.get("pollutants", {}).get(self._sensor_type, {})
        return {
            "display_name": pollutant.get("displayName", "Unknown"),
            "full_name": pollutant.get("fullName", "Unknown"),
            "value": pollutant.get("value", "Unknown"),
            "unit": pollutant.get("unit", "Unknown"),
            "sources": pollutant.get("sources", "Unknown"),
            "effects": pollutant.get("effects", "Unknown"),
            "last_updated": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "google_air_quality")},
            "name": "Google Air Quality",
            "manufacturer": "Google",
            "model": "Air Quality API",
            "entry_type": "service",
            "configuration_url": "https://developers.google.com/maps/documentation/air-quality"
        }

class GoogleAirQualityUAQISensor(CoordinatorEntity, SensorEntity):
    """Representation of the Universal AQI (UAQI) sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality UAQI"
        self._attr_unique_id = f"{DOMAIN}_uaqi"

    @property
    def state(self):
        index = self._get_uaqi_index()
        return index.get("aqi", "Unknown")

    @property
    def icon(self):
        return POLLUTANT_ICONS["uaqi"]

    @property
    def extra_state_attributes(self):
        index = self._get_uaqi_index()
        color = index.get("color", {})
        return {
            "display_name": index.get("displayName", "Unknown"),
            "category": index.get("category", "Unknown"),
            "dominant_pollutant": index.get("dominantPollutant", "Unknown"),
            "color": {
                "red": color.get("red", 0),
                "green": color.get("green", 0),
                "blue": color.get("blue", 0)
            },
            "last_updated": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_uaqi_index(self):
        indexes = self.coordinator.data.get("indexes", [])
        return next((i for i in indexes if i.get("code") == "uaqi"), {})

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "google_air_quality")},
            "name": "Google Air Quality",
            "manufacturer": "Google",
            "model": "Air Quality API",
            "entry_type": "service",
            "configuration_url": "https://developers.google.com/maps/documentation/air-quality"
        }

class GoogleAirQualityHealthSensor(CoordinatorEntity, SensorEntity):
    """Representation of the Health Recommendation sensor."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Google Air Quality Health Recommendations"
        self._attr_unique_id = f"{DOMAIN}_health_recommendations"

    @property
    def state(self):
        return "Available"

    @property
    def extra_state_attributes(self):
        recommendations = self.coordinator.data.get("recommendations", {})
        return {
            "generalPopulation": recommendations.get("generalPopulation", "No recommendation available."),
            "elderly": recommendations.get("elderly", "No recommendation available."),
            "lungDiseasePopulation": recommendations.get("lungDiseasePopulation", "No recommendation available."),
            "heartDiseasePopulation": recommendations.get("heartDiseasePopulation", "No recommendation available."),
            "athletes": recommendations.get("athletes", "No recommendation available."),
            "pregnantWomen": recommendations.get("pregnantWomen", "No recommendation available."),
            "children": recommendations.get("children", "No recommendation available."),
            "last_updated": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "google_air_quality")},
            "name": "Google Air Quality",
            "manufacturer": "Google",
            "model": "Air Quality API",
            "entry_type": "service",
            "configuration_url": "https://developers.google.com/maps/documentation/air-quality"
        }
