"""
Define the flask_sqlalchemy base model for JHH.
"""
import flask_sqlalchemy
import sqlalchemy


#
# Table constants
#
NOT_REMOVED = 0


class Base(flask_sqlalchemy.Model):
    """
    Base class for JHH DB models
    Defines common timestamp columns and CRUD methods.
    """
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB'}

    time_removed = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, server_default='{}'.format(NOT_REMOVED))
    time_created = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        server_default=sqlalchemy.func.unix_timestamp())
    time_modified = sqlalchemy.Column(
        sqlalchemy.TIMESTAMP,
        nullable=False,
        server_onupdate=sqlalchemy.func.now(),
        server_default=sqlalchemy.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def save(self, session, commit=True):
        """
        Add a row to the session so that it gets saved to the DB.

        :param session: flask_sqlalchemy session object
        :param commit: whether to issue the commit
        """
        session.add(self)
        if commit:
            session.commit()

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

    def delete(self, session, commit=True, soft=True):
        """
        Delete a row from the DB.

        :param session: flask_sqlalchemy session object
        :param commit: whether to issue the commit
        :param soft: whether this is a soft delete (i.e., update time_removed)
        """
        if soft:
            self.time_removed = sqlalchemy.func.unix_timestamp()
        else:
            session.delete(self)

        if commit:
            session.commit()
