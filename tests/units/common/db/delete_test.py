
# pylint: disable=missing-module-docstring,missing-function-docstring


import pytest

from app.common import db


@pytest.mark.usefixtures("drop_dummy_table")
@pytest.mark.xfail(reason="the method doesn't work, see the comment above it")
def test_delete_an_existing_id_remove_it_from_db(dummy_instance):

    dummy_instance.delete()

    with db.session() as session:
        cursor = session.execute(
            f"SELECT * FROM Dummies WHERE id = {dummy_instance.id}"
        )
        selected = next(row for row in cursor)
    assert selected is None
