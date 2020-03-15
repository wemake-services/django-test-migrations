# -*- coding: utf-8 -*-

from functools import partial

from django_test_migrations import sql

TESTING_DATABASE_NAME = 'test'


def test_drop_models_table_no_tables_detected(mocker):
    """Ensure any `DROP TABLE` statement executed when no tables detected."""
    testing_connection_mock = mocker.MagicMock()
    testing_connection_mock.introspection.django_table_names.return_value = []
    connections_mock = mocker.patch('django.db.connections._connections')
    connections_mock.test = testing_connection_mock
    sql.drop_models_tables(TESTING_DATABASE_NAME)
    testing_connection_mock.ops.execute_sql_flush.assert_not_called()


def test_drop_models_table_table_detected(mocker):
    """Ensure `DROP TABLE` statements are executed when any table detected."""
    testing_connection_mock = mocker.MagicMock()
    testing_connection_mock.introspection.django_table_names.return_value = [
        'foo_bar',
        'foo_baz',
    ]
    connections_mock = mocker.patch('django.db.connections._connections')
    connections_mock.test = testing_connection_mock
    sql.drop_models_tables(TESTING_DATABASE_NAME)
    testing_connection_mock.ops.execute_sql_flush.assert_called_once()


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
