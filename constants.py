from datetime import datetime
import logging


# Default logging configuration
DEFAULT_LOGGING_LEVEL = logging.getLevelName(logging.INFO)
DEFAULT_LOGGING_FILE_NAME_DATE_FORMAT = "%d%m%Y"
DEFAULT_LOGGING_FORMAT = "%(asctime)s:%(name)s:%(levelname)s:\t%(message)s"
DEFAULT_LOGGING_FILE_PATH = f"./logs/log{datetime.now().date().strftime(DEFAULT_LOGGING_FILE_NAME_DATE_FORMAT)}.log"

# Configuration file path
CONFIGURATION_FILE_PATH = "./configuration.json"
