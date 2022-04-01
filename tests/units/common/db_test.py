"""Unit tests for app models declaration."""

from uuid import uuid4 as uuid
from datetime import datetime as dt

import pytest
import sqlalchemy as sql

from app.common import db, errors as err


class TestSave:

    def test_insert(self, dummy):

        name = "dummy {uuid}".format(uuid=uuid().int)

        saved_dummy = dummy(name=name).save()

        with db.session() as session:
            fetched_dummy = session.execute(
                "SELECT * FROM Dummies WHERE id = {}".format(saved_dummy.id)
            ).fetchone()
        assert fetched_dummy.name == name

    def test_update(self, dummy):

        original_name = "dummy {uuid}".format(uuid=uuid().int)
        with db.session() as session:
            inserted_id = session.execute(
                "INSERT INTO Dummies (name) VALUES ('{}')".format(original_name)
            ).lastrowid
            session.commit()

        updated_dummy = dummy(id=inserted_id)
        updated_dummy.name = "dummy {uuid}".format(uuid=uuid().int)
        updated_dummy.save()

        assert updated_dummy.id == inserted_id
        with db.session() as session:
            fetched_dummy = session.execute(
                "SELECT * FROM Dummies WHERE id = {}".format(updated_dummy.id)
            ).fetchone()
        assert fetched_dummy.id == updated_dummy.id
        assert fetched_dummy.name == updated_dummy.name

    def test_rollback_on_error(self, dummy):

        dummy = dummy(name='dummy name')

        # Class definition set name  nullable  to false.
        dummy.name = None
        with db.session() as session:
            session.execute("DELETE FROM Dummies")
            session.commit()

        with pytest.raises(err.SavingModelFailed):
            dummy.save()
        with db.session() as session:
            result = session.execute("SELECT * FROM Dummies").fetchall()
        assert len(result) == 0


class TestFetch:

    def test_existing_entity(self, dummy):

        name = "dummy {uuid}".format(uuid=uuid().int)
        with db.session() as session:
            inserted_id = session.execute(
                "INSERT INTO Dummies (name) VALUES ('{}')".format(name)
            ).lastrowid
            session.commit()

        fetched_dummy = dummy().fetch(id=inserted_id)

        assert fetched_dummy.name == name

        with db.session() as session:
            session.execute("DELETE FROM Dummies")
            session.commit()

    def test_invalid_id(self, dummy):

        with pytest.raises(err.InvalidModelId):
            dummy().fetch(id=None)

    def test_unknown_entity(self, dummy):

        with pytest.raises(err.UnknownModelId):
            dummy().fetch(id=42)


def test_repr():

    class ReprDummy(db.Model):

        id = sql.Column(sql.Integer, primary_key=True)
        firstname = sql.Column(sql.String(80))
        lastname = sql.Column(sql.String(80))
        age = sql.Column(sql.Integer)

    dummy = ReprDummy(firstname='John', lastname='Doe', age=35)

    assert dummy.__repr__() == "ReprDummy(age=35, firstname='John', lastname='Doe')"

class TestSelect:

    def test_invalid_attribute(self, dummy):

        with pytest.raises(err.InvalidModelAttribute):
            dummy.select(age=30)

    def test_empty_result(self, dummy):

        assert dummy.select(name='John') == []

    def test_select_all(self, dummy):

        # Setup.
        num_dummies = 10
        query = "INSERT INTO Dummies (name) VALUES "
        query += ", ".join(["('John')" for _ in range(num_dummies)])
        query += ", "
        query += ", ".join(["('Tom')" for _ in range(num_dummies)])
        with db.session() as session:
            session.execute(query)
            session.commit()

        dummies = dummy.select(name='John')

        assert len(dummies) == num_dummies
        for dum in dummies:
            assert isinstance(dum, dummy)
            assert dum.name == 'John'

        with db.session() as session:
            session.execute("DELETE FROM Dummies")
            session.commit()

    def test_select_some(self, dummy):

        num_dummies = 10
        query = "INSERT INTO Dummies (name) VALUES "
        query += ", ".join(["('John')" for _ in range(num_dummies)])
        with db.session() as session:
            session.execute(query)
            session.commit()

        dummies = dummy.select(limit=5, name='John')

        assert len(dummies) == 5
        for dum in dummies:
            assert isinstance(dum, dummy)
            assert dum.name == 'John'

        with db.session() as session:
            session.execute("DELETE FROM Dummies")
            session.commit()

