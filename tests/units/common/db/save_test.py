
# pylint: disable=missing-module-docstring,missing-function-docstring


from uuid import uuid4 as uuid

import pytest

from app.common import db


@pytest.mark.usefixtures("drop_dummy_table")
def test_save_insert_if_not_exit(dummy_instance):

    saved_dummy = dummy_instance.save()

    with db.session() as session:
        fetched_dummy = session.execute(
            f"SELECT * FROM Dummies WHERE id = {saved_dummy.id}"
        ).fetchone()
    assert fetched_dummy.name == 'Jon'


@pytest.mark.usefixtures("drop_dummy_table")
def test_save_update_existing(dummy_class):

    original_name = f"dummy {uuid().int}"
    with db.session() as session:
        inserted_id = session.execute(
            f"INSERT INTO Dummies (name) VALUES ('{original_name}')"
        ).lastrowid
        session.commit()

    updated_dummy = dummy_class(id=inserted_id)
    updated_dummy.name = f"dummy {uuid().int}"
    updated_dummy.save()

    assert updated_dummy.id == inserted_id
    with db.session() as session:
        fetched_dummy = session.execute(
            f"SELECT * FROM Dummies WHERE id = {updated_dummy.id}"
        ).fetchone()
    assert fetched_dummy.id == updated_dummy.id
    assert fetched_dummy.name == updated_dummy.name
