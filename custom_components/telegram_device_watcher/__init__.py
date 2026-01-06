from .const import DOMAIN
from .watcher import TelegramDeviceWatcher


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass, entry):
    watcher = TelegramDeviceWatcher(hass, entry)
    await watcher.async_start()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = watcher
    return True


async def async_unload_entry(hass, entry):
    watcher = hass.data[DOMAIN].pop(entry.entry_id)
    watcher.async_stop()
    return True
