from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import dataclass_json

from constants import (
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_LOGGING_FILE_PATH,
    DEFAULT_LOGGING_LEVEL,
)


@dataclass_json
@dataclass
class CronConfiguration:
    LOGGING_LEVEL: str = field(default=DEFAULT_LOGGING_LEVEL)
    LOGGING_FILE_PATH: str = field(default=DEFAULT_LOGGING_FILE_PATH)
    LOGGING_FORMAT: str = field(default=DEFAULT_LOGGING_FORMAT)
    CRONTAB_FILE_PATH: str = field(default=None)
    # LOGGER_NAME: str = field(default="__main__")
    MAX_PROCESSES: int = field(default=1)
