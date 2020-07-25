import pytest

from django_test_migrations.db.backends import mysql, postgresql, registry
from django_test_migrations.db.backends.base.configuration import (
    BaseDatabaseConfiguration,
)
from django_test_migrations.db.backends.exceptions import (
    DatabaseConfigurationNotFound,
)


def test_all_db_backends_registered():
    """Ensures all database backends all registered."""
    registered_vendors = list(registry.database_configuration_registry.keys())
    assert sorted(registered_vendors) == ['mysql', 'postgresql']


def test_abc_subclasses_are_not_registered():
    """Test registration of ``BaseDatabaseConfiguration`` abstract subclasses.

    Ensures ``BaseDatabaseConfiguration`` abstract subclasses are not
    registered.
    """
    vendor = 'abstract_subclass'
    # creates abstract subclasss
    type('DatabaseConfiguration', (BaseDatabaseConfiguration,), {
        'vendor': vendor,
    })
    assert vendor not in registry.database_configuration_registry


@pytest.mark.parametrize(('vendor', 'database_configuration_class'), [
    ('postgresql', postgresql.configuration.DatabaseConfiguration),
    ('mysql', mysql.configuration.DatabaseConfiguration),
])
def test_get_database_configuration_vendor_registered(
    mocker,
    vendor,
    database_configuration_class,
):
    """Ensures database configuration is returned when vendor registered."""
    connection_mock = mocker.Mock()
    connection_mock.vendor = vendor
    database_configuration = registry.get_database_configuration(
        connection_mock,
    )
    assert isinstance(database_configuration, database_configuration_class)


def test_get_database_configuration_vendor_not_registered(mocker):
    """Ensures proper exception is raised when vendor not registered."""
    vendor = 'not_registered_vendor'
    connection_mock = mocker.Mock()
    connection_mock.vendor = vendor
    with pytest.raises(DatabaseConfigurationNotFound, match=vendor):
        registry.get_database_configuration(connection_mock)
