"""Support for Nettiego Namf sensor."""
import logging

from homeassistant.components.air_quality import (
    ATTR_PM_2_5,
    ATTR_PM_10,
    AirQualityEntity,
)

from homeassistant.const import CONF_NAME
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_API_PM10,
    ATTR_API_PM25,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    COORDINATOR_INDEX_DATA, COORDINATOR_INDEX_CONFIG)

from .nettiego import Data, Config

ATTRIBUTION = "Data provided by Nettiego Air Monitor"

PARALLEL_UPDATES = 1

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data[CONF_NAME]

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([NettiegoAirQuality(coordinator, f"{name} NovaFitness SDS011")], False)


def round_state(func):
    """Round state."""

    def _decorator(self):
        res = func(self)
        if isinstance(res, float):
            return round(res)
        return res

    return _decorator


class NettiegoAirQuality(CoordinatorEntity, AirQualityEntity):
    """Implementation of a Nettiego Namf air quality sensor."""
    def __init__(self, coordinator, name):
        """Initialize."""
        super().__init__(coordinator)
        self._name = name
        self._icon = "mdi:blur"

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    @property
    @round_state
    def particulate_matter_2_5(self):
        _LOGGER.debug('coordinator data', self.coordinator.data)
        """Return the particulate matter 2.5 level."""
        return self.coordinator.data[COORDINATOR_INDEX_DATA][Data.PM25]

    @property
    @round_state
    def particulate_matter_10(self):
        """Return the particulate matter 10 level."""
        return self.coordinator.data[COORDINATOR_INDEX_DATA][Data.PM10]

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.name}_{self.coordinator.data[COORDINATOR_INDEX_CONFIG][Config.ID]}_SDS011"

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self.coordinator.data[COORDINATOR_INDEX_CONFIG][Config.ID])
            },
            "model": self.coordinator.data[COORDINATOR_INDEX_CONFIG][Config.ID],
            "name": self.coordinator.data[COORDINATOR_INDEX_CONFIG][Config.ID],
            "manufacturer": MANUFACTURER,
            "entry_type": "service",
            "sw_version": self.coordinator.data[COORDINATOR_INDEX_CONFIG][Config.SOFTWARE_VERSION]
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {}