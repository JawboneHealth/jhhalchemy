"""
Tests the TimeOrderBase functionality against a real database connection.
Creates a simple model that uses the TimeOrderBase mixin and verifies the methods.

See conftest.py to setup your DB details in the fixtures
"""
import jhhalchemy.model.time_order
import pytest
import sqlalchemy


@pytest.fixture
def model(db):
    """
    Create model instances and return one

    :param db: flask_sqlalchemy object fixture
    :return: model instance
    """
    class TimeOrderModel(db.Model, jhhalchemy.model.time_order.TimeOrderMixin):
        """
        Simple model to test the TimeOrderBase methods
        """
        name_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String(255))

    db.create_all()
    for i in xrange(1, 4):
        tom = TimeOrderModel(name='{}'.format(i), time_order=-10 * i)
        tom.save(db.session)
    return tom


def test_time_order_base(model):
    """
    Verify the TimeOrderBase model functionality

    :param model: instantiated model fixture
    """
    start_ts = 1
    end_ts = 19

    #
    # Verify timestamp getter/setter
    #
    model.timestamp = start_ts
    assert model.timestamp == start_ts
    assert model.time_order == -start_ts

    #
    # start and end
    #
    cls = model.__class__
    toms = cls.read_time_range(start_timestamp=start_ts, end_timestamp=end_ts)
    nameset = set([tom.name for tom in toms])
    assert nameset == {'1', '3'}

    #
    # start only
    #
    toms = cls.read_time_range(start_timestamp=start_ts)
    nameset = set([tom.name for tom in toms])
    assert nameset == {'1', '2', '3'}

    #
    # end and another column
    #
    toms = cls.read_time_range(cls.name == '3', end_timestamp=20)
    nameset = set([tom.name for tom in toms])
    assert nameset == {'3'}
