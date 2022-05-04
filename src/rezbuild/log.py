"""Setup logger.

Accept two environments REZBUILD_LOG_LEVEL, REZBUILD_LOG_FILE to control the
log level and log file path.

REZBUILD_LOG_FILE: Path of the log file.
REZBUILD_LOG_LEVEL: One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
"""

# Import built-in modules
import logging
import os

# Import third-party modules
from rezbuild.constants import PACKAGE_NAME


LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def get_env_log_level():
    """Get the log level setting by environments.

    Return the log level setting by REZBUILD_LOG_LEVEL. Otherwise return int 0.
    """
    env_log_level = os.getenv("REZBUILD_LOG_LEVEL")
    if env_log_level and env_log_level.upper() in LOG_LEVELS:
        return getattr(logging, env_log_level.upper())
    else:
        return 0


def get_handler():
    """Get the log handler.

    Return a FileHandler if REZBUILD_LOG_FILE is setting. Otherwise return a
    StreamHandler.
    """
    if os.getenv("REZBUILD_LOG_FILE"):
        handler = logging.FileHandler(os.getenv("REZBUILD_LOG_FILE"))
    else:
        handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    return handler


def init_logger(level=None):
    """Get rezbuild logger.

    Args:
        level (int, optional): Logging level to show. Choice from one of
            logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
            logging.CRITICAL. Default is logging.WARNING.
    """
    level = level or get_env_log_level() or logging.WARNING
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = get_handler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(PACKAGE_NAME)
    logger.setLevel(level)
    logger.addHandler(handler)
    root = os.path.abspath(os.path.dirname(__file__))
    logger.debug(f"Package root: {root}")
