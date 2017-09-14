# JHHAlchemy

Jawbone Health Flask-SQLAlchemy base model and CRUD methods

## Usage

To use this base model:

1. Set it as the model_class when creating the flask_sqlalchemy object:
```python
import flask_sqlalchemy
import jhhalchemy.model

db = flask_sqlalchemy.SQLAlchemy(app, model_class=jhhalchemy.model.Base)
```

2. Your application's models should inherit from flask_sqlalchemy's Model and define Columns with SQLAlchemy's objects:
```python
class MyModel(db.Model):
    my_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
```

3. The Base.save and Base.delete methods require passing in a session object. In most cases use the the one from
flask_sqlalchemy:
```python
my_model = MyModel()
my_model.save(db.session)
my_model.delete(db.session)
```

## Example

Check out how the pytest.fixtures are created in [jhhalchemy/tests/integration/test_base.py](https://github.com/JawboneHealth/jhhalchemy/blob/master/jhhalchemy/tests/integration/test_base.py)
