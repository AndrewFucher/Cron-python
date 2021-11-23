from datetime import datetime
import sys
import threading
from typing import Any

from croniter import croniter
from crontab import CronTab

import command_executor

import logging_messages

from loguru import logger

import os

from constants import (
    CONFIGURATION_FILE_PATH,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_LOGGING_FILE_PATH,
    DEFAULT_LOGGING_LEVEL,
)
from cron_configuration import CronConfiguration

configuration: CronConfiguration = CronConfiguration()


def set_default_logging_config() -> None:
    os.makedirs(os.path.dirname(DEFAULT_LOGGING_FILE_PATH), exist_ok=True)

    logger.add(
        format=DEFAULT_LOGGING_FORMAT,
        sink=DEFAULT_LOGGING_FILE_PATH,
        level=DEFAULT_LOGGING_LEVEL,
        enqueue=True,
        backtrace=True,
    )

    logger.info(logging_messages.DEFAULT_LOGGING_CONFIG_HAS_BEEN_SET)


def set_loggin_config(
    fmt: str = configuration.LOGGING_FORMAT,
    file_path: str = configuration.LOGGING_FILE_PATH,
    lvl: str = configuration.LOGGING_LEVEL,
) -> None:
    global logger
    logger.remove()
    logger.add(
        format=DEFAULT_LOGGING_FORMAT,
        sink=DEFAULT_LOGGING_FILE_PATH,
        level=DEFAULT_LOGGING_LEVEL,
        enqueue=True,
        backtrace=True,
    )


def set_config(config_file_path: str = CONFIGURATION_FILE_PATH) -> None:
    logger.info(logging_messages.STARTING_SETTING_CONFIGURATION)
    is_any_error_came_up = True
    try:
        global configuration
        with open(config_file_path, "r") as conf_file:
            configuration = CronConfiguration.from_json(conf_file.read())
        logger.info(logging_messages.ENDED_SETTING_CONFIGURATION)
        is_any_error_came_up = False
    except FileNotFoundError as exc:
        logger.warning(logging_messages.NO_FILE_FOUND.format(config_file_path))
    except PermissionError as exc:
        logger.warning(logging_messages.PERMISSION_ERROR.format(config_file_path))
    except IOError as exc:
        logger.warning(logging_messages.IO_ERROR.format(exc.errno, exc.strerror))
    except Exception as exc:
        logger.warning(logging_messages.UNKNOWN_ERROR)
    finally:
        if is_any_error_came_up:
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


def iter_over_cron_jobs(cron_jobs: "list[list[Any]]") -> "list[list[Any]]":
    try:
        commands_to_execute = []
        datetime_now = datetime.now().timestamp()
        for cron_job_numer in range(len(cron_jobs)):
            if cron_jobs[cron_job_numer][0].get_current() < datetime_now:
                cron_jobs[cron_job_numer][0].get_next()
                commands_to_execute.append(str(cron_jobs[cron_job_numer][1]))
        if len(commands_to_execute) > 0:
            for c in commands_to_execute:
                threading.Thread(target=command_executor.execute_command, args=(c,logger,)).start()

    except Exception as exc:
        logger.exception(logging_messages.UNKNOWN_ERROR)
        sys.exit(1)

    return cron_jobs





def parse_crontab_to_cron_jobs(
    crontab: CronTab, start_time: datetime
) -> "list[list[Any]]":
    return [
        (
            croniter(
                str(cron_job.slices), start_time.timestamp(), float, True, None, True
            ),
            cron_job.command,
        )
        for cron_job in crontab
    ]


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

    cron_jobs = parse_crontab_to_cron_jobs(crontab, datetime.now())

    while True:
        cron_jobs = iter_over_cron_jobs(cron_jobs)


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
