from typing_extensions import final

from django_test_migrations.db.backends.base.configuration import (
    BaseDatabaseConfiguration,
)
from django_test_migrations.types import DatabaseSettingValue


@final
class DatabaseConfiguration(BaseDatabaseConfiguration):
    """Interact with MySQL database configuration."""

    vendor = 'mysql'
    statement_timeout = 'MAX_EXECUTION_TIME'

    def get_setting_value(self, name: str) -> DatabaseSettingValue:
        """Retrieve value of MySQL database's setting with ``name``."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                'SELECT @@{0};'.format(self.connection.ops.quote_name(name)),
            )
            setting_value = cursor.fetchone()
            if not setting_value:
                return super().get_setting_value(name)
            return setting_value[0]
