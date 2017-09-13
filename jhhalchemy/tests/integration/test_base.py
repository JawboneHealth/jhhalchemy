"""
Tests the base model functionality against a real database connection.
Creates a simple model that inherits from base and then exercises and verifies the base model methods.

To use this, you need to set MYSQL_CONNECTION_URI.
The account you connect with should be able to:
1. create database
2. create a table in that database and have all access rights to it
3. drop the created database

Note: this might work with other databases besides mysql/maria, but we haven't tested that.
"""
import flask
import flask_sqlalchemy
import jhhalchemy.model
import pytest
import sqlalchemy
import sqlalchemy_utils
import time

#
# Set your own MYSQL connection string here
#
MYSQL_CONNECTION_URI = 'mysql://root:root@0.0.0.0/test_db'


@pytest.fixture
def engine():
    """
    Creates SQLAlchemy engine

    :return: engine object
    """
    return sqlalchemy.create_engine(MYSQL_CONNECTION_URI)


@pytest.fixture
def db(engine):
    """
    Create a flask_sqlalchemy object

    :param engine: SQLAlchemy engine
    :return: flask_sqlalchemy object
    """
    #
    # Create DB if it doesn't exist
    #
    if not sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.create_database(engine.url)

    #
    # Initialize flask and flask_sqlalchemy
    #
    app = flask.Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = MYSQL_CONNECTION_URI

    import jhhalchemy.model
    db = flask_sqlalchemy.SQLAlchemy(app, model_class=jhhalchemy.model.Base)
    return db


@pytest.fixture
def model(engine, db):
    """
    Create an instance of a model that inherits from jhhalchemy.model.Base

    :param engine: SQLAlchemy engine object
    :param db: flask_sqlalchemy object
    :return: the model instance
    """
    class NameModel(db.Model):
        """
        Simple model to test the Base methods
        """
        test_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String(255))

        def __init__(self, name):
            self.name = name

    #
    # Create table and yield the model instance.
    #
    db.create_all()
    tester = NameModel('tester{}'.format(time.time()))
    yield tester

    #
    # Tear down the DB.
    #
    db.session.commit()
    sqlalchemy_utils.drop_database(engine.url)


def test_base(db, model):
    """
    Verify the model's base methods.

    :param db: flask_sqlalchemy object
    :param model: instantiated model fixture
    """
    #
    # Save should give you an id
    #
    assert model.test_id is None
    model.save(db.session)
    tester_id = model.test_id
    assert tester_id > 0

    #
    # read_by(name) should give you the same id
    #
    cls = model.__class__
    same_tester = cls.read_by(name=model.name).one()
    assert same_tester.test_id == tester_id

    #
    # read(id > id -1) should give you the same id
    #
    still_same_tester = cls.read(cls.test_id > tester_id - 1).one()
    assert still_same_tester.test_id == tester_id

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
    no_one = cls.read(cls.test_id > tester_id - 1).first()
    assert no_one is None

    #
    # Now, let's include soft-deleted rows
    #
    deleted_tester = cls.read_by(name=model.name, removed=True).one()
    assert deleted_tester.test_id == tester_id
    same_deleted_tester = cls.read(cls.test_id > tester_id - 1, removed=True).one()
    assert same_deleted_tester.test_id == tester_id

    #
    # Ok, delete for real
    #
    deleted_tester.delete(db.session, soft=False)
    assert cls.read_by(name=model.name).first() is None
