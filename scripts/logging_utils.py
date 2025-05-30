"""
Logging utilities for FMGPT.
Provides setup and event logging functions for consistent logging across the project.
"""
import logging
import os
from typing import Any

def setup_logging(log_file: str = "logs/fmgpt.log") -> None:
    """
    Set up logging to file and console.
    :param log_file: Path to the log file.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def log_event(message: str, level: str = "info", extra: Any = None) -> None:
    """
    Log an event with the specified level.
    :param message: The log message.
    :param level: Log level (info, warning, error, debug).
    :param extra: Additional info to log.
    """
    logger = logging.getLogger()
    if extra:
        message = f"{message} | Extra: {extra}"
    level = level.lower()
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "debug":
        logger.debug(message)
    else:
        logger.info(message)
