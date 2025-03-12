from .config_flow import GoogleAirQualityOptionsFlowHandler

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Google Air Quality from a config entry."""
    
    # Register the options flow
    hass.config_entries.async_setup_platform(entry, GoogleAirQualityOptionsFlowHandler)

    scan_interval = entry.options.get("scan_interval", entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))
    language = entry.options.get("language", entry.data.get("language", "en"))

    coordinator = GoogleAirQualityDataUpdateCoordinator(
        hass,
        entry.data["api_key"],
        entry.data["latitude"],
        entry.data["longitude"],
        language,
        scan_interval
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
