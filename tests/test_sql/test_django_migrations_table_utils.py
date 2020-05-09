from django_test_migrations import sql


def test_get_django_migrations_table_sequences0(mocker):
    """Ensure valid sequences are returned when using `Django>1.11`."""
    connection_mock = mocker.MagicMock()
    sql.get_django_migrations_table_sequences(connection_mock)
    connection_mock.introspection.get_sequences.assert_called_once_with(
        connection_mock.cursor().__enter__.return_value,  # noqa: WPS609
        sql.DJANGO_MIGRATIONS_TABLE_NAME,
    )


def test_get_django_migrations_table_sequences1(mocker):
    """Ensure valid sequences are returned when using `Django==1.11`."""
    connection_mock = mocker.Mock()
    del connection_mock.introspection.get_sequences  # noqa: WPS420
    assert (
        sql.get_django_migrations_table_sequences(connection_mock) ==
        [{'table': sql.DJANGO_MIGRATIONS_TABLE_NAME, 'column': 'id'}]
    )
