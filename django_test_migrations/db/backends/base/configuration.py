import abc
import inspect
from typing import ClassVar

from django_test_migrations.db.backends.exceptions import (
    DatabaseConfigurationSettingNotFound,
)
from django_test_migrations.db.backends.registry import (
    database_configuration_registry,
)
from django_test_migrations.types import AnyConnection, DatabaseSettingValue


class BaseDatabaseConfiguration(abc.ABC):
    """Interact with database's settings."""

    vendor: ClassVar[str]
    statement_timeout: ClassVar[str]

    def __init__(self, connection: AnyConnection) -> None:
        """Bind database ``connection`` used to retrieve settings values."""
        self.connection = connection

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        """Register ``BaseDatabaseConfiguration`` subclass of db ``vendor``."""
        if not inspect.isabstract(cls):
            database_configuration_registry.setdefault(cls.vendor, cls)

    @abc.abstractmethod
    def get_setting_value(self, name: str) -> DatabaseSettingValue:
        """Retrieve value of ``vendor`` database's ``name`` setting.

        Raises:
            DatabaseConfigurationSettingNotFound

        """
        raise DatabaseConfigurationSettingNotFound(self.vendor, name)
