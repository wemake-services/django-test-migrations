import pytest

from django_test_migrations.db.backends import postgresql
from django_test_migrations.db.backends.exceptions import (
    DatabaseConfigurationSettingNotFound,
)


def test_get_setting_value(mocker):
    """Ensure expected SQL query is executed."""
    setting_name = 'statement_timeout'
    connection_mock = mocker.MagicMock()
    connection_mock.ops.quote_name = lambda name: name
    database_configuration = (
        postgresql.configuration.PostgreSQLDatabaseConfiguration(
            connection_mock,
        )
    )
    database_configuration.get_setting_value(setting_name)
    cursor_mock = connection_mock.cursor().__enter__()  # noqa: PLC2801
    cursor_mock.execute.assert_called_once_with(
        'SELECT setting FROM pg_settings WHERE name = %s;',
        (setting_name,),
    )


def test_get_existing_setting_value(mocker):
    """Ensure setting value is returned for existing setting."""
    expected_setting_value = 74747
    connection_mock = mocker.MagicMock()
    cursor_mock = connection_mock.cursor().__enter__()  # noqa: PLC2801
    cursor_mock.fetchone.return_value = (expected_setting_value,)
    database_configuration = (
        postgresql.configuration.PostgreSQLDatabaseConfiguration(
            connection_mock,
        )
    )
    setting_value = database_configuration.get_setting_value('testing_setting')
    assert setting_value == expected_setting_value


def test_get_not_existing_setting_value(mocker):
    """Ensure exception is raised when setting does not exist."""
    connection_mock = mocker.MagicMock()
    cursor_mock = connection_mock.cursor().__enter__()  # noqa: PLC2801
    cursor_mock.fetchone.return_value = None
    database_configuration = (
        postgresql.configuration.PostgreSQLDatabaseConfiguration(
            connection_mock,
        )
    )
    with pytest.raises(DatabaseConfigurationSettingNotFound):
        database_configuration.get_setting_value('testing_setting')
