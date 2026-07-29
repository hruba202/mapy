#config_flow.py – Uživatelské rozhraní pro zadání API klíče v nastavení Home Assistanta:
#python
pythonimport voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_KEY, CONF_GEO_QUERY, CONF_ROUTE_START, CONF_ROUTE_END, CONF_ROUTE_MODE

class MapyCzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mapy.cz."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Mapy.cz Služby", data=user_input)

        DATA_SCHEMA = vol.Schema({
            vol.Required(CONF_API_KEY): str,
            vol.Optional(CONF_GEO_QUERY, default=""): str,
            vol.Optional(CONF_ROUTE_START, default=""): str,
            vol.Optional(CONF_ROUTE_END, default=""): str,
            vol.Optional(CONF_ROUTE_MODE, default="car_fast"): vol.In(["car_fast", "car_short", "bike", "foot"]),
        })

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
