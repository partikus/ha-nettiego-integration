"""Constants for Nettiego Air Monitor - NAMF integration."""
ATTR_API_HUMIDITY = "humidity"
ATTR_API_PM10 = "pm10"
ATTR_API_PM25 = "pm25"
ATTR_API_PRESSURE = "pressure"
ATTR_API_TEMPERATURE = "temperature"
DEFAULT_NAME = "Nettiego Air Monitor"
DOMAIN = "nettiego"
MAX_REQUESTS_PER_DAY = 24 * 12 # 24h * every 5 minutes
NO_SENSORS = "There are no Nettiego sensors in this host yet."
MANUFACTURER="Nettiego"


COORDINATOR_INDEX_DATA = "data"
COORDINATOR_INDEX_CONFIG = "config"
