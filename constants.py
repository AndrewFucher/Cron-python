from datetime import datetime
import logging


# Default logging configuration
DEFAULT_LOGGING_LEVEL = logging.getLevelName(logging.INFO)
DEFAULT_LOGGING_FILE_NAME_DATE_FORMAT = "YYYYMMDD"
DEFAULT_LOGGING_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSSSSS}:{function}:{name}:{process}:{level}:\t{message}"
DEFAULT_LOGGING_FILE_PATH = f"./logs/log{{time:{DEFAULT_LOGGING_FILE_NAME_DATE_FORMAT}}}.log"

# Configuration file path
CONFIGURATION_FILE_PATH = "./configuration.json"
