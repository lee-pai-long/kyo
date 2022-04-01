"""DB fixtures."""
# pylint: disable=redefined-outer-name
#       In a classical code this warning is legit but pytest
#       allow the usage of fixture as function arguments,
#       see: https://goo.gl/xX21g9

import pytest
from inflection import singularize

import sqlalchemy as sql

from app.common import db


@pytest.fixture(scope="session")
def dummy():
    """Compute base Dummy model."""

    class Dummy(db.Model):  # pylint: disable=missing-docstring,too-few-public-methods
        id = sql.Column(sql.Integer, primary_key=True)
        name = sql.Column(sql.String(80), nullable=False)
    db.Model.metadata.tables['Dummies'].create()

    yield Dummy

    # Teardown
    db.Model.metadata.tables['Dummies'].drop()


@pytest.fixture(scope="session", autouse=True)
def database(request):
    """Drop db at end of function."""
    # In case migration as not been run.
    db.Model.metadata.create_all()

    yield True

    if not request.config.getoption("--no-teardown"):
        with db.session() as session:
            for table in reversed(db.Model.metadata.sorted_tables):
                model_name = singularize(table.name)
                if 'Dummy' not in model_name:
                    model = getattr(db, model_name)
                    if not model._is_view:  # pylint: disable=protected-access
                        session.query(model).delete()
            session.execute("SET FOREIGN_KEY_CHECKS=1")
            session.commit()
