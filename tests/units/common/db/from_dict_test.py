
# pylint: disable=missing-module-docstring,missing-function-docstring

import pytest


@pytest.mark.usefixtures("drop_dummy_table")
@pytest.mark.parametrize(
    "model, dummy_dict,format",
    [
        (
            model_with_date,
            {'name': 'Jon', 'birthdate': "1986-04-04"},
            "%Y-%m-%d"
        ),
        (
            model_with_datetime,
            {'name': 'Jon', 'birthdate': "1986-04-04T00:00:00"},
            "%Y-%m-%dT%H:%M:%S"
        )

    ]
)
def test_from_dict_returns_an_object_based_on_the_given_dict_attributes(
    model, dummy_class, dummy_dict, format
):

    dummy_instance = dummy_class.from_dict(dummy_dict)

    assert dummy_instance.name == dummy_dict['name']
    assert dummy_instance.birthdate.strftime(
        format=format
    ) == dummy_dict['birthdate']

