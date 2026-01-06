from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import callback

from .const import (
    CONF_ENTITIES,
    CONF_NOTIFY_SERVICE,
    STATE_OFFLINE,
)


class TelegramDeviceWatcher:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry

        self.entities = set(entry.data.get(CONF_ENTITIES, []))
        self.notify_service = entry.options.get(
            CONF_NOTIFY_SERVICE,
            "notify.telegram",
        )

        self._offline = set()
        self._unsub = None

    async def async_start(self):
        self._unsub = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED,
            self._state_listener,
        )

    def async_stop(self):
        if self._unsub:
            self._unsub()
            self._unsub = None

    @callback
    def _state_listener(self, event):
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if not entity_id or entity_id not in self.entities:
            return

        if not new_state:
            return

        state = new_state.state
        name = new_state.name or entity_id

        # Повернувся online — скидаємо debounce
        if state not in STATE_OFFLINE:
            self._offline.discard(entity_id)
            return

        # Debounce
        if entity_id in self._offline:
            return

        self._offline.add(entity_id)

        self.hass.async_create_task(
            self._send_notify(name, entity_id)
        )

    async def _send_notify(self, name, entity_id):
        domain, service = self.notify_service.split(".", 1)

        message = (
            "⚠️ Пристрій недоступний!\n\n"
            f"• Назва: {name}\n"
            f"• Entity: {entity_id}"
        )

        await self.hass.services.async_call(
            domain,
            service,
            {
                "message": message,
            },
        )
