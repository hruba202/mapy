pythonfrom homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_GEO_QUERY, CONF_ROUTE_START, CONF_ROUTE_END

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Mapy.cz sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Přidat geokódovací senzor, pokud byl zadán dotaz
    if entry.data.get(CONF_GEO_QUERY):
        entities.append(MapyCzGeocodeSensor(coordinator, entry))

    # Přidat senzor trasy, pokud byl zadán start a cíl
    if entry.data.get(CONF_ROUTE_START) and entry.data.get(CONF_ROUTE_END):
        entities.append(MapyCzRouteSensor(coordinator, entry))

    async_add_entities(entities, True)


class MapyCzGeocodeSensor(CoordinatorEntity, SensorEntity):
    """Senzor pro vyhledání adresy a souřadnic."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._query = entry.data.get(CONF_GEO_QUERY)
        self._attr_name = f"Mapy.cz Geocode ({self._query})"
        self._attr_unique_id = f"mapycz_geo_{entry.entry_id}"

    @property
    def state(self):
        """Stav senzoru je textová podoba nejlepší shody."""
        data = self.coordinator.data.get("geocode")
        if data and data.get("items"):
            return data["items"][0].get("name", "Neznámé místo")
        return "Nenalezeno"

    @property
    def extra_state_attributes(self):
        """Atributy obsahují přesné zeměpisné souřadnice."""
        data = self.coordinator.data.get("geocode")
        if data and data.get("items"):
            item = data["items"][0]
            return {
                "latitude": item["position"]["lat"],
                "longitude": item["position"]["lon"],
                "label": item.get("label"),
                "type": item.get("type")
            }
        return {}


class MapyCzRouteSensor(CoordinatorEntity, SensorEntity):
    """Senzor pro výpočet vzdálenosti a času trasy."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._start = entry.data.get(CONF_ROUTE_START)
        self._end = entry.data.get(CONF_ROUTE_END)
        self._attr_name = f"Mapy.cz Trasa {self._start} -> {self._end}"
        self._attr_unique_id = f"mapycz_route_{entry.entry_id}"
        # Nastavení jednotky stavu na kilometry
        self._attr_native_unit_of_measurement = "km"

    @property
    def native_value(self):
        """Stav senzoru vyjadřuje celkovou délku trasy v km."""
        data = self.coordinator.data.get("routing")
        if data and data.get("length"):
            # API vrací metry, převedeme na kilometry s přesností na 1 desatinné místo
            return round(data["length"] / 1000, 1)
        return None

    @property
    def extra_state_attributes(self):
        """Atributy obsahují čas dojezdu a podrobnosti."""
        data = self.coordinator.data.get("routing")
        if data and data.get("length"):
            duration_seconds = data.get("duration", 0)
            return {
                "duration_seconds": duration_seconds,
                "duration_minutes": round(duration_seconds / 60),
                "formatted_duration": f"{round(duration_seconds // 3600)}h {round((duration_seconds % 3600) // 60)}m",
                "start_point": self._start,
                "end_point": self._end
            }
        return {}
