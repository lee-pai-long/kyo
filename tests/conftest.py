"""Fixtures."""
# pylint: disable=wildcard-import, unused-wildcard-import,missing-docstring
#         We need to import with wildcard
#         to inject the names in the current scope
#         without having to list every fixtures and helpers
#         individually.

from tests.fixtures.api import *
from tests.fixtures.db import *
from tests.fixtures.utils import *

opts = [
    {
        'flags': ['--no-teardown'],
        'options': {
            'help': 'Execute db teardown or not',
            'action': 'store_true',
            'default': False,
        }
    }
]


def pytest_addoption(parser):
    for opt in opts:
        parser.addoption(*opt['flags'], **opt['options'])
