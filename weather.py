"""Support for Nettiego Namf sensor."""
import logging

from homeassistant.components.weather import (
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    WeatherEntity,
)
from homeassistant.const import CONF_NAME, TEMP_CELSIUS
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    COORDINATOR_INDEX_DATA,
    COORDINATOR_INDEX_CONFIG,
)

from .nettiego import Data, Config

ATTRIBUTION = "Data provided by Nettiego Air Monitor"

PARALLEL_UPDATES = 1

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    name = config_entry.data[CONF_NAME]

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([NettiegoWeather(coordinator, f"{name} Bosch BME280")], False)


def round_state(func):
    """Round state."""

    def _decorator(self):
        res = func(self)
        if isinstance(res, float):
            return round(res)
        return res

    return _decorator


class NettiegoWeather(CoordinatorEntity, WeatherEntity):
    """Implementation of a Nettiego Namf air quality sensor."""
    def __init__(self, coordinator, name):
        """Initialize."""
        super().__init__(coordinator)
        self._attrs = {}
        self._name = name
        self._icon = "mdi:weather-hail"

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def icon(self):
        """Return the icon."""
        return self._icon


    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.name}_{self.coordinator.data[COORDINATOR_INDEX_CONFIG][Config.ID]}_BME280"

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
    def condition(self):
        """Return the current condition."""
        return None

    @property
    def temperature(self):
        """Return the temperature."""
        return float(self.coordinator.data[COORDINATOR_INDEX_DATA][Data.TEMPERATURE])

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the pressure."""
        return float(self.coordinator.data[COORDINATOR_INDEX_DATA][Data.PRESSURE])

    @property
    def humidity(self):
        """Return the humidity."""
        return float(self.coordinator.data[COORDINATOR_INDEX_DATA][Data.HUMIDITY])
