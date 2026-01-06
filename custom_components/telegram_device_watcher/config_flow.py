from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er
import voluptuous as vol

from .const import DOMAIN, CONF_ENTITIES


class TelegramDeviceWatcherConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        # Якщо користувач вже вибрав entity → зберігаємо
        if user_input is not None:
            return self.async_create_entry(
                title="Telegram Device Watcher",
                data={
                    CONF_ENTITIES: user_input[CONF_ENTITIES],
                },
            )

        # Отримуємо всі entity з registry
        entity_reg = er.async_get(self.hass)

        entities = {
            e.entity_id: (
                f"{e.entity_id}"
                + (f" ({e.original_name})" if e.original_name else "")
            )
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
