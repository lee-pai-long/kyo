
# pylint: disable=missing-module-docstring,missing-function-docstring


import pytest


@pytest.mark.usefixtures("drop_dummy_table")
def test_to_dict_returns_a_dict_representation_of_the_model(dummy_instance):

    assert dummy_instance.to_dict() == {
        'name': dummy_instance.name,
        'birthdate': dummy_instance.birthdate
    }
