
# pylint: disable=missing-module-docstring,missing-function-docstring


import pytest

from app.common import db, errors as err


@pytest.mark.usefixtures("drop_dummy_table")
def test_select_invalid_attribute_raises(dummy_class):

    with pytest.raises(err.InvalidModelAttribute):
        dummy_class.select(age=42)


@pytest.mark.usefixtures("drop_dummy_table")
def test_select_unknown_attribute_returns_empty_result(dummy_class):

    assert dummy_class.select(name='John') == []


@pytest.mark.usefixtures("drop_dummy_table")
def test_select_attribute_with_multiple_result_returns_all(dummy_class):

    number_of_dummies = 10
    query = "INSERT INTO Dummies (name) VALUES "
    query += ", ".join(["('John')" for _ in range(number_of_dummies)])
    query += ", "
    query += ", ".join(["('Tom')" for _ in range(number_of_dummies)])
    with db.session() as session:
        session.execute(query)
        session.commit()

    dummies = dummy_class.select(name='John')

    assert len(dummies) == number_of_dummies
    for dummy in dummies:
        assert isinstance(dummy, dummy_class)
        assert dummy.name == 'John'

    with db.session() as session:
        session.execute("DELETE FROM Dummies")
        session.commit()


@pytest.mark.usefixtures("drop_dummy_table")
def test_select_using_limit_returns_limited_results(dummy_class):

    number_of_dummies = 10
    query = "INSERT INTO Dummies (name) VALUES "
    query += ", ".join(["('John')" for _ in range(number_of_dummies)])
    with db.session() as session:
        session.execute(query)
        session.commit()

    dummies = dummy_class.select(name='John', limit=5)

    assert len(dummies) == 5
    for dummy in dummies:
        assert isinstance(dummy, dummy_class)
        assert dummy.name == 'John'

    with db.session() as session:
        session.execute("DELETE FROM Dummies")
        session.commit()
