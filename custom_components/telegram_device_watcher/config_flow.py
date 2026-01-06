from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import config_validation as cv
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, CONF_ENTITIES, CONF_NOTIFY_SERVICE


ALLOWED_DOMAINS = {
    "light",
    "switch",
    "binary_sensor",
    "sensor",
    "climate",
    "fan",
    "cover",
}


def is_real_device(entity_id: str) -> bool:
    return not entity_id.startswith((
        "sensor.home_assistant_",
        "sensor.supervisor_",
        "sensor.system_",
        "update.",
    ))


class TelegramDeviceWatcherConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            return self.async_create_entry(
                title="Telegram Device Watcher",
                data={
                    CONF_ENTITIES: user_input[CONF_ENTITIES],
                },
                options={
                    CONF_NOTIFY_SERVICE: user_input[CONF_NOTIFY_SERVICE],
                },
            )

        entity_reg = er.async_get(self.hass)

        entities = {
            e.entity_id: e.entity_id
            for e in entity_reg.entities.values()
            if (
                e.entity_id.split(".")[0] in ALLOWED_DOMAINS
                and is_real_device(e.entity_id)
            )
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ENTITIES): cv.multi_select(entities),
                vol.Required(
                    CONF_NOTIFY_SERVICE,
                    default="notify.telegram",
                ): str,
            }),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TelegramDeviceWatcherOptionsFlow(config_entry)


class TelegramDeviceWatcherOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)

        entity_reg = er.async_get(self.hass)

        entities = {
            e.entity_id: e.entity_id
            for e in entity_reg.entities.values()
            if (
                e.entity_id.split(".")[0] in ALLOWED_DOMAINS
                and is_real_device(e.entity_id)
            )
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_ENTITIES,
                    default=self._config_entry.data.get(CONF_ENTITIES, []),
                ): cv.multi_select(entities),
                vol.Required(
                    CONF_NOTIFY_SERVICE,
                    default=self._config_entry.options.get(
                        CONF_NOTIFY_SERVICE,
                        "notify.telegram",
                    ),
                ): str,
            }),
        )
