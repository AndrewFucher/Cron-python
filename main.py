from datetime import datetime
import sys
import signal

from croniter import croniter
from crontab import CronItem, CronTab

import logging_messages

from multiprocessing import Process

import logging
import os

from constants import (
    CONFIGURATION_FILE_PATH,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_LOGGING_FILE_PATH,
    DEFAULT_LOGGING_LEVEL,
)
from cron_configuration import CronConfiguration

logger: logging.Logger = logging.getLogger(__name__)
configuration: CronConfiguration = CronConfiguration()


def set_default_logging_config() -> None:
    os.makedirs(os.path.dirname(DEFAULT_LOGGING_FILE_PATH), exist_ok=True)
    
    logging.basicConfig(
        format=DEFAULT_LOGGING_FORMAT,
        filename=DEFAULT_LOGGING_FILE_PATH,
        level=DEFAULT_LOGGING_LEVEL,
    )

    logging.info(logging_messages.DEFAULT_LOGGING_CONFIG_HAS_BEEN_SET)


def set_loggin_config(
    fmt: str = configuration.LOGGING_FORMAT,
    file_path: str = configuration.LOGGING_FILE_PATH,
    lvl: str = logging.getLevelName(configuration.LOGGING_LEVEL),
) -> None:
    logging.basicConfig(format=fmt, filename=file_path, level=lvl, force=True)


def set_config(config_file_path: str = CONFIGURATION_FILE_PATH) -> None:
    logger.info(logging_messages.STARTING_SETTING_CONFIGURATION)

    try:
        global configuration
        with open(config_file_path, "r") as conf_file:
            configuration = CronConfiguration.from_json(conf_file.read())
        logger.info(logging_messages.ENDED_SETTING_CONFIGURATION)
        return
    except FileNotFoundError as exc:
        logger.warning(logging_messages.NO_FILE_FOUND.format(config_file_path))
    except PermissionError as exc:
        logger.warning(logging_messages.PERMISSION_ERROR.format(config_file_path))
    except IOError as exc:
        logger.warning(logging_messages.IO_ERROR.format(exc.errno, exc.strerror))
    except Exception as exc:
        logger.warning(logging_messages.UNKNOWN_ERROR)
    finally:
        logger.info(logging_messages.USING_DEFAULT_CONFIGURATION)

    logger.info(logging_messages.ENDED_SETTING_CONFIGURATION)


def get_crontab(crontab_file_path: str) -> CronTab:
    logger.info(logging_messages.STARTING_PARSING_CRONTAB)

    if not crontab_file_path:
        logger.error(logging_messages.CRONTAB_FILE_PATH_NOT_SPECIFIED)
        return None
    if not os.path.isfile(crontab_file_path):
        logger.error(
            logging_messages.NOT_CRONTAB_FILE_EXISTS_BY_PATH.format(crontab_file_path)
        )
        return None

    crontab: CronTab = None
    try:
        crontab = CronTab(tabfile=crontab_file_path)
    except Exception as exc:
        logger.exception(logging_messages.UNKNOWN_ERROR)

    logger.info(logging_messages.ENDED_PARSING_CRONTAB)
    return crontab


def iter_over_crontab(crontab: CronTab) -> None:
    cron_job: CronItem = None
    datetime_now = datetime.now()
    for cron_job in crontab:
        # croniter.get_next(croniter(cron_job.slices.render()))
        if croniter.match(cron_job.slices.render(), datetime_now):
            subprocess = Process(target=execute_command, args=(cron_job.command))
            subprocess.start()


def execute_command(command: str) -> None:
    pid = os.getpid()
    logger.info(logging_messages.EXECUTING_COMMAND.format(pid, command))
    result = os.system(command)
    logger.info(
        logging_messages.FINISHED_EXECUTING_COMMAND_WITH_CODE.format(pid, result)
    )
    # sys.exit(result)
    os.kill(pid, signal.SIGTERM)


def init() -> None:
    logger.info(logging_messages.STARTING_INITIALIZATION)

    set_default_logging_config()

    logger.info(logging_messages.ENDED_INITIALIZATION)


def set_up() -> None:
    logger.info(logging_messages.STARTING_SET_UP)

    set_config()
    set_loggin_config()

    logger.info(logging_messages.ENDED_SET_UP)


def workflow(crontab: CronTab) -> None:
    if not crontab:
        raise ValueError(logging_messages.CRONTAB_FILE_IS_NONE_ERROR)

    logger.info(logging_messages.STARTING_WORKFLOW)

    while True:
        iter_over_crontab(crontab)


if __name__ == "__main__":
    init()
    set_up()
    crontab: CronTab = get_crontab(configuration.CRONTAB_FILE_PATH)
    if not crontab:
        logger.info(logging_messages.FINISHING_CRON)
        sys.exit(1)
    try:
        workflow(crontab)
    except Exception as exc:
        logger.exception(logging_messages.UNKNOWN_ERROR)
        sys.exit(1)
