
# pylint: disable=missing-module-docstring,missing-function-docstring


import sqlalchemy as sql

from app.common import db


def test_repr_allow_to_easily_recreate_model_objects():

    # pylint: disable=too-few-public-methods,missing-class-docstring
    class ReprDummy(db.Model):

        id = sql.Column(sql.Integer, primary_key=True)
        firstname = sql.Column(sql.String(80))
        lastname = sql.Column(sql.String(80))
        age = sql.Column(sql.Integer)

    dummy = ReprDummy(firstname='John', lastname='Doe', age=35)

    expected_repr = "ReprDummy(age=35, firstname='John', lastname='Doe')"
    assert dummy.__repr__() == expected_repr
