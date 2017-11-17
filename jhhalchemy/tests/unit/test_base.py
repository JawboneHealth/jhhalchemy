"""
Unit tests for the Base model
"""
import jhhalchemy.model
import mock
import pytest


@pytest.fixture
def base_types():
    """
    Modify the BaseTypes class to include some testable properties.
    """
    #
    # Add some fake properties
    #
    jhhalchemy.model.BaseTypes.login = 1
    jhhalchemy.model.BaseTypes.__login__ = 2
    yield jhhalchemy.model.BaseTypes

    #
    # Teardown: Remove the fake properties
    #
    del jhhalchemy.model.BaseTypes.login
    del jhhalchemy.model.BaseTypes.__login__


def test_BaseTypes_values(base_types):
    """
    Verify that values only returns expected properties.

    :param base_types: BaseTypes fixture
    """
    values = base_types.values()
    assert base_types.login in values
    assert base_types.__login__ not in values


@pytest.fixture
def base_instance():
    return jhhalchemy.model.Base()


def test_Base_save(base_instance):
    """
    Verify add and commit to DB.

    :param base_instance: instance of Base model
    """
    session = mock.Mock()

    #
    # Defaults to commit
    #
    base_instance.save(session)
    session.add.assert_called_once_with(base_instance)
    session.commit.assert_called_once_with()

    #
    # No commit
    #
    session.reset_mock()
    base_instance.save(session, commit=False)
    session.add.assert_called_once_with(base_instance)
    assert not session.commit.called


@mock.patch('jhhalchemy.model.Base.query', autospec=True)
def test_Base_read_by(mock_query):
    """
    Verify soft-delete logic in read_by

    :param mock_query: mocked model class query method
    """
    #
    # Default to no soft-deleted rows
    #
    jhhalchemy.model.Base.read_by(col='val')
    mock_query.filter_by.assert_called_once_with(col='val', time_removed=0)

    #
    # Get soft-deleted rows
    #
    mock_query.reset_mock()
    jhhalchemy.model.Base.read_by(removed=True, col='val')
    mock_query.filter_by.assert_called_once_with(col='val')


@mock.patch('jhhalchemy.model.Base.query', autospec=True)
@mock.patch('jhhalchemy.model.Base.time_created', autospec=True)
@mock.patch('jhhalchemy.model.Base.time_removed', autospec=True)
def test_Base_read(mock_time_removed, mock_time_created, mock_query):
    """
    Verify soft-delete logic in read

    :param mock_time_removed: mocked time_removed column
    :param mock_time_created: mockec time_created column
    :param mock_query: mocked model class query method
    """
    #
    # Default to no soft-deleted rows
    #
    jhhalchemy.model.Base.read(mock_time_created == 1)
    mock_query.filter.assert_called_once_with(mock_time_removed == 0, mock_time_created == 1)

    #
    # Get soft-deleted rows
    #
    mock_query.reset_mock()
    jhhalchemy.model.Base.read(mock_time_created == 1, removed=True)
    mock_query.filter.assert_called_once_with(mock_time_created == 1)


@mock.patch('sqlalchemy.func.unix_timestamp', autospec=True)
def test_Base_delete(mock_ut, base_instance):
    """
    Verify soft delete and commit logic

    :param base_instance: instance of Base model
    """
    mock_session = mock.Mock()

    #
    # Default to soft delete and commit
    #
    base_instance.delete(mock_session)
    mock_ut.assert_called_once_with()
    assert not mock_session.delete.called
    mock_session.commit.assert_called_once_with()

    #
    # Hard delete, no commit
    #
    mock_ut.reset_mock()
    mock_session.reset_mock()
    base_instance.delete(mock_session, commit=False, soft=False)
    assert not mock_ut.called
    mock_session.delete.assert_called_once_with(base_instance)
    assert not mock_session.commit.called
