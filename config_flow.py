"""Adds config flow for Nettiego."""
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_URL, CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import aiohttp_client

from .nettiego import Client, NamfError

from .const import (  # pylint:disable=unused-import
    DEFAULT_NAME,
    DOMAIN,
)

class NettiegoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        websession = async_get_clientsession(self.hass)

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_NAME]}"
            )

            self._abort_if_unique_id_configured()
            url_valid = await self._test_url(websession, user_input[CONF_URL])

            if not url_valid:
                self._errors["base"] = "invalid_url"

            if not self._errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self._show_config_form(
            name=DEFAULT_NAME,
            url="",
            latitude=self.hass.config.latitude,
            longitude=self.hass.config.longitude,
        )

    def _show_config_form(self, name=None, url=None, latitude=None, longitude=None):
        """Show the configuration form to edit data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL, default=url): str,
                    vol.Optional(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Optional(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                    vol.Optional(CONF_NAME, default=name): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_url(self, client, url):
        """Return true if api_key is valid."""

        with async_timeout.timeout(10):
            websession = async_get_clientsession(self.hass)
            client = Client(websession, base_url=url)
            try:
                await client.exists()
            except NamfError:
                return False
            return True
