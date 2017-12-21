"""
flask_sqlachemy model mixin for TimeOrder tables
"""
import sqlalchemy


class TimeOrderMixin(object):
    """
    Mixin for tables with time_order columns used for reverse order sorting

    Must be mixed with a model that inherits from jhhalchemy.model
    """
    time_order = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

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
    def read_time_range(cls, *args, **kwargs):
        """
        Get all timezones set within a given time. Uses time_dsc_index

        SELECT *
        FROM <table>
        WHERE time_order <= -<start_timestamp>
        AND time_order >= -<end_timestamp>

        :param args: SQLAlchemy filter criteria, (e.g., uid == uid, type == 1)
        :param kwargs: start_timestamp and end_timestamp are the only kwargs, they specify the range (inclusive)
        :return: model generator
        """
        criteria = list(args)
        start = kwargs.get('start_timestamp')
        end = kwargs.get('end_timestamp')
        if start is not None:
            criteria.append(cls.time_order <= -start)
        if end is not None:
            criteria.append(cls.time_order >= -end)
        return cls.read(*criteria)
