"""
Tests the base model functionality against a real database connection.
Creates a simple model that inherits from base and then exercises and verifies the base model methods.

To use this, you need to set MYSQL_CONNECTION_URI.
The account you connect with should be able to:
1. create database
2. create a table in that database and have all access rights to it

Note: this might work with other databases besides mysql/maria, but we haven't tested that.
"""
import flask
import flask_sqlalchemy
import pytest
import sqlalchemy
import sqlalchemy_utils
import time

#
# Set your own MYSQL connection string here
#
MYSQL_CONNECTION_URI = 'mysql://root:root@0.0.0.0/test_db'


@pytest.fixture
def model():
    """
    Create an instance of a model that inherits from Base.

    Setup:
    1. Create DB if necessary
    2. Initialize flask app, flask_sqlalchemy db, and jhhalchemy db
    3. Define a model that inherits from Base
    4. Create the table that corresponds to the model
    5. Create an instance of the model

    Tear-down:
    1. Drop the DB
    """
    #
    # Create DB if it doesn't exist
    #
    engine = sqlalchemy.create_engine(MYSQL_CONNECTION_URI)
    if not sqlalchemy_utils.database_exists(engine.url):
        sqlalchemy_utils.create_database(engine.url)

    #
    # Initialize flask, flask_sqlalchemy, and jhhalchemy
    #
    app = flask.Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = MYSQL_CONNECTION_URI
    db = flask_sqlalchemy.SQLAlchemy(app)
    import jhhalchemy
    jhhalchemy.init_db(db)
    import jhhalchemy.models

    class NameModel(jhhalchemy.models.Base):
        """
        Simple model to test the Base methods
        """
        test_id = jhhalchemy.db.Column(jhhalchemy.db.Integer, primary_key=True)
        name = jhhalchemy.db.Column(jhhalchemy.db.String(255))

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


def test_base(model):
    """
    Verify the model's base methods.

    :param model: instantiated model fixture
    """
    #
    # Save should give you an id
    #
    assert model.test_id is None
    model.save()
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
    import jhhalchemy.models
    assert still_same_tester.time_removed == jhhalchemy.models.NOT_REMOVED
    still_same_tester.delete()
    assert still_same_tester.time_removed != jhhalchemy.models.NOT_REMOVED

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
    deleted_tester.delete(soft=False)
    assert cls.read_by(name=model.name).first() is None
