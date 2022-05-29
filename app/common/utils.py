"""app helpers modules."""

import logging
import os

# Importing only logging don't give access to handlers module...
# because the handlers module isn't exported in logging/__init__.py.
# see:
# - https://github.com/python/cpython/tree/master/Lib/logging
# - https://github.com/python/cpython/blob/master/Lib/logging/__init__.py
from logging.handlers import WatchedFileHandler
from dateutil.parser import parse


from app.common.config import Config


def log_handler(filename, name=None):
    """Create a log handler to attach to our app.

    The classic FileHandler class keep track of the inode not the
    filename, therefore if the log rotation is by log rotate, the
    logs would still be written in the same file, ex: api.log.1.
    Using WatchedFileHandler allow us to handle log rotation outside
    our application.
    Rotation must be handle externally (like with logrotate).

    Log directory and log level are respectively set in
    Config.LOG_DIRECTORY and Config.LOG_LEVEL.

    :parameters:
        - filename (str): The log filename.
        - name (str): Handler's name(default: filename).

    :returns:
        - handler(logging.handlers.WatchedFileHandler)
    """
    handler = WatchedFileHandler(os.path.join(
        Config.LOG_DIRECTORY, f"{filename}.log"
    ))

    handler.name = name or filename

    handler.setLevel(Config.LOG_LEVEL)

    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)-8s "
        "| %(module)s.%(funcName)s:%(lineno)d -> %(message)s"
    ))

    return handler


def is_date(date_string, fuzzy=False):
    """Return whether the string can be interpreted as a date.

    Based on the following stack overflow answer:
    https://stackoverflow.com/a/25341965/3775614

    :parameters:
        - date_string (str): string to check for date
        - fuzzy (bool): ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
    except ValueError:
        return False
    return True
