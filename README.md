# JHHAlchemy

Jawbone Health Flask-SQLAlchemy base model and mixins

## Base Model Usage

To use the base model:

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

## TimeOrderMixin Usage
To use a jhhalchemy mixin, simply include it in your model's inheritance list:
```python
import jhhalchemy.model.time_order

class MyTimeOrderModel(db.Model, jhhalchemy.model.time_order.TimeOrderMixin):
    """
    Define additional columns, etc.
    """
    my_col = db.Column(...)
    
    @classmethod
    def my_read_range(cls, my_col_value, start_timestamp, end_timestamp):
        cls.read_time_range(my_col == my_col_value, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
```

## Migrations
The `jhhalchemy.migrate` module provides some utility functions to obtain database locks and safely run an
[Alembic](http://alembic.zzzcomputing.com/) upgrade:
```python
jhhalchemy.migrate.upgrade(
    'my_database', 
    'mysql://root:root@0.0.0.0/my_database', 
    'alembic.ini')
```
## Examples

Check out how the fixtures are created in
[tests/integration/conftest.py](https://github.com/JawboneHealth/jhhalchemy/blob/master/tests/integration/conftest.py).

## Tests
jhhalchemy includes unit and integration tests. Use [pytest](https://docs.pytest.org/en/latest/) to run them. For the 
integration tests, you will need to set the `MYSQL_CONNECTION_URI` environment variable. You can find more details in 
the [fixtures](https://github.com/JawboneHealth/jhhalchemy/blob/master/jhhalchemy/tests/integration/conftest.py).

