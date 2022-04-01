"""Api fixtures."""
# pylint: disable=redefined-outer-name
#       In a classical code this warning is legit but pytest
#       allow the usage of fixture as function arguments,
#       see: https://goo.gl/xX21g9

from socket import getfqdn

import pytest

from app.api import create_app


@pytest.fixture(scope="session")
def app():
    """Flask app."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture(scope="module")
def base_url():
    """Define base request url."""
    return "{proto}://{fqdn}:{port}/{prefix}".format(
        proto='https',
        fqdn=getfqdn(),
        port=5000,
        prefix='api/v1'
    )
