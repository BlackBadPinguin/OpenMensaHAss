from homeassistant import config_entries
import voluptuous as vol
import aiohttp

from .const import DOMAIN, CONF_MENSA_ID

async def get_mensen():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://openmensa.org/api/v2/canteens") as resp:
            return await resp.json()

class OpenMensaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=f"Mensa ID: {user_input[CONF_MENSA_ID]}",
                data=user_input,
            )

        # Hole Mensen
        mensen = await get_mensen()
        options = {str(m["id"]): m["name"] for m in mensen}

        schema = vol.Schema({
            vol.Required(CONF_MENSA_ID): vol.In(options)
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)