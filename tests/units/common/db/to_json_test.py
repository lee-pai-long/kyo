

# pylint: disable=missing-module-docstring,missing-function-docstring


import json

import pytest


@pytest.mark.usefixtures("drop_dummy_table")
def test_to_json_returns_a_json_string_representing_the_model(dummy_instance):

    # Somehow I cannot test dummy_instance.to_json() against a literal
    # JSON string representation formateted like so:
    # '{"name": "{0}", "birthdate": "{1}"}'.format(
    #       dummy.name, dummy.birthdate.isoformat()
    #  )
    # It returns a KeyError: '"name"'
    assert dummy_instance.to_json() == json.dumps({
        "name": dummy_instance.name,
        "birthdate": dummy_instance.birthdate.isoformat()
    })
