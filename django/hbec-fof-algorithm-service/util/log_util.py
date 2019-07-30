import logging

from util.sys_constants import LOGGER_NAME


def get_sys_log():
    return logging.getLogger(LOGGER_NAME)
