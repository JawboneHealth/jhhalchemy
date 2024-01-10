"""
Integration test to verify upgrade behavior
"""
import flask
from flask_sqlalchemy import SQLAlchemy
import jhhalchemy.migrate
import jhhalchemy.model
import pytest
import sqlalchemy
import sqlalchemy_utils


@pytest.fixture(scope='module')
def dbname():
    """
    database name fixture

    :return: test db name
    """
    return 'jhhalchemy_test'


@pytest.fixture(scope='module')
def connect_str(dbname):
    """
    connection string fixture

    :param dbname: test db name
    :return: test connection string
    """
    return 'mysql://root:root@0.0.0.0/{}'.format(dbname)


@pytest.fixture(scope='module')
def db(connect_str):
    """
    Yield a flask_sqlalchemy db object for testing, then clean up the database.

    :param connect_str: test connection string
    :return: flask_sqlalchemy db object
    """
    engine = sqlalchemy.create_engine(connect_str)

    #
    # Initialize flask and flask_sqlalchemy
    #
    app = flask.Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = connect_str

    fs_db = SQLAlchemy(app, model_class=jhhalchemy.model.Base)
    if "sqlalchemy" not in app.extensions:
        fs_db.init_app(app)

    yield fs_db

    #
    # Tear down the DB.
    #
    fs_db.session.commit()
    sqlalchemy_utils.drop_database(engine.url)


@pytest.fixture(scope='module')
def model(db):
    """
    Create a model class

    :param db: flask_sqlalchemy fixture
    :return: model instance
    """
    class DropThis(db.Model):
        __tablename__ = 'DropThis'
        dt_id = sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True)

    return DropThis


def test_upgrade(dbname, connect_str, db, model):
    """
    Verify upgrade creates the db and the table.

    :param dbname: test db name
    :param connect_str: test db connection string
    :param db: flask_sqlalchemy db object
    :param model: test table model
    """
    alembic_conf = 'alembic/alembic.ini'
    assert not sqlalchemy_utils.database_exists(connect_str)
    jhhalchemy.migrate.upgrade(dbname, connect_str, alembic_conf)
    assert sqlalchemy_utils.database_exists(connect_str)
    dt = model()
    assert dt.dt_id != 1
    dt.save(db.session)
    assert dt.dt_id == 1
