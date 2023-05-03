import pytest
from pytest_mock import MockerFixture

from django_test_migrations.db.backends import mysql
from django_test_migrations.db.backends.exceptions import (
    DatabaseConfigurationSettingNotFound,
)


@pytest.mark.parametrize(('version', 'setting_name'), [
    ('8.0.33', 'MAX_EXECUTION_TIME'),
    ('10.11.2-MariaDB', 'MAX_STATEMENT_TIME'),
    ('10.11.2-MariaDB-1:10.11.2+maria~ubu2204', 'MAX_STATEMENT_TIME'),
])
def test_statement_timeout(
    mocker: MockerFixture,
    version: str,
    setting_name: str,
) -> None:
    """Ensure expected setting name is returned."""
    connection_mock = mocker.MagicMock()
    cursor_mock = connection_mock.cursor().__enter__()  # noqa: WPS609
    cursor_mock.fetchone.return_value = (version,)
    database_configuration = mysql.configuration.DatabaseConfiguration(
        connection_mock,
    )

    assert database_configuration.statement_timeout == setting_name


def test_get_setting_value(mocker: MockerFixture) -> None:
    """Ensure expected SQL query is executed."""
    setting_name = 'MAX_EXECUTION_TIME'
    connection_mock = mocker.MagicMock()
    connection_mock.ops.quote_name = lambda name: name
    database_configuration = mysql.configuration.DatabaseConfiguration(
        connection_mock,
    )

    database_configuration.get_setting_value(setting_name)

    cursor_mock = connection_mock.cursor().__enter__()  # noqa: WPS609
    cursor_mock.execute.assert_called_once_with(
        'SELECT @@{0};'.format(setting_name),
    )


def test_get_existing_setting_value(mocker: MockerFixture) -> None:
    """Ensure setting value is returned for existing setting."""
    expected_setting_value = 74747
    connection_mock = mocker.MagicMock()
    cursor_mock = connection_mock.cursor().__enter__()  # noqa: WPS609
    cursor_mock.fetchone.return_value = (expected_setting_value,)
    database_configuration = mysql.configuration.DatabaseConfiguration(
        connection_mock,
    )

    setting_value = database_configuration.get_setting_value('testing_setting')

    assert setting_value == expected_setting_value


def test_get_not_existing_setting_value(mocker: MockerFixture) -> None:
    """Ensure exception is raised when setting does not exist."""
    connection_mock = mocker.MagicMock()
    cursor_mock = connection_mock.cursor().__enter__()  # noqa: WPS609
    cursor_mock.fetchone.return_value = None
    database_configuration = mysql.configuration.DatabaseConfiguration(
        connection_mock,
    )

    with pytest.raises(DatabaseConfigurationSettingNotFound):
        database_configuration.get_setting_value('testing_setting')
