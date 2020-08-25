from django_test_migrations import sql

TESTING_DATABASE_NAME = 'test'


def test_drop_models_table_no_tables_detected(mocker):
    """Ensure any ``DROP TABLE`` statement executed when no tables detected."""
    testing_connection_mock = mocker.MagicMock()
    testing_connection_mock.introspection.django_table_names.return_value = []
    connections_mock = mocker.patch('django.db.connections._connections')
    connections_mock.test = testing_connection_mock
    sql.drop_models_tables(TESTING_DATABASE_NAME)
    testing_connection_mock.ops.execute_sql_flush.assert_not_called()


def test_drop_models_table_table_detected(mocker):
    """Ensure ``DROP TABLE`` statements are executed when any table detected."""
    testing_connection_mock = mocker.MagicMock()
    testing_connection_mock.introspection.django_table_names.return_value = [
        'foo_bar',
        'foo_baz',
    ]
    connections_mock = mocker.patch('django.db.connections._connections')
    connections_mock.test = testing_connection_mock
    execute_sql_flush_mock = mocker.patch(
        'django_test_migrations.sql.get_execute_sql_flush_for',
    )
    sql.drop_models_tables(TESTING_DATABASE_NAME)
    execute_sql_flush_mock(testing_connection_mock).assert_called_once()
