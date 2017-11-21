"""
Unit tests for the TimeOrderBase model
"""
import jhhalchemy.model.time_order
import mock


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
