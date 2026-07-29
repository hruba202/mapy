python
import logging
from datetime import timedelta
import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_KEY, CONF_GEO_QUERY, CONF_ROUTE_START, CONF_ROUTE_END, CONF_ROUTE_MODE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mapy.cz integration via Coordinator."""
    coordinator = MapyCzDataCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Mapy.cz integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class MapyCzDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Mapy.cz data from API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the coordinator."""
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=10), # Aktualizace každých 10 minut
        )

    async def _async_update_data(self):
        """Fetch data from Mapy.cz REST API endpoints."""
        api_key = self.entry.data.get(CONF_API_KEY)
        geo_query = self.entry.data.get(CONF_GEO_QUERY)
        r_start = self.entry.data.get(CONF_ROUTE_START)
        r_end = self.entry.data.get(CONF_ROUTE_END)
        r_mode = self.entry.data.get(CONF_ROUTE_MODE)

        headers = {"accept": "application/json", "X-API-KEY": api_key}
        results = {"geocode": None, "routing": None}

        async with aiohttp.ClientSession() as session:
            # 1. Volání Geokódování (pokud je vyplněno)
            if geo_query:
                geo_url = f"https://mapy.cz{geo_query}"
                try:
                    async with session.get(geo_url, headers=headers) as response:
                        if response.status == 200:
                            results["geocode"] = await response.json()
                except Exception as err:
                    _LOGGER.error("Chyba při geokódování: %s", err)

            # 2. Volání Routingu (pokud je vyplněn start i cíl)
            if r_start and r_end:
                # API v1 vyžaduje pro výpočet trasy souřadnice. Pro zjednodušení uživatelského zadávání
                # nejprve převedeme textový start a cíl na souřadnice pomocí rychlého geokódování.
                start_coords = await self._geocode_text(session, headers, r_start)
                end_coords = await self._geocode_text(session, headers, r_end)

                if start_coords and end_coords:
                    route_url = f"https://mapy.cz{start_coords}&end={end_coords}&mode={r_mode}"
                    try:
                        async with session.get(route_url, headers=headers) as response:
                            if response.status == 200:
                                results["routing"] = await response.json()
                    except Exception as err:
                        _LOGGER.error("Chyba při výpočtu trasy: %s", err)

        return results

    async def _geocode_text(self, session, headers, text_query):
        """Pomocná funkce pro převod textu na souřadnice (lon,lat)."""
        url = f"https://mapy.cz{text_query}"
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("items"):
                        pos = data["items"][0]["position"]
                        return f"{pos['lon']},{pos['lat']}"
        except Exception:
            return None
        return None
