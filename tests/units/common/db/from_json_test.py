
# pylint: disable=missing-module-docstring,missing-function-docstring

import pytest

from app.common import errors as err


def test_from_json_raises_when_it_cant_decode_given_json(dummy_class):

    dummy = '{"name": "Jon", "birthdate": "1986-04-04"'

    with pytest.raises(err.UnableToCreateModelFromJSON):
        dummy_class.from_json(dummy)

