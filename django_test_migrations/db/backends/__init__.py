# register all ``BaseDatabaseConfiguration`` subclasses
from django_test_migrations.db.backends.mysql.configuration import (
    DatabaseConfiguration as MySQLDatabaseConfiguration,
)
from django_test_migrations.db.backends.postgresql.configuration import (
    DatabaseConfiguration as PostgreSQLDatabaseConfiguration,
)
