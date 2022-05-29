
# pylint: disable=missing-module-docstring,missing-function-docstring


import pytest

from app.common import db, errors as err


@pytest.mark.usefixtures("drop_dummy_table")
def test_fetching_existing_entry_returns_it(dummy_instance, dummy_class):

    with db.session() as session:
        inserted_id = session.execute(
            f"INSERT INTO Dummies (name) VALUES ('{dummy_instance.name}')"
        ).lastrowid
        session.commit()

    fetched_dummy = dummy_class.fetch(id=inserted_id)

    assert fetched_dummy.name == dummy_instance.name

    with db.session() as session:
        session.execute(f"DELETE FROM Dummies WHERE id = {fetched_dummy.id}")
        session.commit()


@pytest.mark.usefixtures("drop_dummy_table")
def test_fetching_an_invalid_id_raises(dummy_class):

    with pytest.raises(err.InvalidModelId):
        dummy_class.fetch(id=None)


@pytest.mark.usefixtures("drop_dummy_table")
def test_fetching_an_unknown_id_raises(dummy_class):

    with pytest.raises(err.UnknownModelId):
        dummy_class.fetch(id=42)
