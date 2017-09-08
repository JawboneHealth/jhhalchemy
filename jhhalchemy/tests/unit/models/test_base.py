"""
Unit tests for the Base model
"""
import pytest


@pytest.fixture
def base_types(mocker):
    """
    Modify the BaseTypes class to include some testable properties.
    """
    import jhhalchemy
    mocker.patch.object(jhhalchemy, 'db', autospec=True)
    import jhhalchemy.models

    #
    # Add some fake properties
    #
    jhhalchemy.models.BaseTypes.login = 1
    jhhalchemy.models.BaseTypes.__login__ = 2
    yield jhhalchemy.models.BaseTypes

    #
    # Teardown: Remove the fake properties
    #
    del jhhalchemy.models.BaseTypes.login
    del jhhalchemy.models.BaseTypes.__login__


def test_values(base_types):
    """
    Verify that values only returns expected properties.

    :param base_types: BaseTypes fixture
    """
    values = base_types.values()
    assert base_types.login in values
    assert base_types.__login__ not in values


#
# TODO: Figure out how to properly mock db.Model and db.Session so I can write actual unit tests for the Base model.
# At the moment the ROI on figuring this out is low given that the logic is minimal and the integration tests cover it.
#
