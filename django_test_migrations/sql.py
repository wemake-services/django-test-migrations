from functools import partial
from typing import Callable, Dict, List, Optional

import django
from django.core.management.color import Style, no_style
from django.db import connections, transaction
from typing_extensions import Final

from django_test_migrations.types import AnyConnection

DJANGO_MIGRATIONS_TABLE_NAME: Final = 'django_migrations'


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
        if connection.vendor == 'mysql':
            sql_drop_tables = [
                'SET FOREIGN_KEY_CHECKS = 0;',
                *sql_drop_tables,
                'SET FOREIGN_KEY_CHECKS = 1;',
            ]
        get_execute_sql_flush_for(connection)(sql_drop_tables)


def flush_django_migrations_table(
    database_name: str,
    style: Optional[Style] = None,
) -> None:
    """Flush `django_migrations` table.

    Ensures compability with all supported Django versions.
    `django_migrations` is not "regular" Django model, so its not returned
    by ``ConnectionRouter.get_migratable_models`` which is used e.g. to
    implement sequences reset in ``Django==1.11``.

    """
    style = style or no_style()
    connection = connections[database_name]
    execute_sql_flush = get_execute_sql_flush_for(connection)
    sql_flush = get_sql_flush_with_sequences_for(connection)
    execute_sql_flush(
        sql_flush(
            style,
            [DJANGO_MIGRATIONS_TABLE_NAME],
            allow_cascade=False,
        ),
    )


def get_django_migrations_table_sequences(
    connection: AnyConnection,
) -> List[Dict[str, str]]:
    """`django_migrations` table introspected sequences.

    Returns properly inspected sequences when using ``Django>1.11``
    and static sequence for `id` column otherwise.

    """
    if hasattr(connection.introspection, 'get_sequences'):  # noqa: WPS421
        with connection.cursor() as cursor:
            return connection.introspection.get_sequences(
                cursor,
                DJANGO_MIGRATIONS_TABLE_NAME,
            )
    # for ``Django==1.11`` only primary key sequence is returned
    return [{'table': DJANGO_MIGRATIONS_TABLE_NAME, 'column': 'id'}]


def get_sql_flush_with_sequences_for(
    connection: AnyConnection,
):
    """Harmonizes ``sql_flush`` across Django versions."""
    if django.VERSION >= (3, 1):
        return partial(connection.ops.sql_flush, reset_sequences=True)
    return partial(
        connection.ops.sql_flush,
        sequences=get_django_migrations_table_sequences(connection),
    )


def get_execute_sql_flush_for(
    connection: AnyConnection,
) -> Callable[[List[str]], None]:
    """Return ``execute_sql_flush`` callable for given connection.

    This function also harmonizes the signature of ``execute_sql_flush``
    to match Django 3.1 with ``sql_list`` as the only argument.

    """
    if django.VERSION >= (3, 1):
        return connection.ops.execute_sql_flush
    if django.VERSION >= (2, 0):
        return partial(connection.ops.execute_sql_flush, connection.alias)
    return partial(execute_sql_flush, connection)


def execute_sql_flush(
    connection: AnyConnection,
    sql_list: List[str],
) -> None:  # pragma: no cover
    """Execute a list of SQL statements to flush the database.

    This function is copy of ``connection.ops.execute_sql_flush``
    method from Django's source code: https://bit.ly/3doGMye
    to make `django-test-migrations` compatible with ``Django==1.11``.
    ``connection.ops.execute_sql_flush()`` was introduced in ``Django==2.0``.

    """
    with transaction.atomic(
        using=str(connection.alias),
        savepoint=connection.features.can_rollback_ddl,
    ):
        with connection.cursor() as cursor:
            for sql in sql_list:
                cursor.execute(sql)
