"""
flask_sqlachemy model mixin for TimeOrder tables
"""
import sqlalchemy


class TimeOrderMixin(object):
    """
    Mixin for tables with time_order columns used for reverse order sorting
    """
    time_order = sqlalchemy.Column(sqlalchemy.Integer)

    @property
    def timestamp(self):
        """
        Derive the timestamp from time_order.

        :return: the timestamp when the timezone was set
        """
        return -self.time_order

    @timestamp.setter
    def timestamp(self, timestamp):
        """
        Use a timestamp to set time_order.

        :param timestamp: unix timestamp
        """
        self.time_order = -timestamp

    @classmethod
    def read_time_range(cls, start_timestamp=None, end_timestamp=None):
        """
        Get all timezones set within a given time. Uses time_dsc_index

        SELECT *
        FROM <table>
        WHERE time_order <= -<start_timestamp>
        AND time_order >= -<end_timestamp>

        :param start_timestamp: unix timestamp to start looking after
        :param end_timestamp: unix timestamp to start looking before
        :return: model generator
        """
        criteria = []
        if start_timestamp is not None:
            criteria.append(cls.time_order <= -start_timestamp)
        if end_timestamp is not None:
            criteria.append(cls.time_order >= -end_timestamp)
        return cls.read(*criteria)
