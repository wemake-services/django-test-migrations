from contextlib import contextmanager
from functools import partial

import django
from django.core.management.color import Style

from django_test_migrations import sql


@contextmanager
def simulate_django_version(version):
    """Context manager that changes the django VERSION to test compatibility."""
    current_django_version = django.VERSION
    django.VERSION = version
    yield version
    django.VERSION = current_django_version


def test_flush_django_migrations_table(mocker):
    """Ensure ``connection.ops`` methods are called with expected args."""
    style = Style()
    testing_connection_mock = mocker.MagicMock()
    testing_connection_mock.introspection.get_sequences.return_value = []
    connections_mock = mocker.patch('django.db.connections._connections')
    connections_mock.test = testing_connection_mock
    sql.flush_django_migrations_table('test', style)
    if django.VERSION >= (3, 1):
        testing_connection_mock.ops.sql_flush.assert_called_once_with(
            style,
            [sql.DJANGO_MIGRATIONS_TABLE_NAME],
            reset_sequences=True,
            allow_cascade=False,
        )
        testing_connection_mock.ops.execute_sql_flush.assert_called_once_with(
            mocker.ANY,
        )
    elif django.VERSION >= (2, 0):
        testing_connection_mock.ops.sql_flush.assert_called_once_with(
            style,
            [sql.DJANGO_MIGRATIONS_TABLE_NAME],
            sequences=[],
            allow_cascade=False,
        )
        testing_connection_mock.ops.execute_sql_flush.assert_called_once_with(
            mocker.ANY,
            mocker.ANY,
        )
    else:
        testing_connection_mock.ops.sql_flush.assert_called_once_with(
            style,
            [sql.DJANGO_MIGRATIONS_TABLE_NAME],
            sequences=[],
            allow_cascade=False,
        )


class TestGetSqlFlushWithSequences(object):
    """Ensure we call `sql_flush` rightly accross Django versions."""

    def test_for_django31(self, mocker):
        """Ensure we are calling sql_flush with `reset_sequences`."""
        connection_mock = mocker.Mock()
        connection_mock.ops.sql_flush = _fake_sql_flush
        with simulate_django_version((3, 1, 'final', 0)):
            sql_flush = sql.get_sql_flush_with_sequences_for(connection_mock)
        assert sql_flush.func == _fake_sql_flush
        assert sql_flush.keywords == {'reset_sequences': True}

    def test_for_django22(self, mocker):
        """Ensure we are calling sql_flush with the positionnal `sequences`."""
        connection_mock = mocker.MagicMock()
        connection_mock.ops.sql_flush.return_value = _fake_sql_flush
        connection_mock.introspection.get_sequences.return_value = []
        with simulate_django_version((2, 0, 'final', 0)):
            sql_flush = sql.get_sql_flush_with_sequences_for(connection_mock)
        assert sql_flush.func == connection_mock.ops.sql_flush
        assert sql_flush.keywords == {'sequences': []}


class TestGetExecuteSqlFlush(object):
    """Ensure we call `execute_sql_flush` rightly accross Django versions."""

    def test_for_django31(self, mocker):
        """Ensure we are getting execute_sql_flush directly."""
        connection_mock = mocker.Mock()
        connection_mock.ops.execute_sql_flush = _fake_execute_sql_flush
        with simulate_django_version((3, 1, 'final', 0)):
            execute_sql_flush = sql.get_execute_sql_flush_for(connection_mock)
        assert execute_sql_flush == _fake_execute_sql_flush

    def test_for_django20(self, mocker):
        """Ensure we call execute_sql_flush with the database name."""
        connection_mock = mocker.Mock()
        connection_mock.alias = 'test'
        connection_mock.ops.execute_sql_flush = _fake_execute_sql_flush
        with simulate_django_version((2, 0, 'final', 0)):
            execute_sql_flush = sql.get_execute_sql_flush_for(connection_mock)
        assert execute_sql_flush.func == _fake_execute_sql_flush
        assert execute_sql_flush.args[0] == 'test'

    def test_for_django1_11(self, mocker):
        """Ensure custom function is returned."""
        connection_mock = mocker.Mock()

        with simulate_django_version((1, 11, 'final', 0)):
            execute_sql_flush = sql.get_execute_sql_flush_for(connection_mock)
        assert isinstance(execute_sql_flush, partial)
        assert execute_sql_flush.func == sql.execute_sql_flush
        assert execute_sql_flush.args[0] == connection_mock


def _fake_execute_sql_flush(sql_list):
    return None


def _fake_sql_flush():
    return None
