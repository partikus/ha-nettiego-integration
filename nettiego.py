"""
Python wrapper for getting interaction with Tech devices.
"""
import logging
import json

import aiohttp

_LOGGER = logging.getLogger(__name__)

class Client:
    """Main class to perform Tech API requests"""

    def __init__(self, session: aiohttp.ClientSession, base_url):
        _LOGGER.debug("Init NAMF")
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }
        self.base_url = base_url
        self.session = session

    async def get(self, request_path):
        url = self.base_url + request_path
        _LOGGER.debug("Sending GET request: " + url)
        async with self.session.get(url, headers=self.headers) as response:
            _LOGGER.debug(response)
            if response.status != 200:
                _LOGGER.warning("Invalid response from NAMF api: %s", response.status)
                raise NamfError(response.status, await response.text())
            return await response.json(content_type=None)

    async def get_data(self):
        path = "/data.json"
        result = await self.get(path)
        _LOGGER.debug('get_data:result')
        _LOGGER.debug(result)
        return Data(result)

    async def get_config(self):
        path = "/config.json"
        result = await self.get(path)
        return result

    async def exists(self):
        try:
            await self.get_config()
        except NamfError:
            return False
        return True


class NamfError(Exception):
    """Raised when NAMF api request ended in error.
    Attributes:
        status_code - error code returned by NAMF
        status - more detailed description
    """

    def __init__(self, status_code, status):
        self.status_code = status_code
        self.status = status


class _DictToObj(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)
    def __setitem__(self, key, item):
        self[key] = item

class Config(_DictToObj):
    SOFTWARE_VERSION = "SOFTWARE_VERSION"
    ID = "fs_ssid"

    CONFIG_TYPES = [
        SOFTWARE_VERSION,
        ID,
    ]

    def __init__(self, data: dict):
        super().__init__(data)
        for t in Config.CONFIG_TYPES:
            self.__setattr__(t.lower(), data[t] if t in data else None)

class Data(_DictToObj):
    """Measurement for specific time period returned from Nettiego API"""
    # http://{base_url}/data.json
    PM25 = "SDS_P2"
    PM10 = "SDS_P1"
    TEMPERATURE = "BME280_temperature"
    HUMIDITY = "BME280_humidity"
    PRESSURE = "BME280_pressure"

    MEASUREMENTS_TYPES = [
        PM25,
        PM10,
        TEMPERATURE,
        HUMIDITY,
        PRESSURE,
    ]

    def __init__(self, data: dict = {}):
        super().__init__(data)
        # Parse date-times
        # Make popular measurements available directly,
        # i.e. instead of x.sensordatavalues['SDS_P2'] make it accessible as x.pm25
        values = {
            x['value_type']: x['value'] for x in
            data['sensordatavalues']} if 'sensordatavalues' in data else {}
        for t in Data.MEASUREMENTS_TYPES:
            self.__setattr__(t.lower(), values[t] if t in values else None)
            self.__setattr__(t, values[t] if t in values else None)
        self.update(values)
