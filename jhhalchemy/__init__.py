"""
JHHAlchemy defines a declarative base model for JHH database tables.

To use the model:

1. Once you've established the db object in your app, intialize jhhalchemy.

import jhhalchemy
jhhalchemy.init_db(<flask_sqlalchemy object>)

2. Now you can import the base model and inherit from it.

import jhhalchemy.models
class MyModel(jhhalchemy.models.Base):
    ...
"""
db = None


def init_db(fs_db):
    """
    Initialize the module with the current flask sqlalchemy db instance.

    :param fs_db: the instantiated flask sqlalchemy object from your app
    """
    global db
    db = fs_db
