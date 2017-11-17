"""
Tests the base model functionality against a real database connection.
Creates a simple model that inherits from base and then exercises and verifies the base model methods.

See conftest.py to setup your DB details in the fixtures
"""
import jhhalchemy.model
import pytest
import sqlalchemy
import time


@pytest.fixture
def model(db):
    """
    Create a model instance.

    :param db: flask_sqlalchemy fixture
    :return: model instance
    """
    class NameModel(db.Model):
        """
        Simple model to test the Base methods
        """
        name_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String(255))

    db.create_all()
    return NameModel(name='tester{}'.format(time.time()))


def test_base(db, model):
    """
    Verify the model's base methods.

    :param db: flask_sqlalchemy object
    :param model: instantiated model fixture
    """
    #
    # Save should give you an id
    #
    assert model.name_id is None
    model.save(db.session)
    tester_id = model.name_id
    assert tester_id > 0

    #
    # read_by(name) should give you the same id
    #
    cls = model.__class__
    same_tester = cls.read_by(name=model.name).one()
    assert same_tester.name_id == tester_id

    #
    # read(id > id -1) should give you the same id
    #
    still_same_tester = cls.read(cls.name_id > tester_id - 1).one()
    assert still_same_tester.name_id == tester_id

    #
    # delete should set time_removed
    #
    assert still_same_tester.time_removed == jhhalchemy.model.NOT_REMOVED
    still_same_tester.delete(db.session)
    assert still_same_tester.time_removed != jhhalchemy.model.NOT_REMOVED

    #
    # read and read_by should now return nothing
    #
    no_one = cls.read_by(name=model.name).first()
    assert no_one is None
    no_one = cls.read(cls.name_id > tester_id - 1).first()
    assert no_one is None

    #
    # Now, let's include soft-deleted rows
    #
    deleted_tester = cls.read_by(name=model.name, removed=True).one()
    assert deleted_tester.name_id == tester_id
    same_deleted_tester = cls.read(cls.name_id > tester_id - 1, removed=True).one()
    assert same_deleted_tester.name_id == tester_id

    #
    # Ok, delete for real
    #
    deleted_tester.delete(db.session, soft=False)
    assert cls.read_by(name=model.name).first() is None
