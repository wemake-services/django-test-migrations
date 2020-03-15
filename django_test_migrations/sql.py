# -*- coding: utf-8 -*-

from functools import partial
from typing import Callable, Dict, List, Optional, Union

from django.core.management.color import Style, no_style
from django.db import DefaultConnectionProxy, connections, transaction
from django.db.backends.base.base import BaseDatabaseWrapper

_Connection = Union[DefaultConnectionProxy, BaseDatabaseWrapper]

DJANGO_MIGRATIONS_TABLE_NAME = 'django_migrations'


def drop_models_tables(
    database_name: str,
    style: Optional[Style] = None,
) -> None:
    """Drop all installed Django's models tables."""
    style = style or no_style()
    connection = connections[database_name]
    tables = connection.introspection.django_table_names(
        only_existing=True,
        include_views=False,
    )
    sql_drop_tables = [
        connection.SchemaEditorClass.sql_delete_table % {
            'table': style.SQL_FIELD(connection.ops.quote_name(table)),
        }
        for table in tables
    ]
    if sql_drop_tables:
        get_execute_sql_flush_for(connection)(database_name, sql_drop_tables)


def flush_django_migrations_table(
    database_name: str,
    style: Optional[Style] = None,
) -> None:
    """Flush `django_migrations` table."""
    style = style or no_style()
    connection = connections[database_name]
    django_migrations_sequences = get_django_migrations_table_sequences(
        connection,
    )
    execute_sql_flush = get_execute_sql_flush_for(connection)
    execute_sql_flush(
        database_name,
        connection.ops.sql_flush(
            style,
            [DJANGO_MIGRATIONS_TABLE_NAME],
            django_migrations_sequences,
            allow_cascade=False,
        ),
    )


def get_django_migrations_table_sequences(
    connection: _Connection,
) -> List[Dict[str, str]]:
    """`django_migrations` table introspected sequences.

    Returns properly inspected sequences when using `Django>1.11`
    and static sequence for `id` column otherwise.

    """
    if hasattr(connection.introspection, 'get_sequences'):  # noqa: WPS421
        with connection.cursor() as cursor:
            return connection.introspection.get_sequences(
                cursor,
                DJANGO_MIGRATIONS_TABLE_NAME,
            )
    # for `Django==1.11` only primary key sequence is returned
    return [{'table': DJANGO_MIGRATIONS_TABLE_NAME, 'column': 'id'}]


def get_execute_sql_flush_for(
    connection: _Connection,
) -> Callable[[str, List[str]], None]:
    """Return ``execute_sql_flush`` callable for given connection."""
    return getattr(
        connection.ops,
        'execute_sql_flush',
        partial(execute_sql_flush, connection),
    )


def execute_sql_flush(
    connection: _Connection,
    using: str,
    sql_list: List[str],
) -> None:  # pragma: no cover
    """Execute a list of SQL statements to flush the database.

    This function is copy of ``connection.ops.execute_sql_flush``
    method from Django's source code:
    https://github.com/django/django/blob/227d0c7365cfd0a64d021cb9bdcf77bed2d3f170/django/db/backends/base/operations.py#L401
    to make `django-test-migrations` compatible with `Django==1.11`.
    ``connection.ops.execute_sql_flush()`` was introduced in `Django==2.0`.

    """
    with transaction.atomic(
        using=using,
        savepoint=connection.features.can_rollback_ddl,
    ):
        with connection.cursor() as cursor:
            for sql in sql_list:
                cursor.execute(sql)
