"""The Nettiego component."""
import asyncio
import logging
import time
from datetime import timedelta
from math import ceil

import async_timeout
from aiohttp.client_exceptions import ClientConnectorError
from homeassistant.const import CONF_URL, CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    MAX_REQUESTS_PER_DAY,
)
from .nettiego import Client, Data, NamfError

PLATFORMS = ["air_quality", "weather"]

_LOGGER = logging.getLogger(__name__)


def set_update_interval(hass, instances):
    # We check how many Nettiego configured instances are and calculate interval to not exceed allowed numbers of requests.
    interval = timedelta(minutes=ceil(24 * 60 / MAX_REQUESTS_PER_DAY) * instances)

    if hass.data.get(DOMAIN):
        for instance in hass.data[DOMAIN].values():
            instance.update_interval = interval

    return interval


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    return True


async def async_setup_entry(hass, config_entry):
    uniqueId = config_entry.data[CONF_NAME]
    url = config_entry.data[CONF_URL]
    latitude = config_entry.data[CONF_LATITUDE]
    longitude = config_entry.data[CONF_LONGITUDE]

    # For backwards compat, set unique ID
    if config_entry.unique_id is None:
        hass.config_entries.async_update_entry(
            config_entry, unique_id=f"{uniqueId}"
        )

    websession = async_get_clientsession(hass)
    update_interval = set_update_interval(
        hass, len(hass.config_entries.async_entries(DOMAIN))
    )

    coordinator = NettiegoUpdateCoordinator(
        hass, websession, url, latitude, longitude, update_interval
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    set_update_interval(hass, len(hass.data[DOMAIN]))

    return unload_ok


class NettiegoUpdateCoordinator(DataUpdateCoordinator):
    INDEX_DATA = "data"
    INDEX_CONFIG = "config"

    def __init__(self, hass, session, url, latitude, longitude, update_interval):
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)
        self.latitude = latitude
        self.longitude = longitude
        self.client = Client(session, base_url=url)

    async def _async_update_data(self):
        """Update data via library."""
        data = {}
        with async_timeout.timeout(30):
            try:
                data[NettiegoUpdateCoordinator.INDEX_DATA] = await self._get_data()
                data[NettiegoUpdateCoordinator.INDEX_CONFIG] = await self._get_config()
            except (NamfError, ClientConnectorError) as error:
                raise UpdateFailed(error) from error
        return data

    async def _get_data(self, tries=3, timeout=5):
        with async_timeout.timeout(timeout * tries):
            last_error = None
            for x in range(tries):
                try:
                    return await self.client.get_data()
                except (NamfError, ClientConnectorError) as error:
                    last_error = error
                    _LOGGER.error(error)
                time.sleep(timeout / (tries + 1))
            raise UpdateFailed(last_error) from last_error

    async def _get_config(self, tries=3, timeout=5):
        with async_timeout.timeout(timeout * tries):
            last_error = None
            for x in range(tries):
                try:
                    return await self.client.get_config()
                except (NamfError, ClientConnectorError) as error:
                    last_error = error
                    _LOGGER.error(error)
                time.sleep(timeout/(tries+1))
            raise UpdateFailed(last_error) from last_error
