"""
Unit tests for the TimeOrderBase model
"""
import jhhalchemy.model.time_order
import mock
import pytest


def test_timestamp():
    """
    Verify the timestamp property getter and setter
    """
    timestamp = 10
    timeorder = jhhalchemy.model.time_order.TimeOrderMixin()
    timeorder.timestamp = timestamp
    assert timeorder.time_order == -timestamp
    assert timeorder.timestamp == timestamp


@mock.patch('jhhalchemy.model.time_order.TimeOrderMixin.time_order')
def test_read_time_range(mock_time_order):
    """
    Verify the time range lookup.

    :param mock_time_order: mocked column
    """
    col = 1
    start_ts = 1
    end_ts = 10

    #
    # Mock the criteria and the read method
    #
    mock_col = mock.Mock()
    mock_col.__eq__ = mock.Mock()
    col_crit = mock_col == col
    mock_time_order.__le__ = mock.Mock()
    mock_time_order.__ge__ = mock.Mock()
    start_crit = mock_time_order <= -start_ts
    end_crit = mock_time_order >= -end_ts
    jhhalchemy.model.time_order.TimeOrderMixin.read = mock.Mock()

    #
    # Both timestamps and another column
    #
    timeorders = jhhalchemy.model.time_order.TimeOrderMixin.read_time_range(
        mock_col == col,
        start_timestamp=start_ts,
        end_timestamp=end_ts)
    jhhalchemy.model.time_order.TimeOrderMixin.read.assert_called_once_with(col_crit, start_crit, end_crit)
    assert timeorders == jhhalchemy.model.time_order.TimeOrderMixin.read.return_value

    #
    # Start only
    #
    jhhalchemy.model.time_order.TimeOrderMixin.read.reset_mock()
    timeorders = jhhalchemy.model.time_order.TimeOrderMixin.read_time_range(start_timestamp=start_ts)
    jhhalchemy.model.time_order.TimeOrderMixin.read.assert_called_once_with(start_crit)
    assert timeorders == jhhalchemy.model.time_order.TimeOrderMixin.read.return_value


def test_get_timezones_by_range():
    """
    Verify range lookup.
    """
    col = 1
    model_cls = mock.Mock()

    #
    # start > end -> Raise
    #
    start_ts = 10
    end_ts = 1
    with pytest.raises(jhhalchemy.model.time_order.InvalidTimestampRange):
        jhhalchemy.model.time_order.get_by_range(model_cls, col, start_timestamp=start_ts, end_timestamp=end_ts)
    assert not model_cls.read_time_range.called
    assert not model_cls.read_time_range.return_value.order_by.called

    #
    # Don't specify range -> read
    #
    models = jhhalchemy.model.time_order.get_by_range(model_cls, col)
    model_cls.read_time_range.assert_called_once_with(col, end_timestamp=None)
    model_cls.read_time_range.return_value.order_by.assert_called_once_with(model_cls.time_order)
    assert models == model_cls.read_time_range.return_value.order_by.return_value

    #
    # start <= end -> read
    #
    # model between start and end
    # model on start
    # model before start
    # => [between, on start]
    end_ts = 100
    model_cls.reset_mock()
    model_cls.read_time_range.return_value.order_by.return_value = [
        mock.Mock(timestamp=end_ts - 1),
        mock.Mock(timestamp=start_ts),
        mock.Mock(timestamp=start_ts - 1)]
    models = jhhalchemy.model.time_order.get_by_range(model_cls, col, start_timestamp=start_ts, end_timestamp=end_ts)
    model_cls.read_time_range.assert_called_once_with(col, end_timestamp=end_ts)
    model_cls.read_time_range.return_value.order_by.assert_called_once_with(model_cls.time_order)
    assert models == model_cls.read_time_range.return_value.order_by.return_value[:2]

    #
    # Another read case
    #
    # model on end
    # model between start and end
    # model before start
    # => [on end, between, before start]
    #
    model_cls.reset_mock()
    model_cls.read_time_range.return_value.order_by.return_value = [
        mock.Mock(timestamp=end_ts),
        mock.Mock(timestamp=end_ts - 1),
        mock.Mock(timestamp=start_ts - 1)]
    models = jhhalchemy.model.time_order.get_by_range(model_cls, col, start_timestamp=start_ts, end_timestamp=end_ts)
    model_cls.read_time_range.assert_called_once_with(col, end_timestamp=end_ts)
    model_cls.read_time_range.return_value.order_by.assert_called_once_with(model_cls.time_order)
    assert models == model_cls.read_time_range.return_value.order_by.return_value

    #
    # No models in the DB
    #
    model_cls.reset_mock()
    model_cls.read_time_range.return_value.order_by.return_value = []
    models = jhhalchemy.model.time_order.get_by_range(model_cls, col, start_timestamp=start_ts)
    model_cls.read_time_range.assert_called_once_with(col, end_timestamp=None)
    model_cls.read_time_range.return_value.order_by.assert_called_once_with(model_cls.time_order)
    assert models == []
