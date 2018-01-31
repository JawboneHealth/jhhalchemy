"""
pytest fixtures for setting up a DB connection and creating tables to verify the models' functionality.

To use this, you need to set MYSQL_CONNECTION_URI as an ENV var. It defaults to:
mysql://root:root@0.0.0.0/test_db

The account you connect with should be able to:
1. create database
2. create a table in that database and have all access rights to it
3. drop the created database

Note: this might work with other databases besides mysql/maria, but we haven't tested that.
"""
import flask
import flask_sqlalchemy
import jhhalchemy.model
import os
import pytest
import sqlalchemy
import sqlalchemy_utils

#
# Grab MYSQL connection string from the environment
#
MYSQL_CONNECTION_URI = os.environ.get('MYSQL_CONNECTION_URI', 'mysql://root:root@0.0.0.0/test_db')


@pytest.fixture(scope='session')
def engine():
    """
    Creates SQLAlchemy engine

    :return: engine object
    """
    return sqlalchemy.create_engine(MYSQL_CONNECTION_URI)


@pytest.fixture(scope='session')
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

    fs_db = flask_sqlalchemy.SQLAlchemy(app, model_class=jhhalchemy.model.Base)
    yield fs_db

    #
    # Tear down the DB.
    #
    fs_db.session.commit()
    sqlalchemy_utils.drop_database(engine.url)
