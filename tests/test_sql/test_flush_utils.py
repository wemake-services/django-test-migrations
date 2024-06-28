import pytest
from django.core.management.color import Style

from django_test_migrations import sql


@pytest.fixture
def testing_connection_mock(mocker):
    """Mock Django connections to check the methods called."""
    testing_connection_mock = mocker.MagicMock()
    testing_connection_mock.introspection.get_sequences.return_value = []
    connections_mock = mocker.patch('django.db.connections._connections')
    connections_mock.test = testing_connection_mock
    return testing_connection_mock


def test_flush_django_migration_table(mocker, testing_connection_mock):
    """Ensure expected ``connection`` methods are called."""
    style = Style()

    sql.flush_django_migrations_table('test', style)

    testing_connection_mock.ops.sql_flush.assert_called_once_with(
        style,
        [sql.DJANGO_MIGRATIONS_TABLE_NAME],
        reset_sequences=True,
        allow_cascade=False,
    )
    testing_connection_mock.ops.execute_sql_flush.assert_called_once_with(
        mocker.ANY,
    )
