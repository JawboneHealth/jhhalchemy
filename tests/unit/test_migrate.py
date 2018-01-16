"""
Unit tests for migration functions
"""
import jhhalchemy.migrate
import mock


@mock.patch('sqlalchemy.create_engine', autospec=True)
def test_get_upgrade_lock(mock_create):
    """
    Verify locking calls

    :param mock_create: mocked sqlalchemy engine creation method
    """
    dbname = 'dbname'
    connect_str = 'connect_str'

    #
    # TODO: Figure out how to get scalar to return None, then True
    #
    mock_create.return_value.execute.return_value.scalar.return_value = True
    with jhhalchemy.migrate.get_upgrade_lock(dbname, connect_str) as lock:
        mock_create.assert_called_once_with(connect_str)
        mock_create.return_value.execute.assert_called_once_with(
            "SELECT GET_LOCK('upgrade_{}', {})".format(dbname, jhhalchemy.migrate.LOCK_TIMEOUT))
        mock_create.return_value.execute.return_value.scalar.assert_called_once_with()
        mock_create.return_value.execute.return_value.close.assert_called_once_with()
        assert lock == mock_create.return_value.execute.return_value.scalar.return_value
    mock_create.return_value.execute.assert_called_with("SELECT RELEASE_LOCK('upgrade_{}')".format(dbname))
    mock_create.return_value.execute.return_value.close.assert_called_with()
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
