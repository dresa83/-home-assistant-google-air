import requests
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry

API_URL = "https://airquality.googleapis.com/v1/currentConditions:lookup"

def setup_platform(hass, config, add_entities, discovery_info=None):
    pass

async def async_setup_entry(hass, entry, async_add_entities):
    api_key = entry.data["api_key"]
    latitude = entry.data["latitude"]
    longitude = entry.data["longitude"]
    async_add_entities([GoogleAirQualitySensor(api_key, latitude, longitude)])


class GoogleAirQualitySensor(Entity):
    def __init__(self, api_key, latitude, longitude):
        self._api_key = api_key
        self._latitude = latitude
        self._longitude = longitude
        self._state = None
        self._attributes = {}

    def update(self):
        params = {
            "key": self._api_key,
            "location": f"{self._latitude},{self._longitude}"
        }
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            self._state = data.get("aqi")
            self._attributes = {
                "pm2_5": data.get("pm2_5"),
                "pm10": data.get("pm10"),
                "ozone": data.get("ozone"),
                "no2": data.get("no2"),
                "co": data.get("co"),
                "health_recommendations": data.get("health_recommendations")
            }

    @property
    def name(self):
        return "Google Air Quality"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
