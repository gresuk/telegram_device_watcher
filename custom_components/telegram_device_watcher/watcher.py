from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_event

from .const import CONF_ENTITIES, STATE_OFFLINE


class TelegramDeviceWatcher:
    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.entities = set(entry.data[CONF_ENTITIES])
        self._offline = set()
        self._unsub = None

    async def async_start(self):
        self._unsub = async_track_event(
            self.hass,
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

        if entity_id not in self.entities or not new_state:
            return

        state = new_state.state
        name = new_state.name or entity_id

        if state not in STATE_OFFLINE:
            self._offline.discard(entity_id)
            return

        if entity_id in self._offline:
            return

        self._offline.add(entity_id)

        self.hass.async_create_task(
            self._send_telegram(name, entity_id)
        )

    async def _send_telegram(self, name, entity_id):
        await self.hass.services.async_call(
            "telegram_bot",
            "send_message",
            {
                "message": (
                    "⚠️ *Пристрій недоступний!*\n\n"
                    f"• *Назва:* {name}\n"
                    f"• *Entity:* `{entity_id}`"
                ),
                "parse_mode": "markdown",
            },
        )

