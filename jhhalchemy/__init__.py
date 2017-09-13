"""
JHHAlchemy defines the base database model that JHH uses with Flask-SQLAlchemy

To use this base model:

1. Set it as the model_class when creating the flask_sqlalchemy object:

import flask_sqlalchemy
import jhhalchemy.model

db = flask_sqlalchemy.SQLAlchemy(app, model_class=jhhalchemy.model.Base)

2. Your applications model's should inherit from flask_sqlalchemy's Model and define Columns with SQLAlchemy's objects:

class MyModel(db.Model):
    my_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

3. The Base.save and Base.delete methods require passing in a session object. In most cases use the the one from
flask_sqlalchemy:

my_model = MyModel()
my_model.save(db.session)
my_model.delete(db.session)

For an example of this, check out how the pytest.fixtures are created in tests/integration/test_base.py
"""
__version__ = '0.2'
