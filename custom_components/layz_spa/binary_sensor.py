"""Platform for switch integration."""

# Import reqired components
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import logging
from homeassistant.helpers.config_validation import string
from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_NAME, CONF_NAME
from typing import Optional

# from homeassistant.components.sensor import PLATFORM_SCHEMA


from layz_spa.spa import Spa
from .const import CONF_DID, COORDINATOR, DOMAIN, HUB

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up a config entry."""
    title = hass.data[DOMAIN][entry.entry_id][CONF_NAME]
    deviceid = hass.data[DOMAIN][entry.entry_id][CONF_DID]
    spa = hass.data[DOMAIN][entry.entry_id][HUB]
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    # dictionary of switches we want to manage from the layzspa component
    # sensorlist = {
    #    "heater_on": spa.heat_temp_reach,
    # }
    # create switches for power, heat, wave and filter
    # for sensor_attr, function in sensorlist.items():
    #    heater = SpaSensor(spa, title, "heater_on", function, deviceid)
    #    async_add_devices([heater])
    heater1 = SpaSensor(spa, title, "heater_at_temp", deviceid)
    async_add_devices([heater1])
    heater2 = SpaSensor(spa, title, "is_heating", deviceid)
    async_add_devices([heater2])


class SpaSensor(BinarySensorEntity):
    """Representation of LayZSpa Sensor"""

    def __init__(self, spa: Spa, title: string, attr: string, devid):
        """Initialize an LayZSpa Sensor."""
        sensor_name = attr.replace("_", " ")
        self._name = f"{title} {sensor_name.title()}"
        self._spa = spa
        self._attr_name = attr
        self._state = 0
        # self._sensor_func = function
        _LOGGER.warning("Updating %s", self._name)
        if self._attr_name == "heater_at_temp":
            self._state = getattr(self._spa, "heat_temp_reach")
        elif self._attr_name == "is_heating":
            heater_power = getattr(self._spa, "heat_power")
            if heater_power == 1:
                self._state = not getattr(self._spa, "heat_temp_reach")
            else:
                self._state = 0
        # self._state = getattr(self._spa, "heat_temp_reach")
        self._lastupdate = getattr(self._spa, "updated_at")
        self._available = True

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self._name

    async def async_update(self):
        """Fetch new state data for this sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        # capture the last update timestamp from the spa
        current_update = getattr(self._spa, "updated_at")
        # if the last update timestamps from the spa and the value from the previous update are different
        # then we can assume we have a newer value and can update. This should esnure that the latest switch
        # status is recieved from the spa itself and not just the stored value.
        if current_update > self._lastupdate:
            _LOGGER.warning("Updating %s", self._name)
            if self._attr_name == "heat_temp_reach":
                self._state = getattr(self._spa, "heat_temp_reach")
            elif self._attr_name == "is_heating":
                heater_power = getattr(self._spa, "heat_power")
                if heater_power == 1:
                    self._state = not getattr(self._spa, "heat_temp_reach")
                else:
                    self._state = 0
            self._lastupdate = current_update
        # retain the lastupdate timestamp for next time.
