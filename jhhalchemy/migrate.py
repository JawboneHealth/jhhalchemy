"""
Alembic migration utilities
"""
import alembic.command
import alembic.config
import contextlib
import logging
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy_utils
import time

#
# Default timeout to 5 seconds
#
LOCK_TIMEOUT = 5

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(' * JHHAlchemy - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@contextlib.contextmanager
def get_upgrade_lock(dbname, connect_str, timeout=LOCK_TIMEOUT):
    """
    Wait until you can get the lock, then yield it, and eventually release it.

    Inspired by: http://arr.gr/blog/2016/05/mysql-named-locks-in-python-context-managers/

    :param dbname: database to upgrade
    :param connect_str: connection string to the database
    :param timeout: how long to wait between tries for the lock, default 5 seconds
    """
    #
    # Open connection and try to get the lock
    #
    query_getlock = sqlalchemy.text("SELECT GET_LOCK('upgrade_{}', {})".format(dbname, timeout))
    engine = sqlalchemy.create_engine(connect_str)
    with engine.begin() as connection:
        cursor = connection.execute(query_getlock)

    lock = cursor.scalar()
    cursor.close()

    #
    # Keep trying until you get it.
    #
    while not lock:
        logger.info('Cannot acquire {} upgrade lock. Sleeping {} seconds.'.format(dbname, timeout))
        time.sleep(timeout)
        with engine.begin() as connection:
            cursor = connection.execute(query_getlock)
        lock = cursor.scalar()
        cursor.close()
    logger.info('Acquired {} upgrade lock'.format(dbname))
    yield lock

    #
    # Release the lock and close the connection.
    #
    query_releaselock = sqlalchemy.text("SELECT RELEASE_LOCK('upgrade_{}')".format(dbname))
    with engine.begin() as connection:
        cursor = connection.execute(query_releaselock)
    cursor.close()
    engine.dispose()
    logger.info('Released {} upgrade lock'.format(dbname))


def upgrade(dbname, connect_str, alembic_conf):
    """
    Get the database's upgrade lock and run alembic.

    :param dbname: Name of the database to upgrade/create
    :param connect_str: Connection string to the database (usually Flask's SQLALCHEMY_DATABASE_URI)
    :param alembic_conf: location of alembic.ini
    """
    #
    # The db has to exist before we can get the lock. On the off-chance that another process creates the db between
    # checking if it exists and running the create, ignore the exception.
    #
    if not sqlalchemy_utils.database_exists(connect_str):
        logger.info('Creating {}'.format(dbname))
        try:
            sqlalchemy_utils.create_database(connect_str)
        except sqlalchemy.exc.ProgrammingError as exc:
            if not sqlalchemy_utils.database_exists(connect_str):
                logger.error('Could not create {}'.format(dbname))
                raise exc

    with get_upgrade_lock(dbname, connect_str):
        alembic_config = alembic.config.Config(
            alembic_conf,
            attributes={'configure_logger': False})
        logger.info('Upgrading {} to head'.format(dbname))
        alembic.command.upgrade(alembic_config, 'head')
