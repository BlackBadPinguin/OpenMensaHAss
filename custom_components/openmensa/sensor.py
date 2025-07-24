from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import ATTR_ATTRIBUTION
from datetime import datetime, timedelta
import logging
import aiohttp

from .const import DOMAIN, CONF_MENSA_ID

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Daten von OpenMensa.org"

async def async_setup_entry(hass, entry, async_add_entities):
    mensa_id = entry.data[CONF_MENSA_ID]
    session = async_get_clientsession(hass)

    coordinator = OpenMensaCoordinator(hass, session, mensa_id)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        OpenMensaTodaySensor(coordinator, mensa_id),
        OpenMensaWeekSensor(coordinator, mensa_id)
    ])

class OpenMensaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session: aiohttp.ClientSession, mensa_id: str):
        super().__init__(
            hass,
            _LOGGER,
            name="OpenMensaCoordinator",
            update_interval=timedelta(hours=6),
        )
        self.session = session
        self.mensa_id = mensa_id
        self.data = {}

    async def _async_update_data(self):
        data = {}
        today = datetime.today().date()
        for i in range(7):
            date = today + timedelta(days=i)
            url = f"https://openmensa.org/api/v2/canteens/{self.mensa_id}/days/{date}/meals"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data[str(date)] = await resp.json()
                elif resp.status == 404:
                    data[str(date)] = []  # Mensa geschlossen
        return data

class OpenMensaTodaySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, mensa_id):
        super().__init__(coordinator)
        self._date = datetime.today().date()
        self._attr_name = "OpenMensa Today"
        self._attr_unique_id = f"openmensa_{mensa_id}_today"
        self._attr_icon = "mdi:calendar-today"

    @property
    def native_value(self):
        meals = self.coordinator.data.get(str(self._date), [])
        if not meals:
            return "Geschlossen"
        return ", ".join(meal["name"] for meal in meals)

    @property
    def extra_state_attributes(self):
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "date": str(self._date),
            "meals": self.coordinator.data.get(str(self._date), [])
        }

class OpenMensaWeekSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, mensa_id):
        super().__init__(coordinator)
        self._start_date = datetime.today().date()
        self._attr_name = "OpenMensa Week"
        self._attr_unique_id = f"openmensa_{mensa_id}_week"
        self._attr_icon = "mdi:calendar-week"

    @property
    def native_value(self):
        summary = []
        for i in range(7):
            date = self._start_date + timedelta(days=i)
            meals = self.coordinator.data.get(str(date), [])
            if not meals:
                summary.append(f"{date.strftime('%A')}: Geschlossen")
            else:
                meal_names = ", ".join(meal["name"] for meal in meals)
                summary.append(f"{date.strftime('%A')}: {meal_names}")
        return " | ".join(summary)

    @property
    def extra_state_attributes(self):
        attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "week": {}
        }
        for i in range(7):
            date = self._start_date + timedelta(days=i)
            attributes["week"][str(date)] = self.coordinator.data.get(str(date), [])
        return attributes
