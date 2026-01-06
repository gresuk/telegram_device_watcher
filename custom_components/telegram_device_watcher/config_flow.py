from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er
import voluptuous as vol

from .const import DOMAIN, CONF_ENTITIES


class TelegramDeviceWatcherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Telegram Device Watcher",
                data=user_input,
            )

        entity_reg = er.async_get(self.hass)

        entities = {
            e.entity_id: f"{e.entity_id} ({e.original_name or e.entity_id})"
            for e in entity_reg.entities.values()
            if not e.disabled
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ENTITIES): vol.MultiSelect(entities)
                }
            ),
        )

