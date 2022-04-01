"""Utils fixtures."""
# pylint: disable=redefined-outer-name
#       In a classical code this warning is legit but pytest
#       allow the usage of fixture as function arguments,
#       see: https://goo.gl/xX21g9

import random as rd

import pytest

from app.common.config import Config


@pytest.fixture(scope='session')
def config():
    """Return a Config object."""
    return Config
