from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, CONF_MENSA_ID, CONF_RADIUS_KM, CONF_ZONE

_LOGGER = logging.getLogger(__name__)


class OpenMensaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.zone_entity_id: str | None = None
        self.zone_coords: tuple[float, float] | None = None
        self.radius_km: int = 10
        self.canteens: list[dict[str, Any]] = []

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.zone_entity_id = user_input[CONF_ZONE]
            self.radius_km = user_input[CONF_RADIUS_KM]

            zone_state = self.hass.states.get(self.zone_entity_id)
            if not zone_state:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_zone_form_schema(),
                    errors={"base": "zone_not_found"}
                )

            lat = zone_state.attributes.get("latitude")
            lon = zone_state.attributes.get("longitude")
            if lat is None or lon is None:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_zone_form_schema(),
                    errors={"base": "zone_has_no_location"}
                )

            self.zone_coords = (lat, lon)

            # Hole Mensen aus OpenMensa
            self.canteens = await self._find_nearby_canteens(self.zone_coords, self.radius_km)

            if not self.canteens:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_zone_form_schema(),
                    errors={"base": "no_canteens_found"}
                )

            return await self.async_step_select_canteen()

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_zone_form_schema()
        )

    async def async_step_select_canteen(self, user_input=None):
        if user_input is not None:
            canteen_id = user_input[CONF_MENSA_ID]
            canteen = next((c for c in self.canteens if str(c["id"]) == canteen_id), None)

            if not canteen:
                return self.async_abort(reason="invalid_canteen")

            await self.async_set_unique_id(str(canteen["id"]))
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=canteen.get("name", f"Mensa {canteen_id}"),
                data={
                    CONF_MENSA_ID: canteen["id"],
                    CONF_RADIUS_KM: self.radius_km,
                    CONF_ZONE: self.zone_entity_id,
                },
            )

        canteen_options = {
            str(c["id"]): f'{c["name"]} ({c["city"]})' for c in self.canteens
        }

        return self.async_show_form(
            step_id="select_canteen",
            data_schema=vol.Schema({
                vol.Required(CONF_MENSA_ID): vol.In(canteen_options)
            })
        )

    def _get_zone_form_schema(self):
        zones = {
            state.entity_id: state.name or state.entity_id
            for state in self.hass.states.async_all("zone")
        }

        return vol.Schema({
            vol.Required(CONF_ZONE): vol.In(zones),
            vol.Required(CONF_RADIUS_KM, default=10): vol.All(vol.Coerce(int), vol.Range(min=1, max=100))
        })

    async def _find_nearby_canteens(self, coords: tuple[float, float], radius_km: int):
        lat, lon = coords
        url = f"https://openmensa.org/api/v2/canteens?near[lat]={lat}&near[lng]={lon}&near[dist]={radius_km * 1000}"

        session = aiohttp_client.async_get_clientsession(self.hass)

        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    _LOGGER.warning("OpenMensa API returned status %s", resp.status)
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching OpenMensa data: %s", err)

        return []

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
            description_placeholders={
                "info": "Optionen werden hier noch ergänzt..."
            }
        )
