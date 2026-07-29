#config_flow.py – Uživatelské rozhraní pro zadání API klíče v nastavení Home Assistanta:
python
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_API_KEY

class MapyCzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Mapy.cz", data=user_input)

        schema = vol.Schema({vol.Required(CONF_API_KEY): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
