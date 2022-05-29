"""DB fixtures."""
# pylint: disable=redefined-outer-name
#       In a classical code this warning is legit but pytest
#       allow the usage of fixture as function arguments,
#       see: https://goo.gl/xX21g9
# pylint: disable=missing-function-docstring

import datetime

import pytest

import sqlalchemy as sql

from app.common import db


# This fixture is useful to fix a bug we had, where all the test failed because
# sqlalchemy and/or sqlite was returning that the table Dummies already existed
# when the dummy_class fixture was trying to create it.
# But when we look in the DB, the table wasn't there. So this is either a
# sqlalchemy and/or sqlite cache thing or I don't know what is going on here.
# But forcing the drop of the table at the beginning of each test sessions
# seems to work. Go figures, sometime you just need to have faith.
@pytest.fixture(scope="session")
def drop_dummy_table():

    with db.session() as session:
        session.execute("DROP TABLE IF EXISTS Dummies")
        session.commit()


@pytest.fixture(scope="session")
def dummy_class():

    class Dummy(db.Model):  # pylint: disable=missing-docstring,too-few-public-methods
        id = sql.Column(sql.Integer, primary_key=True)
        name = sql.Column(sql.String(80), nullable=False)
        birthdate = sql.Column(sql.Date, nullable=True)
    db.Model.metadata.tables['Dummies'].create()

    yield Dummy

    db.Model.metadata.tables['Dummies'].drop()


@pytest.fixture(scope="session")
def model_with_date(dummy_class):
    return dummy_class


@pytest.fixture(scope="session")
def model_with_datetime():

    class Order(db.Model):  # pylint: disable=missing-docstring,too-few-public-methods
        id = sql.Column(sql.Integer, primary_key=True)
        username = sql.Column(sql.String(80), nullable=False)
        order_datetime = sql.Column(sql.DateTime, nullable=True)
    db.Model.metadata.tables['Orders'].create()

    yield Order

    db.Model.metadata.tables['Orders'].drop()


@pytest.fixture(scope="function")
def dummy_instance(dummy_class):

    return dummy_class(name='Jon', birthdate=datetime.date(1986, 4, 4))
