"""
Base model with CRUD methods (technically only R and D since we don't need explicit Create and Update methods on the
model.
"""
import jhhalchemy
import sqlalchemy


#
# Table constants
#
NOT_REMOVED = 0


class BaseTypes(object):
    """
    Base class for type column constants.
    """
    @classmethod
    def values(cls):
        """
        Return the values of the properties (i.e., the type IDs)

        :return: list of values
        """
        return [val for (key, val) in cls.__dict__.iteritems() if not key.startswith('__')]


class Base(jhhalchemy.db.Model):
    """
    Base class for JHH DB models
    Defines common timestamp columns and CRUD methods.
    """
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB'}

    time_removed = jhhalchemy.db.Column(jhhalchemy.db.Integer, default=NOT_REMOVED)
    time_created = jhhalchemy.db.Column(jhhalchemy.db.Integer, default=sqlalchemy.func.unix_timestamp())
    time_modified = jhhalchemy.db.Column(jhhalchemy.db.TIMESTAMP, onupdate=sqlalchemy.func.now())

    def save(self, commit=True):
        """
        Add a row to the session so that it gets saved to the DB.

        :param commit: whether to issue the commit
        """
        jhhalchemy.db.session.add(self)
        if commit:
            jhhalchemy.db.session.commit()

    @classmethod
    def read_by(cls, removed=False, **kwargs):
        """
        filter_by query helper that handles soft delete logic. If your query conditions require expressions, use read.

        :param removed: whether to include soft-deleted rows
        :param kwargs: where clause mappings to pass to filter_by
        :return: row object generator
        """
        if not removed:
            kwargs['time_removed'] = 0
        return cls.query.filter_by(**kwargs)

    @classmethod
    def read(cls, *criteria, **kwargs):
        """
        filter query helper that handles soft delete logic. If your query conditions do not require expressions,
        consider using read_by.

        :param criteria: where clause conditions
        :param kwargs: set removed=True if you want soft-deleted rows
        :return: row object generator
        """
        if not kwargs.get('removed', False):
            return cls.query.filter(cls.time_removed == 0, *criteria)
        return cls.query.filter(*criteria)

    def delete(self, commit=True, soft=True):
        """
        Delete a row from the DB.

        :param commit: whether to issue the commit
        :param soft: whether this is a soft delete (i.e., update time_removed)
        """
        if soft:
            self.time_removed = sqlalchemy.func.unix_timestamp()
        else:
            jhhalchemy.db.session.delete(self)

        if commit:
            jhhalchemy.db.session.commit()
