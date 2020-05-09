from functools import partial

from django.core.management.color import Style

from django_test_migrations import sql


def test_flush_django_migrations_table(mocker):
    """Ensure ``connection.ops`` methods are called with expected args."""
    style = Style()
    testing_connection_mock = mocker.MagicMock()
    testing_connection_mock.introspection.get_sequences.return_value = []
    connections_mock = mocker.patch('django.db.connections._connections')
    connections_mock.test = testing_connection_mock
    sql.flush_django_migrations_table('test', style)
    testing_connection_mock.ops.sql_flush.assert_called_once_with(
        style,
        [sql.DJANGO_MIGRATIONS_TABLE_NAME],
        [],
        allow_cascade=False,
    )
    testing_connection_mock.ops.execute_sql_flush.assert_called_once_with(
        'test',
        mocker.ANY,
    )


def test_get_execute_sql_flush_for_method_present(mocker):
    """Ensure connections.ops method returned when it is already present."""
    connection_mock = mocker.Mock()
    connection_mock.ops.execute_sql_flush = _fake_execute_sql_flush
    execute_sql_flush = sql.get_execute_sql_flush_for(connection_mock)
    assert execute_sql_flush == _fake_execute_sql_flush


def test_get_execute_sql_flush_for_method_missing(mocker):
    """Ensure custom function is returned when connection.ops miss methods."""
    connection_mock = mocker.Mock()
    del connection_mock.ops.execute_sql_flush  # noqa: WPS420
    execute_sql_flush = sql.get_execute_sql_flush_for(connection_mock)
    assert isinstance(execute_sql_flush, partial)
    assert execute_sql_flush.func == sql.execute_sql_flush
    assert execute_sql_flush.args[0] == connection_mock


def _fake_execute_sql_flush(using, sql_list):
    return None
