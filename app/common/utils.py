"""app helpers modules.

:contains:
    - log_handler: To create a log handler to attach to our app.
    - db_session: Generate a database session.
"""

# Standard.
import logging
# Importing only logging don't give access to handlers module...
# because the handlers module isn't exported in logging/__init__.py.
# see:
# - https://github.com/python/cpython/tree/master/Lib/logging
# - https://github.com/python/cpython/blob/master/Lib/logging/__init__.py
from logging.handlers import WatchedFileHandler
import os

# Internal.
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
    # Create log handler.
    handler = WatchedFileHandler(os.path.join(
        Config.LOG_DIRECTORY,
        "{filename}.log".format(filename=filename)
    ))

    # Set handler's name.
    handler.name = name or filename

    # Set log level.
    handler.setLevel(Config.LOG_LEVEL)

    # Add formatter.
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)-8s "
        "| (%(process)d) [%(thread)d] "
        "%(module)s.%(funcName)s:%(lineno)d -> %(message)s"
    ))

    # Return handler object.
    return handler
