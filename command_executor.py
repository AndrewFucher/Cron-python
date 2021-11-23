import logging_messages

import os

from loguru import logger
from loguru._logger import Logger


def set_up_logger(logger_: Logger) -> None:
    global logger
    logger = logger_

#, file_path: str, lvl: str, fmt: str
def execute_command(command: str, logger_: Logger) -> None:
    # logger.add(sink=file_path, level=lvl, format=fmt, enqueue=True, backtrace=True)
    pid = os.getpid()
    logger_.info(logging_messages.EXECUTING_COMMAND.format(pid, command))
    result = os.system(command)
    logger_.info(
        logging_messages.FINISHED_EXECUTING_COMMAND_WITH_CODE.format(pid, result)
    )
    # sys.exit(result)
    # rr.complete()
    # os.kill(pid, signal.SIGTERM)
