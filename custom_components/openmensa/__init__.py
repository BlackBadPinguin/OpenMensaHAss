from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the OpenMensa integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenMensa from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    # Zukünftige, empfohlene Methode
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an OpenMensa config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
