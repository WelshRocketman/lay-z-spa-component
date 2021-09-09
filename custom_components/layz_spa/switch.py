"""Platform for switch integration."""
# import logging

# import awesomelights
# import voluptuous as vol

# import homeassistant.helpers.config_validation as cv
# # Import the device class from the component that you want to support
# from homeassistant.components.light import (
#     ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity)
# from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import logging
from homeassistant.helpers.config_validation import string
from homeassistant.const import STATE_OFF, STATE_ON, CONF_NAME
from typing import Optional
from homeassistant.components.switch import DEVICE_CLASS_SWITCH, SwitchEntity

from layz_spa.spa import Spa
from .const import CONF_DID, COORDINATOR, DOMAIN, HUB

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
#     vol.Required(CONF_HOST): cv.string,
#     vol.Optional(CONF_USERNAME, default='admin'): cv.string,
#     vol.Optional(CONF_PASSWORD): cv.string,
# })


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up a config entry."""
    title = hass.data[DOMAIN][entry.entry_id][CONF_NAME]
    deviceid = hass.data[DOMAIN][entry.entry_id][CONF_DID]
    spa = hass.data[DOMAIN][entry.entry_id][HUB]
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    switchables = {
        "power": spa.set_power,
        "heat_power": spa.set_heat_power,
        "wave_power": spa.set_wave_power,
        "filter_power": spa.set_filter_power,
    }
    for switch_attr, function in switchables.items():
        heater = SpaSwitch(spa, title, switch_attr, function)
        async_add_devices([heater])


class SpaSwitch(SwitchEntity):
    """Representation of an Awesome Light."""

    def __init__(
        self,
        spa: Spa,
        title: string,
        attr: string,
        function,
    ):
        """Initialize an AwesomeLight."""
        switch_name = attr.replace("_", " ")
        self._name = f"{title} {switch_name.title()}"
        _LOGGER.warning("setup %s", self._name)
        self._spa = spa
        self._attr_name = attr
        self._switch_func = function
        self._state = getattr(self._spa, self._attr_name)

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    async def async_update(self):
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = getattr(self._spa, self._attr_name)

    async def async_turn_on(self):
        """Turn filter on."""
        await self._switch_func(True)

    async def async_turn_off(self):
        """Turn filter on."""
        await self._switch_func(False)
