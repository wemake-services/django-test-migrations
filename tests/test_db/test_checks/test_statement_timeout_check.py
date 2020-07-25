import datetime

import pytest

from django_test_migrations.db.checks.statement_timeout import (
    CHECK_NAME,
    check_statement_timeout_setting,
)
from django_test_migrations.logic.datetime import timedelta_to_miliseconds

ALL_CONNECTIONS_MOCK_PATH = (
    'django_test_migrations.db.checks.statement_timeout.connections.all'
)


@pytest.fixture()
def connection_mock_factory(mocker):
    """Factory of DB connection mocks."""
    def factory(vendor, fetch_one_result=None):
        connection_mock = mocker.MagicMock(vendor=vendor)
        cursor_mock = connection_mock.cursor.return_value
        cursor_mock = cursor_mock.__enter__.return_value  # noqa: WPS609
        cursor_mock.fetchone.return_value = fetch_one_result
        return connection_mock
    return factory


@pytest.mark.parametrize('vendor', ['postgresql', 'mysql'])
def test_correct_statement_timeout(mocker, connection_mock_factory, vendor):
    """Ensure empty list returned when ``statement_timeout`` value correct."""
    connection_mock = connection_mock_factory(vendor, (20000,))
    mocker.patch(ALL_CONNECTIONS_MOCK_PATH, return_value=[connection_mock])
    assert not check_statement_timeout_setting()


@pytest.mark.parametrize('vendor', ['postgresql', 'mysql'])
def test_statement_timeout_not_set(mocker, connection_mock_factory, vendor):
    """Ensure W001 is returned in list when ``statement_timeout`` not set."""
    connection_mock = connection_mock_factory(vendor, (0,))
    mocker.patch(ALL_CONNECTIONS_MOCK_PATH, return_value=[connection_mock])
    check_messages = check_statement_timeout_setting()
    assert len(check_messages) == 1
    assert check_messages[0].id.endswith('W001')


@pytest.mark.parametrize('vendor', ['postgresql', 'mysql'])
def test_statement_timeout_too_high(mocker, connection_mock_factory, vendor):
    """Ensure W002 is returned in list when ``statement_timeout`` too high."""
    connection_mock = connection_mock_factory(
        vendor,
        (timedelta_to_miliseconds(datetime.timedelta(hours=2)),),
    )
    mocker.patch(ALL_CONNECTIONS_MOCK_PATH, return_value=[connection_mock])
    check_messages = check_statement_timeout_setting()
    assert len(check_messages) == 1
    assert check_messages[0].id.endswith('W002')


def test_unsupported_vendors(mocker):
    """Ensure empty list returned when no connections vendors supported."""
    vendors = ['sqlite3', 'custom']
    connection_mocks = [mocker.MagicMock(vendor=vendor) for vendor in vendors]
    mocker.patch(ALL_CONNECTIONS_MOCK_PATH, return_value=connection_mocks)
    assert not check_statement_timeout_setting()


@pytest.mark.parametrize('vendor', ['postgresql', 'mysql'])
def test_statement_timeout_setting_not_found(
    mocker,
    connection_mock_factory,
    vendor,
):
    """Ensure empty list returned when ``statement_timeout`` not found."""
    connection_mock = connection_mock_factory(vendor, None)
    mocker.patch(ALL_CONNECTIONS_MOCK_PATH, return_value=[connection_mock])
    assert not check_statement_timeout_setting()


def test_multiple_connections(mocker, connection_mock_factory):
    """Ensure list with many items returned when many connections present."""
    connections_mocks = [
        connection_mock_factory('sqlite', None),
        connection_mock_factory('postgresql', (0,)),
        connection_mock_factory(
            'mysql',
            (timedelta_to_miliseconds(datetime.timedelta(hours=2)),),
        ),
    ]
    mocker.patch(ALL_CONNECTIONS_MOCK_PATH, return_value=connections_mocks)
    check_messages = check_statement_timeout_setting()
    expected_messages_ids = [
        '{0}.W001'.format(CHECK_NAME),
        '{0}.W002'.format(CHECK_NAME),
    ]
    assert expected_messages_ids == [message.id for message in check_messages]
