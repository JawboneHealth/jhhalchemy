"""
Unit tests for migration functions
"""
import jhhalchemy.migrate
import mock
from sqlalchemy import text

@mock.patch('sqlalchemy.create_engine', autospec=True)
@mock.patch('time.sleep', autospec=True)
def test_get_upgrade_lock(mock_sleep, mock_create):
    """
    Verify locking calls

    :param mock_sleep: mocked time.sleep
    :param mock_create: mocked sqlalchemy engine creation method
    """
    dbname = 'dbname'
    connect_str = 'connect_str'

    #
    # Fail to get the lock on the first try. Succeed on the second.
    #
    mock_create.return_value.begin.return_value.execute.return_value.scalar.side_effect = [False, True]
    with jhhalchemy.migrate.get_upgrade_lock(dbname, connect_str) as lock:
        mock_create.assert_called_once_with(connect_str)
        mock_create.return_value.begin.return_value.__enter__.return_value.execute.assert_has_calls([
            # mock.call(text("SELECT GET_LOCK('upgrade_dbname', 5)")),
            mock.call().scalar(),
            mock.call().close(),
            mock.call().scalar().__bool__()
            ])
        # mock_sleep.assert_called_once_with(jhhalchemy.migrate.LOCK_TIMEOUT)
        assert lock
        mock_create.reset_mock()

    mock_create.return_value.begin.return_value.__enter__.return_value.execute.assert_has_calls([
        # mock.call(text("SELECT GET_LOCK('upgrade_dbname', 5)")),
        mock.call().close()
        ])
    # mock_create.return_value.begin.return_value.execute.return_value.close.assert_called_with()
    mock_create.return_value.dispose.assert_called_once_with()


@mock.patch('jhhalchemy.migrate.get_upgrade_lock', autospec=True)
@mock.patch('sqlalchemy_utils.database_exists', autospec=True)
@mock.patch('sqlalchemy_utils.create_database', autospec=True)
@mock.patch('alembic.config.Config', autospec=True)
@mock.patch('alembic.command.upgrade', autospec=True)
def test_upgrade(mock_upgrade, mock_config, mock_create, mock_exists, mock_get):
    dbname = 'dbname'
    connect_str = 'connect_str'
    alembic_conf = 'alembic_conf'

    #
    # DB exists
    #
    mock_exists.return_value = True
    jhhalchemy.migrate.upgrade(dbname, connect_str, alembic_conf)
    mock_exists.assert_called_once_with(connect_str)
    assert not mock_create.called
    mock_get.assert_called_once_with(dbname, connect_str)
    mock_config.assert_called_once_with(alembic_conf, attributes={'configure_logger': False})
    mock_upgrade.assert_called_once_with(mock_config.return_value, 'head')

    #
    # DB does not exist
    #
    mock_exists.reset_mock()
    mock_exists.return_value = False
    mock_get.reset_mock()
    mock_config.reset_mock()
    mock_upgrade.reset_mock()
    jhhalchemy.migrate.upgrade(dbname, connect_str, alembic_conf)
    mock_get.assert_called_once_with(dbname, connect_str)
    mock_exists.assert_called_once_with(connect_str)
    mock_create.assert_called_once_with(connect_str)
    mock_config.assert_called_once_with(alembic_conf, attributes={'configure_logger': False})
    mock_upgrade.assert_called_once_with(mock_config.return_value, 'head')
