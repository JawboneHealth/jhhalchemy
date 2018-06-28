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


"""
Helper Function for APIs that interact with time_order models
"""


class InvalidTimestampRange(Exception):
    """
    Raise this when start_timestamp > end_timestamp
    """
    pass


def get_by_range(model_cls, *args, **kwargs):
    """
    Get ordered list of models for the specified time range.
    The timestamp on the earliest model will likely occur before start_timestamp. This is to ensure that we return
    the models for the entire range.

    :param model_cls: the class of the model to return
    :param args: arguments specific to the model class
    :param kwargs: start_timestamp and end_timestamp (see below) as well as keyword args specific to the model class
    :keyword start_timestamp: the most recent models set before this and all after, defaults to 0
    :keyword end_timestamp: only models set before (and including) this timestamp, defaults to now
    :return: model generator
    """
    start_timestamp = kwargs.get('start_timestamp')
    end_timestamp = kwargs.get('end_timestamp')
    if (start_timestamp is not None) and (end_timestamp is not None) and (start_timestamp > end_timestamp):
        raise InvalidTimestampRange

    models = model_cls.read_time_range(*args, end_timestamp=end_timestamp).order_by(model_cls.time_order)

    #
    # start time -> Loop through until you find one set before or on start
    #
    if start_timestamp is not None:
        index = 0
        for index, model in enumerate(models, start=1):
            if model.timestamp <= start_timestamp:
                break
        models = models[:index]

    return models
